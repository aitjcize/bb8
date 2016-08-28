#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Messaging unittest
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import unittest

import pytz

from bb8.backend.database import (Bot, DatabaseManager, Platform,
                                  PlatformTypeEnum, User)
from bb8.backend import messaging
from bb8.backend.message_format import Message


class MessagingUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()
        self.setup_prerequisite()

    def tearDown(self):
        self.dbm.disconnect()

    def setup_prerequisite(self):
        self.dbm.reset()

        self.bot = Bot(name=u'test', description=u'test',
                       interaction_timeout=120, session_timeout=86400).add()
        self.dbm.commit()

        self.platform = Platform(bot_id=self.bot.id,
                                 type_enum=PlatformTypeEnum.Facebook,
                                 provider_ident='facebook_page_id',
                                 config={}).add()
        self.dbm.commit()

        self.user_1 = User(bot_id=self.bot.id,
                           platform_id=self.platform.id,
                           platform_user_ident='1153206858057166',
                           last_seen=datetime.datetime(2016, 6, 2, 12, 44, 56,
                                                       tzinfo=pytz.utc)).add()
        self.user_2 = User(bot_id=self.bot.id,
                           platform_id=self.platform.id,
                           platform_user_ident='1318395614844436',
                           last_seen=datetime.datetime(2016, 6, 2, 12, 44, 56,
                                                       tzinfo=pytz.utc)).add()
        self.dbm.commit()

    def test_broadcast_message(self):
        """Test facebook message sending."""
        # Test card message
        m = Message('Message test')

        context = {}
        context['count'] = 0

        def send_message_mock(unused_user, unused_messages):
            context['count'] += 1

        messaging.send_message = send_message_mock
        messaging.broadcast_message(self.bot, [m, m])

        self.assertEquals(context['count'], 2)


if __name__ == '__main__':
    unittest.main()
