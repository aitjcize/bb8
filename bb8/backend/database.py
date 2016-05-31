# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy import (Column, ForeignKey, Integer, String, Table, Text,
                        PickleType, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    passwd = Column(String(256), nullable=False)

    bots = relationship('Bot', secondary='account_bot')


t_account_bot = Table(
    'account_bot', metadata,
    Column('account_id', ForeignKey('account.id'), nullable=False),
    Column('bot_id', ForeignKey('bot.id'), nullable=False)
)


class Bot(Base):
    __tablename__ = 'bot'

    id = Column(Integer, primary_key=True, autoincrement=True)
    interaction_timeout = Column(Integer, nullable=False)
    session_timeout = Column(Integer, nullable=False)
    root_node_id = Column(Integer, nullable=False)
    start_node_id = Column(Integer, nullable=False)

    orphan_nodes = relationship('Node', secondary='bot_node')
    platforms = relationship('Platform')


t_bot_node = Table(
    'bot_node', metadata,
    Column('bot_id', ForeignKey('bot.id'), nullable=False),
    Column('node_id', ForeignKey('node.id'), nullable=False)
)


class PlatformTypeEnum(Enum):
    Facebook = 'FACEBOOK'
    Line = 'LINE'


class Platform(Base):
    __tablename__ = 'platform'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(PlatformTypeEnum, nullable=False)
    config = Column(PickleType, nullable=False)


class Node(Base):
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
    linkages = relationship('Linkage')


class Action(Base):
    __tablename__ = 'action'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=False)


class Linkage(Base):
    __tablename__ = 'linkage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_node_id = Column(ForeignKey('node.id'), nullable=False)
    end_node_id = Column(ForeignKey('node.id'), nullable=False)
    action_id = Column(ForeignKey('action.id'), nullable=False)
    ack_message = Column(Text, nullable=False)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    platform_type_enum = Column(PlatformTypeEnum, nullable=False)
    platform_user_id = Column(String(512), nullable=False)
    session_stack = Column(PickleType, nullable=False)


class ContentModule(Base):
    __tablename__ = 'content_module'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    content_filename = Column(String(256), nullable=False)
    ui_filename = Column(String(256), nullable=False)
    input_parameter = Column(PickleType, nullable=False)


class ParserModule(Base):
    __tablename__ = 'parser_module'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    content_filename = Column(String(256), nullable=False)
    ui_filename = Column(String(256), nullable=False)
    variables = Column(PickleType, nullable=False)

    actions = relationship('Action', secondary='parser_module_action')


t_parser_module_action = Table(
    'parser_module_action', metadata,
    Column('parser_module_id', ForeignKey('parser_module.id'), nullable=False),
    Column('action_id', ForeignKey('action.id'), nullable=False)
)


class MessageTypeEnum(Enum):
    Text = 'TEXT'
    Card = 'CARD'


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(Integer, nullable=False)
    content = Column(PickleType, nullable=False)


class ColletedDatum(Base):
    __tablename__ = 'colleted_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    key = Column(String(512), nullable=False)
    value = Column(PickleType, nullable=False)


class Conversation(Base):
    __tablename__ = 'conversation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    sender_enum = Column(Integer, nullable=False)
    msg = Column(PickleType, nullable=False)

    user = relationship('User')


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    event_name = Column(String(512), nullable=False)
    event_value = Column(PickleType, nullable=False)


engine = create_engine('sqlite:///test.db', echo=True)
Base.metadata.create_all(engine)
