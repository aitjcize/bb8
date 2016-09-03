# -*- coding: utf-8 -*-
"""
    ORM definition
    ~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import hashlib
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import (Column, DateTime, ForeignKey, Integer,
                        Table, Unicode, String)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker, joinedload,
                            relationship, object_session)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import has_identity
from sqlalchemy.schema import UniqueConstraint

from content import config


DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata

engine = create_engine(config.DATABASE, echo=False,
                       encoding='utf-8',
                       pool_recycle=3600 * 8)

Session = scoped_session(sessionmaker(engine))


def Reset():
    metadata.drop_all(engine)
    metadata.create_all(engine)


def Initialize():
    """Initialize the database and create all tables if there don't exist."""
    for table in ['entry', 'tag', 'keyword']:
        if table not in engine.table_names():
            Reset()
            return


def GetSession():
    return sessionmaker(engine)()


class ModelMixin(object):
    """Provides common field and methods for models."""
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return '<%s(\'%s\')>' % (type(self).__name__, self.id)

    @classmethod
    def columns(cls):
        return [m.key for m in cls.__table__.columns]

    @classmethod
    def commit(cls):
        Session().commit()

    @classmethod
    def flush(cls):
        Session().flush()

    @classmethod
    def query(cls):
        """Short hand for query."""
        return Session().query(cls)

    @classmethod
    def get_all(cls, cache=None):
        """Get all record from a table."""
        query_object = cls.query()
        if cache:
            query_object = query_object.options(cache)
        return query_object.all()

    @classmethod
    def get_by(cls, eager=None, order_by=None, offset=0, limit=0,
               single=False, cache=None, lock=False, query=False, **kwargs):
        """Get item by kwargs."""
        query_object = cls.query()
        if eager:
            joinloads = [joinedload(x) for x in eager]
            query_object = query_object.options(*joinloads)

        if cache and not lock:
            query_object = query_object.options(cache)

        query_object = query_object.filter_by(**kwargs)

        if order_by is not None:
            query_object = query_object.order_by(*order_by)

        if offset:
            query_object = query_object.offset(offset)

        if limit:
            query_object = query_object.limit(limit)

        if lock:
            query_object = query_object.with_lockmode('update')

        if query:
            return query_object

        if single:
            try:
                return query_object.limit(1).one()
            except NoResultFound:
                return None
        return query_object.all()

    @classmethod
    def delete_by(cls, **kwargs):
        """Delete by kwargs."""
        return cls.query().filter_by(**kwargs).delete()

    @classmethod
    def delete_all(cls):
        """Delete all records from a table."""
        return cls.query().delete()

    @classmethod
    def exists(cls, **kwargs):
        return cls.get_by(**kwargs)

    @classmethod
    def count(cls):
        """Get count."""
        return cls.query().count()

    @classmethod
    def count_by(cls, **kwargs):
        """Get count by condition."""
        return cls.query().filter_by(**kwargs).count()

    def touch(self):
        """Update update_at timestamp."""
        self.updated_at = datetime.utcnow()

    def add(self):
        """Register object."""
        Session().add(self)
        return self

    def delete(self):
        """Unregister object."""
        self.query().filter_by(id=self.id).delete()
        return self

    def refresh(self):
        """Refresh object and reconnect it with session."""
        #: Detached
        if object_session(self) is None and has_identity(self):
            Session().add(self)
        Session().refresh(self)
        return self

    def rexpunge(self):
        """Refresh then detach from session."""
        Session().refresh(self)
        Session().expunge(self)
        return self

    def expunge(self):
        """Detach from session."""
        Session().expunge(self)
        return self

    def merge(self):
        """Merge a object with current session"""
        Session().merge(self)
        return self


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
        query = Session().query(cls)
        return query.filter(
            cls.title.like(unicode('%' + term + '%'))
        ).limit(count).all()

    @classmethod
    def columns(cls):
        return [m.key for m in cls.__table__.columns]

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
    'entry_tag', metadata,
    Column('entry_link_hash', ForeignKey('entry.link_hash'), nullable=False),
    Column('tag_id', ForeignKey('tag.id'), nullable=False)
)
