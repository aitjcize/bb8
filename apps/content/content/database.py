# -*- coding: utf-8 -*-
"""
    ORM definition
    ~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import hashlib

from sqlalchemy import (Column, DateTime, ForeignKey, Integer,
                        Table, Unicode, String)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

from content import config

from bb8_client.database_utils import (DeclarativeBase, DatabaseManager,
                                       DatabaseSession, ModelMixin)


# Configure database
DatabaseManager.set_database_uri(config.DATABASE)
DatabaseManager.set_pool_size(config.N_THREADS)


def Initialize():
    """Initialize the database and create all tables if there don't exist."""
    with DatabaseSession():
        for table in ['entry', 'tag', 'keyword']:
            if table not in DatabaseManager.engine.table_names():
                DatabaseManager.reset()
                return


class Tag(DeclarativeBase, ModelMixin):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(64), nullable=False)


class Entry(DeclarativeBase, ModelMixin):
    __tablename__ = 'entry'
    __table_args__ = (UniqueConstraint('link'),)

    def generate_link_hash(context):  # pylint: disable=E0213
        return hashlib.sha1(context.current_parameters['link']).hexdigest()

    link_hash = Column(String(40), primary_key=True,
                       default=generate_link_hash, nullable=False)
    title = Column(Unicode(256), nullable=False)
    link = Column(Unicode(512), nullable=False)
    publish_time = Column(DateTime, nullable=False)
    source = Column(Unicode(64), nullable=False)
    original_source = Column(Unicode(64), nullable=False)
    image_url = Column(Unicode(512), nullable=False)
    author = Column(Unicode(64), nullable=False)

    tags = relationship('Tag', secondary='entry_tag')

    @classmethod
    def search(cls, term, count):
        return cls.query().filter(
            cls.title.like(unicode('%' + term + '%'))
        ).limit(count).all()

    def __repr__(self):
        return '<%s(\'%s\')>' % (type(self).__name__, self.link)


class Keyword(DeclarativeBase, ModelMixin):
    __tablename__ = 'keyword'
    __table_args__ = (UniqueConstraint('name'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('keyword.id'))
    name = Column(Unicode(64), nullable=False)

    related_keywords = relationship('Keyword')


t_entry_tag = Table(
    'entry_tag', DeclarativeBase.metadata,
    Column('entry_link_hash', ForeignKey('entry.link_hash'), nullable=False),
    Column('tag_id', ForeignKey('tag.id'), nullable=False)
)
