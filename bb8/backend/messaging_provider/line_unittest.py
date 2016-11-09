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
from bb8.backend.message import Message
from bb8.backend.messaging_provider import line


class LineMessagingUnittest(unittest.TestCase):
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
            'access_token': 'iHRMgmp3zRLOc6kPCbPNMwEDHyFqLGSy0tyG3uZxnkNlhMKg'
                            '8GVFqMGslcOkmgOAFLlBvvYuXmKF9odhXtsCm3tBxRcPryKr'
                            'kOvzHBcBvS2zrVGiVmZGh5EBcqazgurYMwVSdgNSrhCm/qp6'
                            '2aR7HAdB04t89/1O/w1cDnyilFU=',
            'channel_secret': '335c901df3a1969ca28a48bf6ddcc333'
        }
        platform = Platform(bot_id=self.bot.id,
                            name=u'Line',
                            type_enum=PlatformTypeEnum.Line,
                            provider_ident='aitjcize.line',
                            config=config).add()
        DatabaseManager.commit()

        self.user = User(
            platform_id=platform.id,
            platform_user_ident='U7200f33369e7e586c973c3a9df8feee4',
            last_seen=datetime.datetime.now()).add()

        DatabaseManager.commit()

    def test_send_message(self):
        """Test line message sending."""

        # Test simple text message
        m = Message('test')
        line.push_message(self.user, [m])

        # Test image message
        m = Message(image_url='http://i.imgur.com/4loi6PJ.jpg')
        line.push_message(self.user, [m])

        # Test button template message
        m = Message(buttons_text='Button template test')
        m.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    'Google', url='http://www.google.com/'))
        m.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    '17', url='http://www.17.media/'))
        line.push_message(self.user, [m])

        # Test list template message
        m = Message(top_element_style=Message.ListTopElementStyle.LARGE)
        l = Message.ListItem('Google', 'google.com',
                             'http://i.imgur.com/1QfaG1u.png')
        l.set_default_action(Message.Button(Message.ButtonType.WEB_URL,
                                            url='http://www.google.com'))
        l.set_button(Message.Button(Message.ButtonType.WEB_URL,
                                    title='Goto Google',
                                    url='http://www.google.com/'))
        m.add_list_item(l)
        l = Message.ListItem('17', 'http://www.17.media/',
                             'http://i.imgur.com/4loi6PJ.jpg')
        l.set_button(Message.Button(Message.ButtonType.WEB_URL,
                                    title='Goto 17',
                                    url='http://www.17.media/'))
        m.add_list_item(l)
        m.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                    '17', url='http://www.17.media/'))

        line.push_message(self.user, [m])

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

        line.push_message(self.user, [m])


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
