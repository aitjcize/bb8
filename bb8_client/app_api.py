# -*- coding: utf-8 -*-
"""
    Application API
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import cPickle

from grpc.beta import implementations

from bb8_client import config, app_service_pb2

# pylint: disable=E0611,E0401,W0611
from bb8_client.base_message import Message, Render


_DEFAULT_TIMEOUT_SECS = 10


class MessagingService(object):

    def __init__(self, timeout=_DEFAULT_TIMEOUT_SECS):
        channel = implementations.insecure_channel(config.HOST, config.PORT)
        self._stub = app_service_pb2.beta_create_MessagingService_stub(channel)
        self._timeout = timeout

    def Ping(self):
        res = self._stub.Ping(app_service_pb2.Empty(), self._timeout)

        if not res.success:
            raise RuntimeError('Ping: %s' % res.msg)

    def Send(self, user_ids, msgs):
        res = self._stub.Send(
            app_service_pb2.SendRequest(
                user_ids=user_ids,
                messages_object=cPickle.dumps([m.as_dict() for m in msgs])),
            self._timeout)

        if not res.success:
            raise RuntimeError('Send: %s' % res.msg)

    def Broadcast(self, bot_id, msgs):
        res = self._stub.Broadcast(
            app_service_pb2.BroadcastRequest(
                bot_id=bot_id,
                messages_object=cPickle.dumps([m.as_dict() for m in msgs])),
            self._timeout)

        if not res.success:
            raise RuntimeError('Broadcast: %s' % res.msg)
