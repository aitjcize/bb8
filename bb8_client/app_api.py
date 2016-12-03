# -*- coding: utf-8 -*-
"""
    Application API
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import cPickle
import urllib

import grpc

from bb8_client import config
from bb8_client import app_service_pb2  # pylint: disable=E0611

# pylint: disable=E0611,E0401,W0611
from bb8_client.base_message import (Message, Render, TextPayload,
                                     LocationPayload, EventPayload)


_DEFAULT_TIMEOUT_SECS = 10


class MessagingService(object):

    def __init__(self, timeout=_DEFAULT_TIMEOUT_SECS):
        channel = grpc.insecure_channel('%s:%d' % (config.HOST, config.PORT))
        self._stub = app_service_pb2.MessagingServiceStub(channel)
        self._timeout = timeout

    def Ping(self):
        self._stub.Ping(app_service_pb2.Empty(), self._timeout)

    def Push(self, user_ids, msgs, eta=None, user_localtime=False):
        try:
            serialized_message = [m.as_dict() for m in msgs]
        except Exception as e:
            raise RuntimeError('Failed to serialize message: %s' % e)

        self._stub.Push(
            app_service_pb2.PushRequest(
                user_ids=user_ids,
                messages_object=cPickle.dumps(serialized_message),
                eta=eta,
                user_localtime=user_localtime),
            self._timeout)

    def Broadcast(self, bot_id, msgs, static=True):
        try:
            serialized_message = [m.as_dict() for m in msgs]
        except Exception as e:
            raise RuntimeError('Failed to serialize message: %s' % e)

        self._stub.Broadcast(
            app_service_pb2.BroadcastRequest(
                bot_id=bot_id,
                messages_object=cPickle.dumps(serialized_message),
                static=static),
            self._timeout)


def CacheImage(link, width=500):
    """Wrap the image specified by *link* and return the cached URL."""
    link = link[link.index('//') + 2:]
    return 'https://images.weserv.nl/?url={0}&q=95&h={1}'.format(
        urllib.quote(link), width)


def TrackedURL(link, path_name):
    """Wraps given *link* with in tracking API."""
    return ('https://%s:%s/api/r/{{bot_id}}/'
            '{{user.platform_user_ident}}?path=%s&url=%s' %
            (config.RESOURCE_HOSTNAME, config.HTTP_PORT, path_name, link))
