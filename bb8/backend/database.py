# -*- coding: utf-8 -*-
"""
    Database ORM definition
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import importlib
import uuid

from datetime import datetime, timedelta

import enum
import jwt

from passlib.hash import bcrypt  # pylint: disable=E0611
from flask import Flask  # pylint: disable=C0411,C0413

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        PickleType, Table, Text, String, Unicode, UnicodeText)
from sqlalchemy.orm import relationship, deferred
from sqlalchemy.schema import UniqueConstraint

from bb8 import config

# pylint: disable=W0611
from bb8.backend.database_utils import (DeclarativeBase, DatabaseManager,
                                        DatabaseSession, ModelMixin,
                                        JSONSerializer)
from bb8.backend.metadata import SessionRecord
from bb8.error import AppError
from bb8.constant import HTTPStatus, CustomError


# Configure database
DatabaseManager.set_database_uri(config.DATABASE)
DatabaseManager.set_pool_size(config.N_THREADS)


class AppContext(object):
    """Convenient wrapper for app.test_request_context()"""
    def __init__(self, app=None, engine=None):
        if app is None:
            app = Flask(__name__)
        self.context = app.test_request_context()
        self.engine = engine

    def __enter__(self):
        self.context.__enter__()
        DatabaseManager.connect(self.engine)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        DatabaseManager.disconnect()
        self.context.__exit__(exc_type, exc_value, tb)


class Account(DeclarativeBase, ModelMixin, JSONSerializer):
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


class OAuthInfo(DeclarativeBase, ModelMixin):
    __tablename__ = 'oauth_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)

    provider = Column(Enum(OAuthProviderEnum), nullable=False)
    provider_ident = Column(String(256), nullable=False)

    account = relationship('Account', back_populates="oauth_infos")


class PlatformTypeEnum(enum.Enum):
    Facebook = 'Facebook'
    Line = 'Line'


class Bot(DeclarativeBase, ModelMixin, JSONSerializer):
    __tablename__ = 'bot'

    __json_public__ = ['id', 'name', 'description', 'root_node_id',
                       'start_node_id', 'platforms']

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False)
    description = Column(UnicodeText, nullable=False)
    interaction_timeout = Column(Integer, nullable=False, default=120)
    admin_interaction_timeout = Column(Integer, nullable=False, default=180)
    session_timeout = Column(Integer, nullable=False, default=86400)
    ga_id = Column(Unicode(32), nullable=True)
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
        self.delete_all_platforms()
        super(Bot, self).delete()

    def delete_all_node_and_links(self):
        """Delete all associated node and links of this bot."""
        Linkage.delete_by(bot_id=self.id)
        Node.delete_by(bot_id=self.id)

    def delete_all_platforms(self):
        """Delete all associated platform of this bot."""
        Platform.delete_by(bot_id=self.id)


class GenderEnum(enum.Enum):
    Male = 'Male'
    Female = 'Female'


class User(DeclarativeBase, ModelMixin, JSONSerializer):
    __tablename__ = 'user'

    __json_public__ = ['first_name', 'last_name', 'locale', 'gender',
                       'timezone']

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    platform_id = Column(ForeignKey('platform.id'), nullable=False)
    platform_user_ident = Column(String(128), nullable=False)
    last_seen = Column(DateTime, nullable=False)
    last_admin_seen = Column(DateTime, nullable=False,
                             default=datetime(1970, 1, 1))
    login_token = deferred(Column(Text, nullable=True))

    first_name = Column(Unicode(32), nullable=True)
    last_name = Column(Unicode(32), nullable=True)
    locale = Column(String(16), nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    timezone = Column(Integer, nullable=True)

    session = Column(SessionRecord.as_mutable(PickleType), nullable=True)

    platform = relationship('Platform')
    colleted_data = relationship('ColletedDatum')

    def goto(self, node_id):
        """Goto a node."""
        sess = self.session
        self.session = SessionRecord(node_id)
        if sess:
            self.session.input_transformation = sess.input_transformation


class Node(DeclarativeBase, ModelMixin):
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


class Platform(DeclarativeBase, ModelMixin):
    __tablename__ = 'platform'
    __table_args__ = (UniqueConstraint('provider_ident'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(Enum(PlatformTypeEnum), nullable=False)
    provider_ident = Column(String(128), nullable=False)
    config = Column(PickleType, nullable=False)

    bot = relationship('Bot')


class Linkage(DeclarativeBase, ModelMixin):
    __tablename__ = 'linkage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    start_node_id = Column(ForeignKey('node.id'), nullable=False)
    end_node_id = Column(ForeignKey('node.id'), nullable=False)
    action_ident = Column(String(128), nullable=False)
    ack_message = Column(PickleType, nullable=False)

    start_node = relationship('Node', foreign_keys=[start_node_id],
                              backref='linkages')
    end_node = relationship('Node', foreign_keys=[end_node_id])


class SupportedPlatform(enum.Enum):
    All = 'All'
    Facebook = 'Facebook'
    Line = 'Line'


class ContentModule(DeclarativeBase, ModelMixin):
    __tablename__ = 'content_module'

    id = Column(String(128), primary_key=True, nullable=False)
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


class ParserModule(DeclarativeBase, ModelMixin):
    __tablename__ = 'parser_module'

    id = Column(String(128), primary_key=True, nullable=False)
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


class ColletedDatum(DeclarativeBase, ModelMixin):
    __tablename__ = 'collected_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    key = Column(String(128), nullable=False)
    value = Column(PickleType, nullable=False)


class SenderEnum(enum.Enum):
    Bot = 'BOT'
    Human = 'HUMAN'


class Conversation(DeclarativeBase, ModelMixin):
    __tablename__ = 'conversation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    sender_enum = Column(Enum(SenderEnum), nullable=False)
    msg = Column(PickleType, nullable=False)

    user = relationship('User')


class Event(DeclarativeBase, ModelMixin):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    event_name = Column(String(128), nullable=False)
    event_value = Column(PickleType, nullable=False)


class Broadcast(DeclarativeBase, ModelMixin):
    __tablename__ = 'broadcast'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(PickleType, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)


class FeedEnum(enum.Enum):
    RSS = 'RSS'
    ATOM = 'ATOM'
    CSV = 'CSV'
    JSON = 'JSON'
    XML = 'XML'


class Feed(DeclarativeBase, ModelMixin, JSONSerializer):
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
        return cls.query().filter(cls.title.like(unicode('%' + term + '%')))


class PublicFeed(DeclarativeBase, ModelMixin):
    __tablename__ = 'public_feed'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(256), nullable=False)
    type = Column(Enum(FeedEnum), nullable=False)
    title = Column(Unicode(128), nullable=False)
    image_url = Column(String(256), nullable=False)


t_account_bot = Table(
    'account_bot', DeclarativeBase.metadata,
    Column('account_id', ForeignKey('account.id'), nullable=False),
    Column('bot_id', ForeignKey('bot.id'), nullable=False)
)


t_bot_node = Table(
    'bot_node', DeclarativeBase.metadata,
    Column('bot_id', ForeignKey('bot.id'), nullable=False),
    Column('node_id', ForeignKey('node.id'), nullable=False)
)
