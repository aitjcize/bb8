# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy import (Column, ForeignKey, Integer, String, Table, Text,
                        PickleType)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
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

    id = Column(Integer, primary_key=True)
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


class Platform(Base):
    __tablename__ = 'platform'

    id = Column(Integer, primary_key=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(Integer, nullable=False)
    config = Column(PickleType, nullable=False)


class Node(Base):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    content_module_id = Column(ForeignKey('content_module.id'), nullable=False)
    content_config = Column(PickleType, nullable=False)
    parser_module_id = Column(ForeignKey('parser_module.id'), nullable=False)
    parser_config = Column(PickleType, nullable=False)
    action_map = Column(PickleType, nullable=False)

    bot = relationship('Bot')
    content_module = relationship('ContentModule')
    parser_module = relationship('ParserModule')
    linkages = relationship('Linkage')


class Linkage(Base):
    __tablename__ = 'linkage'

    id = Column(Integer, primary_key=True)
    start_node_id = Column(ForeignKey('node.id'), nullable=False)
    end_node_id = Column(ForeignKey('node.id'), nullable=False)
    action_id = Column(String(256), nullable=False)
    ack_message = Column(Text, nullable=False)


class BotUser(Base):
    __tablename__ = 'bot_user'

    id = Column(Integer, primary_key=True)
    platform_type_enum = Column(Integer, nullable=False)
    platform_user_id = Column(String(512), nullable=False)
    session_stack = Column(PickleType, nullable=False)


class ContentModule(Base):
    __tablename__ = 'content_module'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    content_filename = Column(String(256), nullable=False)
    ui_filename = Column(String(256), nullable=False)
    input_parameter = Column(PickleType, nullable=False)


class ParserModule(Base):
    __tablename__ = 'parser_module'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    content_filename = Column(String(256), nullable=False)
    ui_filename = Column(String(256), nullable=False)
    actions = Column(PickleType, nullable=False)
    variables = Column(PickleType, nullable=False)


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    type_enum = Column(Integer, nullable=False)
    content = Column(PickleType, nullable=False)

    bot = relationship('Bot')


class ColletedDatum(Base):
    __tablename__ = 'colleted_data'

    id = Column(Integer, primary_key=True)
    account_id = Column(ForeignKey('account.id'), nullable=False)
    bot_user_id = Column(ForeignKey('bot_user.id'), nullable=False)
    key = Column(String(512), nullable=False)
    value = Column(PickleType, nullable=False)

    account = relationship('Account')
    bot_user = relationship('BotUser')


class Conversation(Base):
    __tablename__ = 'conversation'

    id = Column(Integer, primary_key=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    bot_user_id = Column(ForeignKey('bot_user.id'), nullable=False)
    sender_enum = Column(Integer, nullable=False)
    msg = Column(PickleType, nullable=False)

    bot = relationship('Bot')
    bot_user = relationship('BotUser')


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    bot_id = Column(ForeignKey('bot.id'), nullable=False)
    bot_user_id = Column(ForeignKey('bot_user.id'), nullable=False)
    event_name = Column(String(512), nullable=False)
    event_value = Column(PickleType, nullable=False)

    bot = relationship('Bot')
    bot_user = relationship('BotUser')


engine = create_engine('sqlite:///test.db', echo=True)
Base.metadata.create_all(engine)
