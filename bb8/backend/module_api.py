#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API
    ~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import importlib
from datetime import datetime, timedelta

from flask import g

from sqlalchemy import desc

from bb8 import config
# pylint: disable=W0611
from bb8.backend.database import PlatformTypeEnum, SupportedPlatform
from bb8.backend.database import CollectedDatum as _CollectedDatum
# pylint: disable=W0611
from bb8.backend.message import (Message, Render, Resolve, IsVariable,
                                 TextPayload, LocationPayload, EventPayload)
from bb8.backend.messaging import broadcast_message_async
from bb8.backend.metadata import ParseResult


CONFIG = {
    'HTTP_ROOT': 'https://%s:%d/' % (config.HOSTNAME, config.HTTP_PORT)
}


# Expose broadcast_message_async as module API
BroadcastMessage = broadcast_message_async


def Config(key):
    """Return a config value given."""
    return CONFIG.get(key, None)


def GetUserId():
    """Get User ID."""
    return g.user.id


def GetUserTime():
    """Get current time according to user's timezone."""
    return datetime.utcnow() + timedelta(hours=g.user.timezone)


def GetgRPCService(name):
    """Get third-party app gRPC service."""
    hostname = config.APP_HOSTNAME_MAP.get(name, None)
    if hostname is None:
        raise RuntimeError('unknown service `%s\'' % name)

    try:
        module = importlib.import_module(
            'bb8.pb_modules.%s_service_pb2' % name.lower())
    except Exception:
        raise RuntimeError('no gRPC module available for `%s\'' % name)

    return module, (hostname, config.APP_GRPC_SERVICE_PORT)


def CacheImage(link):
    return 'https://{0}:{1}/api/util/cache_image?url={2}'.format(
        config.HOSTNAME, config.HTTP_PORT, link)


class Memory(object):
    """API wrapper for User.memory dictionary."""
    @classmethod
    def Get(cls, key, default=None):
        return g.user.memory.get(key, default)

    @classmethod
    def Set(cls, key, value):
        g.user.memory[key] = value

    @classmethod
    def Clear(cls):
        return g.user.memory.clear()


class Settings(object):
    """API wrapper for User.settings dictionary."""
    __protected_fields__ = ['subscribe']

    @classmethod
    def Get(cls, key, default=None):
        return g.user.settings.get(key, default)

    @classmethod
    def Set(cls, key, value):
        g.user.settings[key] = value

    @classmethod
    def Clear(cls):
        """Clear all non-protected fields."""
        g.user.settings = dict((f, g.user.settings[f])
                               for f in cls.__protected_fields__)


class CollectedData(object):
    """API for getting user collected data."""
    _MAX_RETURN_RESULTS = 100

    @classmethod
    def GetLast(cls, key, default=None):
        """Get the last collected result given *key*."""
        result = _CollectedDatum.get_by(
            query=[_CollectedDatum.value], user_id=g.user.id, key=key,
            order_by=[desc('created_at')],
            single=True)
        return result[0] if result else default

    @classmethod
    def Get(cls, key, limit=1, offset=0):
        """Get *limit* result starting from *offset* given *key*.

        The max number of results is constraint to _MAX_RETURN_RESULTS.
        """
        if limit > cls._MAX_RETURN_RESULTS:
            limit = cls._MAX_RETURN_RESULTS

        result = _CollectedDatum.get_by(
            query=[_CollectedDatum.value], user_id=g.user.id,
            key=key, order_by=[desc('created_at')],
            offset=offset, limit=limit)
        return [x[0] for x in result] if result else []

    @classmethod
    def Count(cls, key):
        """Get number of entries."""
        return _CollectedDatum.count_by(user_id=g.user.id, key=key)
