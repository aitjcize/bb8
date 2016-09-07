# -*- coding: utf-8 -*-
"""
    Database ORM definition
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import time

from datetime import datetime

import enum
import pytz

from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (scoped_session, sessionmaker, joinedload,
                            object_session)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import has_identity


DeclarativeBase = declarative_base()


class DatabaseManager(object):
    """
    Database Manager class
    """
    database_uri = None
    engine = None
    db = None

    @classmethod
    def set_database_uri(cls, database_uri):
        cls.database_uri = database_uri

    @classmethod
    def connect(cls, engine=None):
        """Set DatabaseManager.db to a scoped_session instance.

        engine is the source of database connections, it provide pooling
        functions. A scoped_session is a thread-local object using the Registry
        pattern, which means every call to the scoped_session instance returns
        the same session object. We store scoped_session instance as
        DatabaseManager.db for easier access in ModelMixin. When the remove()
        method of a scoped_session is called, the database connection is
        returned to the engine pool.
        """
        if engine:
            cls.engine = engine
        elif cls.engine is None:
            cls.create_engine()

        if not cls.db:
            cls.db = scoped_session(sessionmaker(bind=cls.engine))

    @classmethod
    def disconnect(cls, commit=True):
        if commit:
            try:
                cls.db().commit()
            except InvalidRequestError:
                cls.db().rollback()
        cls.db().close()
        cls.db.remove()

    @classmethod
    def reconnect(cls, commit=True):
        cls.disconnect(commit)
        cls.connect()

    @classmethod
    def session(cls):
        if cls.engine is None:
            cls.create_engine()
        return sessionmaker(bind=cls.engine)()

    @classmethod
    def create_engine(cls):
        if cls.database_uri is None:
            raise RuntimeError('DATABASE_URI not set')
        cls.engine = create_engine(cls.database_uri, echo=False,
                                   encoding='utf-8', pool_size=8,
                                   pool_recycle=3600 * 8)

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
        cls.db().commit()

    @classmethod
    def flush(cls):
        cls.db().flush()

    @classmethod
    def rollback(cls):
        cls.db().rollback()


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
        DatabaseManager.commit()

    @classmethod
    def flush(cls):
        DatabaseManager.flush()

    @classmethod
    def query(cls, *args):
        """Short hand for query."""
        if args:
            return DatabaseManager.db().query(*args)
        else:
            return DatabaseManager.db().query(cls)

    @classmethod
    def get_all(cls):
        """Get all record from a table."""
        query_object = cls.query()
        return query_object.all()

    @classmethod
    def get_by(cls, eager=None, order_by=None, offset=0, limit=0,
               single=False, lock=False, query=False, **kwargs):
        """Get item by kwargs."""
        query_object = cls.query()
        if eager:
            joinloads = [joinedload(x) for x in eager]
            query_object = query_object.options(*joinloads)

        query_object = query_object.filter_by(**kwargs)

        if order_by:
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

    def add(self):
        """Register object."""
        DatabaseManager.db().add(self)
        return self

    def commit_unique(self):
        """Register object."""
        try:
            DatabaseManager.db().add(self)
            DatabaseManager.commit()
        except IntegrityError:
            DatabaseManager.rollback()
            return None
        return self

    def delete(self):
        """Unregister object."""
        self.query().filter_by(id=self.id).delete()
        return self

    def refresh(self):
        """Refresh object and reconnect it with session."""
        #: Detached
        if object_session(self) is None and has_identity(self):
            DatabaseManager.db().add(self)
        DatabaseManager.db().refresh(self)
        return self

    def rexpunge(self):
        """Refresh then detach from session."""
        DatabaseManager.db().refresh(self)
        DatabaseManager.db().expunge(self)
        return self

    def expunge(self):
        """Detach from session."""
        DatabaseManager.db().expunge(self)
        return self

    def merge(self):
        """Merge a object with current session"""
        DatabaseManager.db().merge(self)
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
