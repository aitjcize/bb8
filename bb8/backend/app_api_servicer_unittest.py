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
from bb8_client.app_api import MessagingService


class MessagingServicerUnittest(unittest.TestCase):
    def setUp(self):
        self._process = None

    def tearDown(self):
        if self._process:
            self._process.terminate()

    def start_server(self):
        self._process = multiprocessing.Process(target=start_server)
        self._process.start()
        time.sleep(0.5)

    def test_RPC(self):
        self.start_server()

        service = MessagingService()
        service.Ping()


if __name__ == '__main__':
    unittest.main()
