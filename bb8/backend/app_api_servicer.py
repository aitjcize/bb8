#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Application API Servicer
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import contextlib
import cPickle
import os
import time
import traceback

from bb8 import config
from bb8.backend.database import DatabaseManager, Bot, User
from bb8.backend import messaging
from bb8.backend.message import Message
from bb8.logging_utils import Logger
from bb8.pb_modules import app_service_pb2  # pylint: disable=E0611


SECONDS_IN_A_DAY = 86400

logger = Logger(os.path.join(config.LOG_DIR, config.API_SERVICER_LOG_FILE),
                'app-api-servicer')


class MessagingServicer(app_service_pb2.BetaMessagingServiceServicer):
    def Ping(self, unused_request, unused_context):
        return app_service_pb2.Status(success=True, msg=None)

    def Send(self, request, unused_context):
        try:
            msgs = [Message.FromDict(m) for m in
                    cPickle.loads(request.messages_object)]
        except Exception:
            return app_service_pb2.Status(
                success=False,
                msg=('Failed to deserialize message:\n%s' %
                     traceback.format_exc()))

        with contextlib.closing(DatabaseManager.session()) as sess:
            for user_id in request.user_ids:
                user = sess.query(User).filter_by(id=user_id).limit(1).one()
                if user:
                    messaging.send_message(user, msgs)

        return app_service_pb2.Status(success=True, msg=None)

    def Broadcast(self, request, unused_context):
        with contextlib.closing(DatabaseManager.session()) as sess:
            bot = sess.query(Bot).filter_by(id=request.bot_id).limit(1).one()
            if bot is None:
                return app_service_pb2.Status(
                    success=False,
                    msg='Bot<%d> does not exist' % request.bot_id)

            try:
                msgs = [Message.FromDict(m) for m in
                        cPickle.loads(request.messages_object)]
            except Exception:
                return app_service_pb2.Status(
                    success=False,
                    msg=('Failed to deserialize message:\n%s' %
                         traceback.format_exc()))

            users = sess.query(User).filter_by(bot_id=request.bot_id)
            for user in users:
                messaging.send_message(user, msgs)

        return app_service_pb2.Status(success=True, msg=None)


def start_server():
    server = app_service_pb2.beta_create_MessagingService_server(
        MessagingServicer())
    server.add_insecure_port('[::]:%d' % config.APP_API_SERVICE_PORT)
    server.start()
    logger.info('BB8 Application API servicer started.')

    try:
        while True:
            time.sleep(SECONDS_IN_A_DAY)
    except KeyboardInterrupt:
        logger.info('Recieved KeyboardInterrupt, server stopped.')


if __name__ == '__main__':
    start_server()
