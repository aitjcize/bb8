# -*- coding: utf-8 -*-
"""
    Database ORM definition
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import enum

from sqlalchemy import create_engine
from sqlalchemy import (Column, ForeignKey, Integer, String, Table, Text,
                        PickleType)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker, joinedload,
                            relationship, object_session)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import has_identity

# TODO(aitjcize): remove this when SQLA release verson 1.1
from sqlalchemy_enum34 import EnumType

from bb8 import config


DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata


class G(object):
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            raise RuntimeError('database is not connected')
        return self._db

    @db.setter
    def db(self, value):
        self._db = value


# Global object for managing session
g = G()


class DatabaseManager(object):
    """
    Database Manager class
    """
    engine = None

    @classmethod
    def connect(cls, engine=None):
        """Return a SQLAlchemy engine connection."""
        if engine:
            cls.engine = engine
            DeclarativeBase.metadata.bind = engine
        elif not cls.engine:
            cls.create_engine()

        Session = scoped_session(sessionmaker(bind=cls.engine))
        g.db = Session()

    @classmethod
    def disconnect(cls, commit=True):
        if commit:
            try:
                g.db.commit()
            except Exception:
                pass
        g.db.close()
        g.db = None

    @classmethod
    def reconnect(cls, commit=True):
        cls.disconnect(commit)
        cls.connect()

    @classmethod
    def is_connected(cls):
        try:
            return g.db is not None
        except Exception:
            return False

    @classmethod
    def create_engine(cls):
        cls.engine = create_engine(config.DATABASE, echo=False,
                                   encoding='utf-8', pool_recycle=3600)

    @classmethod
    def create_all_tables(cls):
        """Create all table."""
        DeclarativeBase.metadata.create_all(cls.engine)

    @classmethod
    def drop_all_tables(cls):
        """Drop all table."""
        DeclarativeBase.metadata.drop_all(cls.engine)

    @classmethod
    def create_new_table(cls, k):
        DeclarativeBase.metadata.tables[k.__tablename__].create(cls.engine)

    @classmethod
    def drop_table(cls, k):
        DeclarativeBase.metadata.tables[k.__tablename__].drop(cls.engine)

    @classmethod
    def reset(cls):
        """Reset and initialize database."""
        DeclarativeBase.metadata.drop_all(cls.engine)
        DeclarativeBase.metadata.create_all(cls.engine)

    @classmethod
    def commit(cls):
        g.db.commit()

    @classmethod
    def flush(cls):
        g.db.flush()


class QueryHelperMixin(object):
    db_manager = DatabaseManager()

    @classmethod
    def commit(cls):
        cls.db_manager.commit()

    @classmethod
    def flush(cls):
        cls.db_manager.flush()

    @classmethod
    def query(cls, *expr):
        """Short hand for query."""
        return g.db.query(*expr)

    @classmethod
    def get_all(cls, cache=None):
        """Get all record from a table."""
        query_object = cls.query(cls)
        if cache:
            query_object = query_object.options(cache)
        return query_object.all()

    @classmethod
    def get_by(cls, eager=None, order_by=None, offset=0, limit=0,
               single=False, cache=None, lock=False, **kwargs):
        """Get item by kwargs."""
        query_object = cls.query(cls)
        if eager:
            joinloads = [joinedload(x) for x in eager]
            query_object = query_object.options(*joinloads)

        if cache and not lock:
            query_object = query_object.options(cache)

        query_object = query_object.filter_by(**kwargs)

        if order_by:
            query_object = query_object.order_by(*order_by)

        if offset:
            query_object = query_object.offset(offset)

        if limit:
            query_object = query_object.limit(limit)

        if lock:
            query_object = query_object.with_lockmode('update')

            if cache:
                query_object.options(cache).invalidate()

        if single:
            try:
                return query_object.one()
            except NoResultFound:
                return None
        return query_object.all()

    @classmethod
    def delete_by(cls, **kwargs):
        """Delete image by kwargs."""
        return cls.query(cls).filter_by(**kwargs).delete()

    @classmethod
    def delete_all(cls):
        """Delete all records from a table."""
        return cls.query(cls).delete()

    @classmethod
    def select(cls, *args):
        cls.query_object = cls.query(*args)
        return cls

    @classmethod
    def exists(cls, **kwargs):
        return cls.get_by(**kwargs)

    @classmethod
    def count(cls):
        """Get images count."""
        return cls.query(cls).count()

    @classmethod
    def count_by(cls, **kwargs):
        """Get images count by condition."""
        return cls.query(cls).filter_by(**kwargs).count()

    def add(self):
        """Register object."""
        g.db.add(self)
        return self

    def delete(self):
        """Unregister object."""
        self.query(type(self)).filter_by(id=self.id).delete()
        return self

    def refresh(self):
        """Refresh object and reconnect it with session."""
        #: Detached
        if object_session(self) is None and has_identity(self):
            g.db.add(self)
        g.db.refresh(self)
        return self

    def rexpunge(self):
        """Refresh then detach from session."""
        g.db.refresh(self)
        g.db.expunge(self)
        return self

    def expunge(self):
        """Detach from session."""
        g.db.expunge(self)
        return self

    def merge(self):
        """Merge a object with current session"""
        g.db.merge(self)
        return self


class Account(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    passwd = Column(String(256), nullable=False)

    bots = relationship('Bot', secondary='account_bot')
    users = relationship('User')


class PlatformTypeEnum(enum.Enum):
    Facebook = 'FACEBOOK'
    Line = 'LINE'


class User(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    platform_type_enum = Column(EnumType(PlatformTypeEnum), nullable=False)
    platform_user_id = Column(String(512), nullable=False)
    session_stack = Column(PickleType, nullable=False)

    colleted_data = relationship('ColletedDatum')


class Bot(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'bot'

    id = Column(Integer, primary_key=True, autoincrement=True)
    interaction_timeout = Column(Integer, nullable=False)
    session_timeout = Column(Integer, nullable=False)
    root_node_id = Column(Integer, nullable=True)
    start_node_id = Column(Integer, nullable=True)

    messages = relationship('Message')
    orphan_nodes = relationship('Node', secondary='bot_node')
    platforms = relationship('Platform')


class Node(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    content_module_id = Column(ForeignKey('content_module.id'), nullable=False)
    content_config = Column(PickleType, nullable=False)
    parser_module_id = Column(ForeignKey('parser_module.id'), nullable=False)
    parser_config = Column(PickleType, nullable=False)

    bot = relationship('Bot')
    content_module = relationship('ContentModule')
    parser_module = relationship('ParserModule')


class Platform(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'platform'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(EnumType(PlatformTypeEnum), nullable=False)
    provider_ident = Column(String(512), nullable=False)
    configuration = Column(PickleType, nullable=False)


class Action(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'action'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=False)


class Linkage(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'linkage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_node_id = Column(ForeignKey('node.id'), nullable=False)
    end_node_id = Column(ForeignKey('node.id'), nullable=False)
    action_id = Column(ForeignKey('action.id'), nullable=False)
    ack_message = Column(Text, nullable=False)

    start_node = relationship('Node', foreign_keys=[start_node_id],
                              backref='linkages')
    end_node = relationship('Node', foreign_keys=[end_node_id])
    action = relationship('Action')


class ContentModule(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'content_module'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    content_filename = Column(String(256), nullable=False)
    ui_filename = Column(String(256), nullable=False)
    input_parameter = Column(PickleType, nullable=False)


class ParserModule(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'parser_module'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    content_filename = Column(String(256), nullable=False)
    ui_filename = Column(String(256), nullable=False)
    variables = Column(PickleType, nullable=False)

    actions = relationship('Action', secondary='parser_module_action')


class MessageTypeEnum(enum.Enum):
    Text = 'TEXT'
    Card = 'CARD'


class Message(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(EnumType(MessageTypeEnum), nullable=False)
    content = Column(PickleType, nullable=False)


class ColletedDatum(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'colleted_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    key = Column(String(512), nullable=False)
    value = Column(PickleType, nullable=False)


class SenderEnum(enum.Enum):
    Bot = 'BOT'
    Human = 'HUMAN'


class Conversation(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'conversation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    sender_enum = Column(EnumType(SenderEnum), nullable=False)
    msg = Column(PickleType, nullable=False)

    user = relationship('User')


class Event(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    event_name = Column(String(512), nullable=False)
    event_value = Column(PickleType, nullable=False)


t_account_bot = Table(
    'account_bot', metadata,
    Column('account_id', ForeignKey('account.id'), nullable=False),
    Column('bot_id', ForeignKey('bot.id'), nullable=False)
)


t_bot_node = Table(
    'bot_node', metadata,
    Column('bot_id', ForeignKey('bot.id'), nullable=False),
    Column('node_id', ForeignKey('node.id'), nullable=False)
)


t_parser_module_action = Table(
    'parser_module_action', metadata,
    Column('parser_module_id', ForeignKey('parser_module.id'), nullable=False),
    Column('action_id', ForeignKey('action.id'), nullable=False)
)
