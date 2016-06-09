# -*- coding: utf-8 -*-
"""
    Database ORM definition
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import importlib

import enum

from sqlalchemy import create_engine
from sqlalchemy import (Boolean, Column, Enum, ForeignKey, Integer, String,
                        Table, Text, PickleType)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker, joinedload,
                            relationship, object_session)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import has_identity
from sqlalchemy.schema import UniqueConstraint

from bb8 import config
from bb8.backend.metadata import SessionRecord


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
try:
    # Use flask's global object if available
    from flask import g  # pylint: disable=C0411,C0413
    g.db = None
except Exception:
    g = G()


class DatabaseManager(object):
    """
    Database Manager class
    """
    engine = None

    @classmethod
    def connect(cls, engine=None):
        """Return a SQLAlchemy engine connection."""
        try:
            _ = g.db
        except RuntimeError:
            pass
        else:
            return

        if engine:
            cls.engine = engine
            DeclarativeBase.metadata.bind = engine
        elif not cls.engine:
            cls.create_engine()

        ScopedSession = scoped_session(sessionmaker(bind=cls.engine))
        g.db = ScopedSession()

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

    @classmethod
    def rollback(cls):
        g.db.rollback()


class DatabaseSession(object):
    def __init__(self, disconnect=True):
        self._disconnect = disconnect

    def __enter__(self):
        DatabaseManager.connect()

    def __exit__(self, exc_type, exc_value, tb):
        DatabaseManager.commit()
        if self._disconnect:
            DatabaseManager.disconnect()


class QueryHelperMixin(object):
    db_manager = DatabaseManager()

    def __repr__(self):
        return '<%s(\'%s\')>' % (type(self).__name__, self.id)

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
                return query_object.limit(1).one()
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


class PlatformTypeEnum(enum.Enum):
    Facebook = 'FACEBOOK'
    Line = 'LINE'


class Bot(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'bot'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=False)
    interaction_timeout = Column(Integer, nullable=False)
    session_timeout = Column(Integer, nullable=False)
    root_node_id = Column(Integer, nullable=True)
    start_node_id = Column(Integer, nullable=True)

    orphan_nodes = relationship('Node', secondary='bot_node')
    platforms = relationship('Platform')

    @property
    def root_node(self):
        return Node.get_by(id=self.root_node_id, single=True)


class User(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    platform_id = Column(ForeignKey('platform.id'), nullable=False)
    platform_user_ident = Column(String(512), nullable=False)
    last_seen = Column(Integer, nullable=False)
    login_token = Column(String(512), nullable=True)
    session = Column(SessionRecord.as_mutable(PickleType), nullable=True)

    platform = relationship('Platform')
    colleted_data = relationship('ColletedDatum')

    def goto(self, node_id):
        """Goto a node."""
        self.session = SessionRecord(node_id)


class Node(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    expect_input = Column(Boolean, nullable=False)
    content_module_id = Column(ForeignKey('content_module.id'), nullable=False)
    content_config = Column(PickleType, nullable=False)
    parser_module_id = Column(ForeignKey('parser_module.id'), nullable=True)
    parser_config = Column(PickleType, nullable=True)

    bot = relationship('Bot')
    content_module = relationship('ContentModule')
    parser_module = relationship('ParserModule')

    def build_linkages(self, links):
        """Build linkage according to links.

        Args:
            links: is a list of bb8.backend.module_api.LinkageItem
        """

        for link in links:
            end_node_id = link.end_node_id if link.end_node_id else self.id
            Linkage(start_node_id=self.id,
                    end_node_id=end_node_id,
                    action_ident=link.action_ident,
                    ack_message=link.ack_message).add()
        self.commit()


class Platform(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'platform'
    __table_args__ = (UniqueConstraint('provider_ident'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(Enum(PlatformTypeEnum), nullable=False)
    provider_ident = Column(String(512), nullable=False)
    config = Column(PickleType, nullable=False)

    bot = relationship('Bot')


class Linkage(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'linkage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_node_id = Column(ForeignKey('node.id'), nullable=False)
    end_node_id = Column(ForeignKey('node.id'), nullable=False)
    action_ident = Column(String(256), nullable=False)
    ack_message = Column(Text, nullable=False)

    start_node = relationship('Node', foreign_keys=[start_node_id],
                              backref='linkages')
    end_node = relationship('Node', foreign_keys=[end_node_id])


class ContentModule(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'content_module'

    id = Column(String(128), primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    module_name = Column(String(256), nullable=False)
    ui_module_name = Column(String(256), nullable=False)

    CONTENT_MODULES = 'bb8.backend.content_modules'

    def get_module(self):
        return importlib.import_module(
            '%s.%s' % (self.CONTENT_MODULES, self.module_name))


class ParserModule(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'parser_module'

    id = Column(String(128), primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    module_name = Column(String(256), nullable=False)
    ui_module_name = Column(String(256), nullable=False)
    variables = Column(PickleType, nullable=False)

    PARSER_MODULES = 'bb8.backend.parser_modules'

    def get_module(self, name=None):
        if name is None:
            name = self.module_name
        return importlib.import_module(
            '%s.%s' % (self.PARSER_MODULES, name))


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
    sender_enum = Column(Enum(SenderEnum), nullable=False)
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
