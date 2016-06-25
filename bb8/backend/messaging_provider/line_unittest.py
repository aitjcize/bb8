#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Line Messaging unittest
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest
import datetime

from bb8 import app
from bb8.backend.database import DatabaseManager
from bb8.backend.database import Bot, Platform, PlatformTypeEnum, User
from bb8.backend.messaging import Message
from bb8.backend.messaging_provider import line


class LineMessagingUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()
        self.account = None
        self.bot = None
        self.setup_prerequisite()

    def tearDown(self):
        self.dbm.disconnect()

    def setup_prerequisite(self):
        self.dbm.reset()

        self.bot = Bot(name=u'test', description=u'test',
                       interaction_timeout=120, session_timeout=86400).add()
        self.dbm.commit()

        config = {
            'channel_id': '1468633788',
            'channel_secret': '70a5bfd80b2cf26e387b83aa836fc884',
            'mid': 'u5526efbbc9c7ad1b3375c5102c276e68'
        }
        platform = Platform(bot_id=self.bot.id,
                            type_enum=PlatformTypeEnum.Line,
                            provider_ident='u5526efbbc9c7ad1b3375c5102c276e68',
                            config=config).add()
        self.dbm.commit()

        self.user = User(
            bot_id=self.bot.id,
            platform_id=platform.id,
            platform_user_ident='ua5afdc200e1fd44a748f6896376b9076',
            last_seen=datetime.datetime.now()).add()

        self.dbm.commit()

    def test_send_message(self):
        """Test line message sending."""

        # Test simple text message
        m = Message('test')
        line.send_message(self.user, [m])

        # Test image message
        m = Message(image_url='http://i.imgur.com/4loi6PJ.jpg')
        line.send_message(self.user, [m])

        # Test button template message
        m = Message()
        m.set_buttons_text('Button template test')
        m.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    'Google', url='http://www.google.com/'))
        m.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    '17', url='http://www.17.media/'))
        line.send_message(self.user, [m])

        # Test generic template message
        m = Message()
        bubble = Message.Bubble('Generic template test',
                                'http://www.starwars.com/',
                                'http://i.imgur.com/4loi6PJ.jpg',
                                'Bubble subtitle')
        bubble.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                         'Starwars',
                                         url='http://www.starwars.com/'))
        bubble.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                         'Google',
                                         url='http://www.google.com/'))
        bubble.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                         '17',
                                         url='http://www.17.media/'))
        m.add_bubble(bubble)
        m.add_bubble(bubble)
        m.add_bubble(bubble)

        line.send_message(self.user, [m])


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
