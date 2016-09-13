#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Application API Servicer
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import cPickle
import os
import time

import grpc

from concurrent import futures
from flask import g

from bb8 import app, config
from bb8.backend.database import DatabaseSession, Bot, User
from bb8.backend import messaging
from bb8.backend.message import Message
from bb8.logging_utils import Logger
from bb8.pb_modules import app_service_pb2  # pylint: disable=E0611


_GRPC_MAX_WORKERS = 8
_SECONDS_IN_A_DAY = 86400

logger = Logger(os.path.join(config.LOG_DIR, config.API_SERVICER_LOG_FILE),
                'app-api-servicer')


class MessagingServicer(app_service_pb2.MessagingServiceServicer):
    def Ping(self, unused_request, unused_context):
        return app_service_pb2.Empty()

    def _SendToUsers(self, users, messages_dict):
        """Helper function for sending messages to users."""
        with app.test_request_context():
            user_count = User.count()
            for user in users:
                g.user = user
                variables = {
                    'statistic': {
                        'user_count': user_count
                    },
                    'user': user.to_json()
                }
                msgs = [Message.FromDict(m, variables) for m in messages_dict]

                messaging.send_message(user, msgs)

    def Send(self, request, context):
        with DatabaseSession():
            messages_dict = cPickle.loads(request.messages_object)
            users = User.query().filter(User.id.in_(request.user_ids))
            self._SendToUsers(users, messages_dict)

        return app_service_pb2.Empty()

    def Broadcast(self, request, unused_context):
        with DatabaseSession():
            bot = Bot.get_by(id=request.bot_id, single=True)
            if not bot:
                raise RuntimeError('Bot<%d> does not exist' % request.bot_id)

            messages_dict = cPickle.loads(request.messages_object)
            users = User.get_by(bot_id=request.bot_id)
            self._SendToUsers(users, messages_dict)

        return app_service_pb2.Empty()


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=_GRPC_MAX_WORKERS))
    app_service_pb2.add_MessagingServiceServicer_to_server(
        MessagingServicer(), server)
    server.add_insecure_port('[::]:%d' % config.APP_API_SERVICE_PORT)
    server.start()

    logger.info('BB8 Application API servicer started.')

    try:
        while True:
            time.sleep(_SECONDS_IN_A_DAY)
    except KeyboardInterrupt:
        logger.info('Recieved KeyboardInterrupt, server stopped.')


if __name__ == '__main__':
    start_server()
