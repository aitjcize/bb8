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

from bb8 import config
from bb8.backend.database import DatabaseSession, Bot, User
from bb8.backend import messaging_tasks
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

    def Push(self, request, context):
        with DatabaseSession():
            messages_dict = cPickle.loads(request.messages_object)
            users = User.query().filter(User.id.in_(request.user_ids)).all()
            messaging_tasks.push_message_from_dict_async(
                users, messages_dict, request.eta, request.user_localtime)

        return app_service_pb2.Empty()

    def Broadcast(self, request, unused_context):
        with DatabaseSession():
            bot = Bot.get_by(id=request.bot_id, single=True)
            if not bot:
                raise RuntimeError('Bot<%d> does not exist' % request.bot_id)

            eta = None if request.eta == 0 else request.eta
            messages_dict = cPickle.loads(request.messages_object)
            if request.static:
                msgs = [Message.FromDict(m, {}) for m in messages_dict]
                messaging_tasks.broadcast_message_async(bot, msgs, eta)
            else:
                users = User.get_by(bot_id=request.bot_id)
                messaging_tasks.push_message_from_dict_async(
                    users, messages_dict, eta)

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
