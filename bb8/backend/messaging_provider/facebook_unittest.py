#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Facebook Messaging unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest
import datetime

from bb8.backend.database import DatabaseManager
from bb8.backend.database import Bot, Platform, PlatformTypeEnum, User
from bb8.backend.messaging import Message
from bb8.backend.messaging_provider import facebook


class FacebookMessagingUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()
        self.account = None
        self.bot = None
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def setup_prerequisite(self):
        DatabaseManager.reset()

        self.bot = Bot(name=u'test', description=u'test',
                       interaction_timeout=120, session_timeout=86400).add()
        DatabaseManager.commit()

        config = {
            'access_token': 'EAAP0okfsZCVkBAI3BCU5s3u8O0iVFh6NAwFHa7X2bKZCGQ'
                            'Lw6VYeTpeTsW5WODeDbekU3ZA0JyVCBSmXq8EqwL1GDuZBO'
                            '7aAlcNEHQ3AZBIx0ZBfFLh95TlJWlLrYetzm9owKNR8Qju8'
                            'HF6qra20ZC6HqNXwGpaP74knlNvQJqUmwZDZD'
        }
        platform = Platform(name=u'Test Platform',
                            bot_id=self.bot.id,
                            type_enum=PlatformTypeEnum.Facebook,
                            provider_ident='1155924351125985',
                            config=config).add()
        DatabaseManager.commit()

        self.user = User(platform_id=platform.id,
                         platform_user_ident='1153206858057166',
                         last_seen=datetime.datetime.now()).add()

        DatabaseManager.commit()

    def test_send_message(self):
        """Test facebook message sending."""

        # Test simple text message
        m = Message('test')
        facebook.send_message(self.user, [m])

        # Test image message
        m = Message(image_url='http://i.imgur.com/4loi6PJ.jpg')
        facebook.send_message(self.user, [m])

        # Test button template message
        m = Message(buttons_text='Button template test')
        m.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    'Google', url='http://www.google.com/'))
        m.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    '17', url='http://www.17.media/'))
        facebook.send_message(self.user, [m])

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

        facebook.send_message(self.user, [m])


if __name__ == '__main__':
    unittest.main()
