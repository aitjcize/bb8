# -*- coding: utf-8 -*-
"""
    ORM definition
    ~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import hashlib

import enum
from sqlalchemy import (Table, Column, ForeignKey,
                        Integer, Unicode, String, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from bb8_client.database_utils import (DeclarativeBase, DatabaseManager,
                                       DatabaseSession, ModelMixin)

from drama import config

DatabaseManager.set_database_uri(config.DATABASE)
DatabaseManager.set_pool_size(config.N_THREADS)


def Initialize():
    """Initialize the database and create all tables if there don't exist."""
    with DatabaseSession():
        for table in ['episode', 'drama', 'user']:
            if table not in DatabaseManager.engine.table_names():
                DatabaseManager.reset()
                return


class DramaCountryEnum(enum.Enum):
    TAIWAN = 'tw'
    JAPAN = 'jp'
    KOREA = 'kr'
    CHINA = 'cn'
    NOT_CLASSIFIED = 'default'


class Drama(DeclarativeBase, ModelMixin):
    __tablename__ = 'drama'
    __table_args__ = (UniqueConstraint('name'),)

    def generate_link_hash(context):  # pylint: disable=E0213
        return hashlib.sha1(context.current_parameters['link']).hexdigest()

    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(Unicode(512), nullable=False)
    link_hash = Column(String(40),
                       default=generate_link_hash,
                       nullable=False)
    name = Column(Unicode(64), nullable=False)
    description = Column(Unicode(512), nullable=False)
    image = Column(Unicode(512), nullable=False)
    country = Column(Enum(DramaCountryEnum), nullable=True)
    order = Column(Integer, nullable=True)

    episodes = relationship('Episode', backref='drama')

    def __repr__(self):
        return u'<%s(\'%s\')>' % (type(self).__name__, self.name)


class Episode(DeclarativeBase, ModelMixin):
    __tablename__ = 'episode'

    def generate_link_hash(context):  # pylint: disable=E0213
        return hashlib.sha1(context.current_parameters['link']).hexdigest()

    link = Column(Unicode(512), nullable=False)
    link_hash = Column(String(40), primary_key=True,
                       default=generate_link_hash, nullable=False)

    drama_id = Column(Integer, ForeignKey('drama.id'))

    serial_number = Column(Integer, nullable=False)

    def __repr__(self):
        return '<%s(\'%s\')>' % (type(self).__name__, self.link)


class User(DeclarativeBase, ModelMixin):
    __tablename__ = 'drama_user'

    id = Column(Integer, primary_key=True)

    subscribed_dramas = relationship(
        'Drama',
        secondary='subscription',
        backref='users')


t_subscription = Table(
    'subscription', DeclarativeBase.metadata,
    Column('user_id', ForeignKey('drama_user.id'), nullable=False),
    Column('drama_id', ForeignKey('drama.id'), nullable=False)
)
