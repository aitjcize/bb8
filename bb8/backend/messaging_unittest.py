#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Messaging unittest
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

import mock

from bb8.backend.database import DatabaseManager
from bb8.backend import messaging
from bb8.backend.message import Message
from bb8.backend.test_utils import BaseMessagingMixin


class MessagingUnittest(unittest.TestCase, BaseMessagingMixin):
    def setUp(self):
        DatabaseManager.connect()
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_send_message(self):
        """Test message sending."""
        m = Message('Message test')

        target = 'bb8.backend.messaging_provider.facebook.send_message'
        with mock.patch(target) as mock_send_message:
            messaging.send_message(self.user_1, [m, m])
            mock_send_message.assert_called_once_with(self.user_1, [m, m])

    def test_broadcast_message(self):
        # Test card message
        m = Message('Message test')

        target = 'bb8.backend.messaging.send_message_async'
        with mock.patch(target) as mock_send_message:
            messaging.broadcast_message(self.bot, [m, m])
            self.assertEquals(mock_send_message.call_count, 2)


if __name__ == '__main__':
    unittest.main()
