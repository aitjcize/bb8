# -*- coding: utf-8 -*-
"""
    ORM definition
    ~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import (Column, DateTime, ForeignKey, Integer,
                        Table, Unicode)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker, joinedload,
                            relationship, object_session)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import has_identity


DeclarativeBase = declarative_base()
DATABASE = os.getenv('DATABASE')
engine = create_engine(DATABASE, echo=False,
                       encoding='utf-8',
                       pool_recycle=3600 * 8)

db = scoped_session(sessionmaker(engine))


def get_session():
    return scoped_session(sessionmaker(engine))


class ModelMixin(object):
    """Provides common field and methods for models."""

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<%s(\'%s\')>' % (type(self).__name__, self.id)

    @classmethod
    def columns(cls):
        return [m.key for m in cls.__table__.columns]

    @classmethod
    def commit(cls):
        db().commit()

    @classmethod
    def flush(cls):
        db().flush()

    @classmethod
    def query(cls):
        """Short hand for query."""
        return db().query(cls)

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
        db().add(self)
        return self

    def delete(self):
        """Unregister object."""
        self.query().filter_by(id=self.id).delete()
        return self

    def refresh(self):
        """Refresh object and reconnect it with session."""
        #: Detached
        if object_session(self) is None and has_identity(self):
            db().add(self)
        db().refresh(self)
        return self

    def rexpunge(self):
        """Refresh then detach from session."""
        db().refresh(self)
        db().expunge(self)
        return self

    def expunge(self):
        """Detach from session."""
        db().expunge(self)
        return self

    def merge(self):
        """Merge a object with current session"""
        db().merge(self)
        return self


class Tag(DeclarativeBase, ModelMixin):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(64), nullable=False)


class Entry(DeclarativeBase, ModelMixin):
    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Unicode(256), nullable=False)
    link = Column(Unicode(512), nullable=False, unique=True)
    publish_time = Column(DateTime, nullable=False)
    source = Column(Unicode(64), nullable=False)
    original_source = Column(Unicode(64), nullable=False)
    image_url = Column(Unicode(512), nullable=False)
    author = Column(Unicode(64), nullable=False)

    tags = relationship('Tag', secondary='entry_tag')

    @classmethod
    def search(cls, term, count):
        query = db().query(cls)
        return query.filter(
            cls.title.like(unicode('%' + term + '%'))).limit(count)

    @classmethod
    def columns(cls):
        return [m.key for m in cls.__table__.columns]


t_entry_tag = Table(
    'entry_tag', DeclarativeBase.metadata,
    Column('entry_id', ForeignKey('entry.id'), nullable=False),
    Column('tag_id', ForeignKey('tag.id'), nullable=False)
)
