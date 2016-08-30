#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Application API Unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import multiprocessing
import time
import unittest

import mock

from bb8.backend.app_api_servicer import start_server
from bb8.backend.database import DatabaseManager
from bb8.backend.message import Message
from bb8.backend.test_utils import BaseMessagingMixin
from bb8_client.app_api import MessagingService


class MessagingServicerUnittest(unittest.TestCase, BaseMessagingMixin):
    def setUp(self):
        self._process = None
        self._service = MessagingService()

        DatabaseManager.connect()
        self.setup_prerequisite()

    def tearDown(self):
        if self._process:
            self._process.terminate()
        DatabaseManager.disconnect()

    def start_server(self):
        self._process = multiprocessing.Process(target=start_server)
        self._process.start()
        time.sleep(0.5)

    def test_Ping(self):
        self.start_server()

        self._service.Ping()

    def test_Send(self):
        m = Message('Test message')
        target = 'bb8.backend.messaging.send_message'
        with mock.patch(target):
            self.start_server()
            self._service.Send([self.user_1.id], [m, m])

        with self.assertRaises(RuntimeError):
            self._service.Send([self.user_1.id], ['bad message'])

    def test_Broadcast(self):
        m = Message('Test message')
        target = 'bb8.backend.messaging.send_message'
        with mock.patch(target):
            self.start_server()
            self._service.Broadcast(self.bot.id, [m, m])


if __name__ == '__main__':
    unittest.main()
