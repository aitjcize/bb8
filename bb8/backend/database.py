# -*- coding: utf-8 -*-
"""
    Database ORM definition
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import hashlib
import importlib
import time
import uuid

from datetime import datetime, timedelta

import enum
import jwt

from dogpile.cache.region import make_region

from passlib.hash import bcrypt  # pylint: disable=E0611
from flask import Flask  # pylint: disable=C0411,C0413

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        Float, PickleType, Table, Text, String, Unicode,
                        UnicodeText, func)
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import relationship, deferred
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict

from bb8 import config

# pylint: disable=W0611
from bb8.backend.database_utils import (DeclarativeBase, DatabaseManager,
                                        DatabaseSession, ModelMixin,
                                        JSONSerializableMixin)
from bb8.backend.metadata import SessionRecord
from bb8.backend.caching_query import FromCache, query_callable
from bb8.constant import HTTPStatus, CustomError


# Cache configuration
def md5_key_mangler(key):
    """Receive cache keys as long concatenated strings;
    distill them into an md5 hash."""
    # KEY- prefixed keys means it's a custom key, don't hash it
    if key.startswith('KEY-'):
        return key
    return hashlib.md5(key.encode('ascii')).hexdigest()


regions = {}
for region_name in config.DOGPILE_CACHE_CONFIG:
    regions[region_name] = make_region(key_mangler=md5_key_mangler).configure(
        'dogpile.cache.redis',
        arguments=config.DOGPILE_CACHE_CONFIG[region_name]
    )


# Configure database
DatabaseManager.set_database_uri(config.DATABASE)
DatabaseManager.set_pool_size(config.N_THREADS * 2)
DatabaseManager.set_query_cls(query_callable(regions))


@classmethod
def _flushall(cls, region):  # pylint: disable=W0613
    regions[region].backend.client.flushall()

DatabaseManager.flushall = _flushall


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


class AccountUser(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'account_user'
    __table_args__ = (UniqueConstraint('email'),)

    __json_public__ = ['name', 'email', 'email_verified', 'timezone']

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    name = Column(Unicode(256), nullable=False, default=u'')
    email = Column(String(256), nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    passwd = Column(String(256), nullable=False)
    timezone = Column(String(32), nullable=False, default='UTC')

    account = relationship('Account')
    oauth_infos = relationship('OAuthInfo', back_populates='account_user')

    @classmethod
    def register(cls, data, invite=None):
        if invite:
            account, payload = Account.from_invite_code(invite)
            if payload['email'] != data['email']:
                raise RuntimeError('invitation link not intended for this '
                                   'email')
        else:
            account = Account(name=unicode(data['email'])).add()

        return AccountUser(
            account=account, email=data['email']
        ).set_passwd(data['passwd']).add()

    @classmethod
    def register_oauth(cls, email, provider, provider_ident, invite=None):
        oauth_info = OAuthInfo.get_by(
            provider=provider,
            provider_ident=provider_ident, single=True)

        # if the user is already exists, log him in
        if oauth_info:
            return oauth_info.account_user

        account_user = AccountUser.get_by(
            email=email, single=True)

        if account_user:
            return account_user

        # Temporarily only allow invited social auth
        if config.DEPLOY and not invite:
            raise RuntimeError('we are currently invite-only')

        if invite:
            account, payload = Account.from_invite_code(invite)
            # If email is master email, a user is able to create new Account.
            if payload['email'] == config.INVITE_MASTER:
                account = Account(name=email).add()
            elif payload['email'] != email:
                raise RuntimeError('invitation link not intended for this '
                                   'email')
        else:
            account = Account(name=email).add()

        user = AccountUser(
            account=account, email=email, passwd='',
        ).add()

        oauth_info = OAuthInfo(
            account_user=user,
            provider=provider,
            provider_ident=provider_ident).add()
        return user

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
            raise RuntimeError('auth token is invalid')
        return cls.get_by(id=payload['sub'], single=True)


class AccountTierEnum(enum.Enum):
    Free = 'Free'
    Trial = 'Trial'
    Basic = 'Basic'


class Account(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'account'
    __table_args__ = (UniqueConstraint('name'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(256), nullable=False)
    stripe_customer_id = Column(String(128), nullable=True)
    membership = Column(Enum(AccountTierEnum), nullable=False,
                        default=AccountTierEnum.Free)
    active_until = Column(Integer, nullable=False, default=0)

    account_users = relationship('AccountUser')
    bots = relationship('Bot')
    platforms = relationship('Platform')
    broadcasts = relationship('Broadcast')
    feeds = relationship('Feed', lazy='dynamic')

    def active(self):
        return time.time() < self.active_until

    def invite_code(self, email, expiration=15):
        payload = {
            'iss': 'compose.ai',
            'sub': self.id,
            'email': email,
            'jti': str(uuid.uuid4()),  # unique identifier of the token
            'exp': datetime.utcnow() + timedelta(days=expiration)
        }
        token = jwt.encode(payload, config.JWT_SECRET)
        return token.decode('unicode_escape')

    @classmethod
    def from_invite_code(cls, token):
        try:
            payload = jwt.decode(token, config.JWT_SECRET)
        except (jwt.DecodeError, jwt.ExpiredSignature):
            raise RuntimeError('auth token is invalid')
        return cls.get_by(id=payload['sub'], single=True), payload


class OAuthProviderEnum(enum.Enum):
    Facebook = 'Facebook'
    Google = 'Google'
    Github = 'Github'


class OAuthInfo(DeclarativeBase, ModelMixin):
    __tablename__ = 'oauth_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_user_id = Column(ForeignKey('account_user.id'), nullable=False)

    provider = Column(Enum(OAuthProviderEnum), nullable=False)
    provider_ident = Column(String(256), nullable=False)

    account_user = relationship('AccountUser', back_populates="oauth_infos")


class PlatformTypeEnum(enum.Enum):
    Facebook = 'Facebook'
    Line = 'Line'


class Bot(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'bot'

    __json_public__ = ['id', 'ga_id', 'name', 'description']

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=True)
    name = Column(Unicode(64), nullable=False)
    description = deferred(Column(Unicode(512), nullable=False))
    interaction_timeout = Column(Integer, nullable=False, default=120)
    admin_interaction_timeout = Column(Integer, nullable=False, default=180)
    session_timeout = Column(Integer, nullable=False, default=86400)
    ga_id = Column(Unicode(32), nullable=True)
    settings = Column(PickleType, nullable=True)
    staging = deferred(Column(PickleType, nullable=True))

    account = relationship('Account')
    bot_defs = relationship('BotDef')
    nodes = relationship('Node')
    platforms = relationship('Platform')

    orphan_nodes = relationship('Node', secondary='bot_node')

    ROOT_STABLE_ID = 'Root'
    ROOT_ROUTER_STABLE_ID = 'RootRouter'
    START_STABLE_ID = 'Start'

    def __repr__(self):
        return '<%s(\'%s\', \'%s\')>' % (type(self).__name__, self.id,
                                         self.name.encode('utf8'))

    @property
    def detail_fields(self):
        return [
            'interaction_timeout',
            'admin_interaction_timeout',
            'session_timeout',
            'ga_id',
            'settings',
            'staging'
        ]

    @property
    def users(self):
        # Only list deployed platform in deployment and only list dev platforms
        # in non-deployment mode. This prevents us from accidentally affecting
        # production platforms.
        platform_ids = [p.id for p in Platform.get_by(
            bot_id=self.id, deployed=config.DEPLOY)]

        if not platform_ids:  # No associated platform
            return []
        return User.query().filter(User.platform_id.in_(platform_ids)).all()

    def node(self, stable_id):
        return Node.get_cached(self.id, stable_id)

    def delete(self):
        Node.delete_by(bot_id=self.id)
        BotDef.delete_by(bot_id=self.id)
        self.remove_platform_reference()
        super(Bot, self).delete()

    def delete_all_nodes(self):
        """Delete all associated node and links of this bot."""
        Node.delete_by(bot_id=self.id)

    def remove_platform_reference(self):
        """Remove all associated platform reference of this bot."""
        Platform.get_by(bot_id=self.id, return_query=True).update(
            {'bot_id': None})


class GenderEnum(enum.Enum):
    Male = 'Male'
    Female = 'Female'


class ThreadStatusEnum(enum.Enum):
    Read = 'Read'
    Unread = 'Unread'
    Assigned = 'Assigned'
    Open = 'Open'
    Closed = 'Closed'
    Archived = 'Archived'


class User(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'user'

    __json_public__ = ['first_name', 'last_name', 'locale', 'gender',
                       'timezone', 'platform_user_ident']

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform_id = Column(ForeignKey('platform.id'), nullable=False)
    platform_user_ident = Column(String(128), nullable=False)
    last_seen = Column(DateTime, nullable=False)
    last_admin_seen = Column(DateTime, nullable=False,
                             default=datetime(1970, 1, 1))

    # Profile information
    first_name = Column(Unicode(32), nullable=True)
    last_name = Column(Unicode(32), nullable=True)
    locale = Column(String(16), nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    timezone = Column(Integer, nullable=True)

    session = Column(SessionRecord.as_mutable(PickleType), nullable=True)
    memory = Column(MutableDict.as_mutable(PickleType), nullable=False,
                    default={})
    settings = Column(MutableDict.as_mutable(PickleType), nullable=False,
                      default={'subscribe': True})

    # CRM-related fields
    assignee = Column(ForeignKey('account_user.id'), nullable=True)
    status = Column(Enum(ThreadStatusEnum), nullable=True)
    comment = Column(UnicodeText, nullable=True)

    # Relationship
    platform = relationship('Platform')
    conversations = relationship('Conversation')
    colleted_data = relationship('CollectedDatum')
    labels = relationship('Label', secondary='user_label')

    def delete(self):
        Conversation.delete_by(user_id=self.id)
        CollectedDatum.delete_by(user_id=self.id)
        super(User, self).delete()

    def goto(self, stable_id):
        """Goto a node."""
        sess = self.session
        self.session = SessionRecord(stable_id)
        if sess:
            self.session.input_transformation = sess.input_transformation


class Node(DeclarativeBase, ModelMixin):
    __tablename__ = 'node'
    __table_args__ = (UniqueConstraint('bot_id', 'stable_id'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    stable_id = Column(String(128), nullable=False)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    name = Column(Unicode(128), nullable=False)
    description = deferred(Column(UnicodeText, nullable=False, default=u''))
    expect_input = Column(Boolean, nullable=False)
    next_node_id = Column(String(128), nullable=True)
    module_id = Column(ForeignKey('module.id'), nullable=False)
    config = Column(PickleType, nullable=False)

    bot = relationship('Bot')
    module = relationship('Module')

    def __repr__(self):
        return '<%s(\'%s\', \'%s\')>' % (type(self).__name__, self.id,
                                         self.stable_id)

    @classmethod
    def get_cache_key(cls, bot_id, stable_id):
        return 'KEY-node[module]-%s-%s' % (bot_id, stable_id)

    @classmethod
    def get_cached(cls, bot_id, stable_id):
        return Node.get_by(
            bot_id=bot_id, stable_id=stable_id, eager=['module'],
            cache=FromCache('default', cls.get_cache_key(bot_id, stable_id)),
            single=True)

    def invalidate_cached(self):
        return Node.invalidate_by(
            cache=FromCache(
                'default', self.get_cache_key(self.bot_id, self.stable_id)))


class Platform(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'platform'
    __table_args__ = (UniqueConstraint('provider_ident'),)

    __json_public__ = ['id', 'bot_id', 'name', 'type_enum', 'provider_ident']

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=True)
    name = Column(Unicode(128), nullable=False)
    deployed = Column(Boolean, nullable=False, default=True)
    type_enum = Column(Enum(PlatformTypeEnum), nullable=False)
    provider_ident = Column(String(128), nullable=False)
    config = Column(PickleType, nullable=False)

    account = relationship('Account')
    bot = relationship('Bot')

    def __repr__(self):
        return '<%s(\'%s\', \'%s\')>' % (type(self).__name__, self.id,
                                         self.name.encode('utf8'))

    def delete(self):
        for user in User.get_by(platform_id=self.id):
            user.delete()
        super(Platform, self).delete()

    @classmethod
    def schema(cls):
        return {
            'type': 'object',
            'required': [
                'name',
                'deployed',
                'type_enum',
                'provider_ident',
                'config'
            ],
            'properties': {
                'bot_id': {
                    'type': ['null', 'integer'],
                },
                'name': {
                    'type': 'string',
                    'maxLength': 128
                },
                'deployed': {'type': 'boolean'},
                'type_enum': {
                    'enum': ['Facebook', 'Line']
                },
                'provider_ident': {
                    'type': 'string',
                    'maxLength': 128
                },
                'config': {'type': 'object'}
            }
        }

    @classmethod
    def get_cache_key(cls, provider_ident):
        return 'KEY-platform[bot]-%s' % provider_ident

    @classmethod
    def get_cached(cls, provider_ident):
        return Platform.get_by(
            provider_ident=provider_ident,
            eager=['bot'],
            cache=FromCache('default', cls.get_cache_key(provider_ident)),
            single=True)

    def invalidate_cached(self):
        Platform.invalidate_by(
            cache=FromCache(
                'default', self.get_cache_key(self.provider_ident)))


class SupportedPlatform(enum.Enum):
    All = 'All'
    Facebook = 'Facebook'
    Line = 'Line'


class ModuleTypeEnum(enum.Enum):
    Content = 'Content'
    Parser = 'Parser'
    Router = 'Router'
    Function = 'Function'


class Module(DeclarativeBase, ModelMixin):
    __tablename__ = 'module'

    id = Column(String(128), primary_key=True, nullable=False)
    type = Column(Enum(ModuleTypeEnum), nullable=False)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    supported_platform = Column(Enum(SupportedPlatform), nullable=False,
                                default=SupportedPlatform.All)
    module_name = Column(String(256), nullable=False)
    variables = Column(PickleType, nullable=False)

    MODULE_PACKAGE = 'bb8.backend.modules'

    def get_python_module(self):
        return importlib.import_module(
            '%s.%s' % (self.MODULE_PACKAGE, self.module_name))


class CollectedDatum(DeclarativeBase, ModelMixin):
    __tablename__ = 'collected_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    key = Column(String(128), nullable=False)
    value = Column(PickleType, nullable=False)


class SenderEnum(enum.Enum):
    Bot = 'Bot'
    User = 'User'
    Manual = 'Manual'


class Conversation(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'conversation'

    __json_public__ = ['id', 'sender_enum', 'sender', 'messages', 'timestamp']

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    sender_enum = Column(Enum(SenderEnum), nullable=False)
    sender = Column(ForeignKey('account_user.id'), nullable=True)
    messages = Column(PickleType, nullable=False)
    timestamp = Column(Float, nullable=False)

    user = relationship('User')


class Event(DeclarativeBase, ModelMixin):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    event_name = Column(String(128), nullable=False)
    event_value = Column(PickleType, nullable=False)


class BroadcastStatusEnum(enum.Enum):
    Draft = 'Draft'
    Queued = 'Queued'
    Sending = 'Sending'
    Sent = 'Sent'


class Broadcast(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'broadcast'

    __json_public__ = ['id', 'bot_id', 'name', 'messages', 'scheduled_time',
                       'status']

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    name = Column(Unicode(64), nullable=False)
    messages = Column(PickleType, nullable=False)
    scheduled_time = Column(DateTime, nullable=True)
    status = Column(Enum(BroadcastStatusEnum), nullable=False,
                    default=BroadcastStatusEnum.Draft)

    account = relationship('Account')

    @classmethod
    def schema(cls):
        return {
            'type': 'object',
            'required': [
                'account_id',
                'bot_id',
                'name',
                'messages',
                'scheduled_time',
            ],
            'properties': {
                'account_id': {'type': 'integer'},
                'bot_id': {'type': 'integer'},
                'name': {
                    'type': 'string',
                    'maxLength': 64
                },
                'messages': {
                    'type': 'array',
                    'item': {'type': 'object'}
                },
                'scheduled_time': {'type': 'integer'},
                'status': {'enum': ['Draft', 'Queued']}
            }
        }


class BotDef(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'bot_def'
    __table_args__ = (UniqueConstraint('bot_id', 'version'),)

    __json_public__ = ['id', 'bot_id', 'version', 'note']

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    version = Column(Integer, nullable=False)
    bot_json = deferred(Column(PickleType, nullable=False))
    note = Column(Unicode(64), nullable=True)

    @classmethod
    def add_version(cls, bot_id, bot_json, note=None):
        bot_def = None
        for unused_i in range(3):  # Retry for three times
            try:
                max_version = cls.query(func.max(cls.version)).filter_by(
                    bot_id=bot_id).one()[0]
                if max_version is None:
                    version = 1
                else:
                    version = max_version + 1
                bot_def = BotDef(bot_id=bot_id, version=version,
                                 bot_json=bot_json, note=note).add()
                DatabaseManager.flush()
            except (InvalidRequestError, IntegrityError):
                DatabaseManager.rollback()
            else:
                break
        return bot_def


class Label(DeclarativeBase, ModelMixin, JSONSerializableMixin):
    __tablename__ = 'label'
    __table_args__ = (UniqueConstraint('account_id', 'name'),)

    __json_public__ = ['id', 'name']

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=True)
    name = Column(Unicode(32), nullable=False)

    account = relationship('Account')


class FeedEnum(enum.Enum):
    RSS = 'RSS'
    ATOM = 'ATOM'
    CSV = 'CSV'
    JSON = 'JSON'
    XML = 'XML'


class Feed(DeclarativeBase, ModelMixin, JSONSerializableMixin):
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


t_bot_node = Table(
    'bot_node', DeclarativeBase.metadata,
    Column('bot_id', ForeignKey('bot.id'), nullable=False),
    Column('node_id', ForeignKey('node.id'), nullable=False)
)


t_user_label = Table(
    'user_label', DeclarativeBase.metadata,
    Column('user_id', ForeignKey('user.id'), nullable=False),
    Column('label_id', ForeignKey('label.id'), nullable=False)
)
