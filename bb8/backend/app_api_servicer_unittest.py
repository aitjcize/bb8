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

from bb8.backend.app_api_servicer import start_server
from bb8.backend.database import DatabaseManager
from bb8.backend.message import Message
from bb8.backend.test_utils import (BaseTestMixin, start_celery_worker,
                                    stop_celery_worker)
from bb8_client.app_api import MessagingService


class MessagingServicerUnittest(unittest.TestCase, BaseTestMixin):
    def setUp(self):
        self._process = None
        self._service = MessagingService()

        DatabaseManager.connect()
        self.setup_prerequisite()
        self.start_service()

    def tearDown(self):
        if self._process:
            self._process.terminate()

        stop_celery_worker()
        DatabaseManager.disconnect()

    def start_service(self):
        # Start API server
        self._process = multiprocessing.Process(target=start_server)
        self._process.start()
        time.sleep(0.5)

        # Start celery worker
        start_celery_worker()
        time.sleep(3)

    def test_Ping(self):
        self._service.Ping()

    def test_Push(self):
        ms = [Message('AppAPI: Push: Test message')]
        self._service.Push([self.user_1.id], ms)

        with self.assertRaises(RuntimeError):
            self._service.Push([self.user_1.id], ['bad message'])

        # Wait for celery to process task
        time.sleep(5)

    def test_Broadcast(self):
        ms = [Message('AppAPI: Broadcast: Test message')]
        self._service.Broadcast(self.bot.id, ms)

        # Wait for celery to process task
        time.sleep(5)


if __name__ == '__main__':
    unittest.main()
