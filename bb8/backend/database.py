# -*- coding: utf-8 -*-
"""
    Database ORM definition
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import time
import uuid
import importlib
from datetime import datetime, timedelta

import jwt
import enum
import pytz
from passlib.hash import bcrypt  # pylint: disable=E0611

from sqlalchemy import create_engine
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        PickleType, Table, Text, String, Unicode, UnicodeText)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker, joinedload,
                            relationship, object_session, deferred)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import has_identity
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.exc import IntegrityError

from bb8 import config
from bb8.backend.metadata import SessionRecord
from bb8.error import AppError
from bb8.constant import HTTPStatus, CustomError


DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata


try:
    """
    The pooled connection can not share accross process. We need to create a
    new engine after fork.

    See: http://docs.sqlalchemy.org/en/latest/core/pooling.html#
        using-connection-pools-with-multiprocessing
    """
    import uwsgi  # pylint: disable=E0401,C0413

    def create_new_connection():
        DatabaseManager.create_engine()

    uwsgi.post_fork_hook = create_new_connection
except Exception:
    pass


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
            g.db.commit()
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
        if exc_type == IntegrityError:
            DatabaseManager.rollback()
            return

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


class JSONSerializer(object):
    __json_public__ = None
    __json_hidden__ = None

    def unix_timestamp(self, dt):
        """ Return the time in seconds since the epoch as an integer """

        _EPOCH = datetime(1970, 1, 1, tzinfo=pytz.utc)
        if dt.tzinfo is None:
            return int(time.mktime((dt.year, dt.month, dt.day,
                                    dt.hour, dt.minute, dt.second,
                                    -1, -1, -1)) + dt.microsecond / 1e6)
        else:
            return int((dt - _EPOCH).total_seconds())

    def get_field_names(self):
        for p in self.__mapper__.iterate_properties:
            yield p.key

    def to_json(self):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []

        rv = dict()
        for key in public:
            rv[key] = getattr(self, key)
            if isinstance(rv[key], datetime):
                rv[key] = self.unix_timestamp(rv[key])
            elif isinstance(rv[key], enum.Enum):
                rv[key] = rv[key].value
        for key in hidden:
            rv.pop(key, None)
        return rv


class Account(DeclarativeBase, QueryHelperMixin, JSONSerializer):
    __tablename__ = 'account'

    __json_public__ = ['name', 'username', 'email']

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False, default=u'')
    username = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    passwd = Column(String(256), nullable=False)

    bots = relationship('Bot', secondary='account_bot')

    feeds = relationship('Feed', lazy='dynamic')
    entries = relationship('Entry')
    oauth_infos = relationship('OAuthInfo', back_populates="account")

    def set_passwd(self, passwd):
        self.passwd = bcrypt.encrypt(passwd)
        return self

    def verify_passwd(self, passwd):
        return bcrypt.verify(passwd, self.passwd)

    @property
    def auth_token(self, expiration=30):
        payload = {
            'iss': 'compose.ai',
            'sub': self.id,
            'jti': str(uuid.uuid4()),  # unique identifier of the token
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=expiration)
        }
        token = jwt.encode(payload, config.JWT_SECRET)
        return token.decode('unicode_escape')

    @classmethod
    def from_auth_token(cls, token):
        try:
            payload = jwt.decode(token, config.JWT_SECRET)
        except (jwt.DecodeError, jwt.ExpiredSignature):
            raise AppError(HTTPStatus.STATUS_CLIENT_ERROR,
                           CustomError.ERR_UNAUTHENTICATED,
                           'The token %s is invalid' % token)
        return cls.get_by(id=payload['sub'], single=True)


class OAuthProviderEnum(enum.Enum):
    Facebook = 'Facebook'
    Google = 'Google'
    Github = 'Github'


class OAuthInfo(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'oauth_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)

    provider = Column(Enum(OAuthProviderEnum), nullable=False)
    provider_ident = Column(String(256), nullable=False)

    account = relationship('Account', back_populates="oauth_infos")


class PlatformTypeEnum(enum.Enum):
    Facebook = 'Facebook'
    Line = 'Line'


class Bot(DeclarativeBase, QueryHelperMixin, JSONSerializer):
    __tablename__ = 'bot'

    __json_public__ = ['id', 'name', 'description',
                       'root_node_id', 'start_node_id',
                       'platforms']

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False)
    description = Column(UnicodeText, nullable=False)
    interaction_timeout = Column(Integer, nullable=False, default=120)
    session_timeout = Column(Integer, nullable=False, default=86400)
    root_node_id = Column(Integer, nullable=True)
    start_node_id = Column(Integer, nullable=True)

    nodes = relationship('Node')
    linkages = relationship('Linkage')
    platforms = relationship('Platform')

    orphan_nodes = relationship('Node', secondary='bot_node')

    @property
    def root_node(self):
        return Node.get_by(id=self.root_node_id, single=True)

    def delete(self):
        self.delete_all_node_and_links()
        super(Bot, self).delete()

    def delete_all_node_and_links(self):
        """Delete all associated node and links of this bot."""
        Linkage.delete_by(bot_id=self.id)
        Node.delete_by(bot_id=self.id)
        Platform.delete_by(bot_id=self.id)


class User(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    platform_id = Column(ForeignKey('platform.id'), nullable=False)
    platform_user_ident = Column(String(128), nullable=False)
    last_seen = Column(DateTime, nullable=False)
    login_token = deferred(Column(Text, nullable=True))
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
    name = Column(Unicode(128), nullable=False)
    description = Column(UnicodeText, nullable=True)
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
            Linkage(bot_id=self.bot_id,
                    start_node_id=self.id,
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
    provider_ident = Column(String(128), nullable=False)
    config = Column(PickleType, nullable=False)

    bot = relationship('Bot')


class Linkage(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'linkage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    start_node_id = Column(ForeignKey('node.id'), nullable=False)
    end_node_id = Column(ForeignKey('node.id'), nullable=False)
    action_ident = Column(String(128), nullable=False)
    ack_message = Column(UnicodeText, nullable=False)

    start_node = relationship('Node', foreign_keys=[start_node_id],
                              backref='linkages')
    end_node = relationship('Node', foreign_keys=[end_node_id])


class SupportedPlatform(enum.Enum):
    All = 'All'
    Facebook = 'Facebook'
    Line = 'Line'


class ContentModule(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'content_module'

    id = Column(String(128), primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    supported_platform = Column(Enum(SupportedPlatform), nullable=False,
                                default=SupportedPlatform.All)
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
    supported_platform = Column(Enum(SupportedPlatform), nullable=False,
                                default=SupportedPlatform.All)
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
    key = Column(String(128), nullable=False)
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
    event_name = Column(String(128), nullable=False)
    event_value = Column(PickleType, nullable=False)


class FeedEnum(enum.Enum):
    RSS = 'RSS'
    ATOM = 'ATOM'
    CSV = 'CSV'
    JSON = 'JSON'
    XML = 'XML'


class Feed(DeclarativeBase, QueryHelperMixin, JSONSerializer):
    __tablename__ = 'feed'

    __json_hidden__ = ['account_id']

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    url = Column(String(256), nullable=False)
    type = Column(Enum(FeedEnum), nullable=False)
    title = Column(Unicode(128), nullable=False)
    image_url = Column(String(256), nullable=False)

    @classmethod
    def search_title(cls, term):
        return cls.query(cls).filter(cls.title.like(unicode('%' + term + '%')))


class PublicFeed(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'public_feed'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(256), nullable=False)
    type = Column(Enum(FeedEnum), nullable=False)
    title = Column(Unicode(128), nullable=False)
    image_url = Column(String(256), nullable=False)


class Entry(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    title = Column(Unicode(128), nullable=False)
    link = Column(Unicode(256), nullable=False)
    description = Column(UnicodeText, nullable=False)
    publish_time = Column(DateTime, nullable=False)
    source_name = Column(Unicode(64), nullable=False)
    image_url = Column(String(256), nullable=False)
    author = Column(Unicode(64), nullable=False)
    content = Column(UnicodeText, nullable=False)

    tags = relationship('Tag', secondary='entry_tag')


class Broadcast(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'broadcast'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(PickleType, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)


class Tag(DeclarativeBase, QueryHelperMixin):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(64), nullable=False)


t_entry_tag = Table(
    'entry_tag', metadata,
    Column('entry_id', ForeignKey('entry.id'), nullable=False),
    Column('tag_id', ForeignKey('tag.id'), nullable=False)
)

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
