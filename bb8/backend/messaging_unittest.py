#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Messaging unittest
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.database import DatabaseManager
from bb8.backend.database import Bot, Platform, PlatformTypeEnum, User
from bb8.backend.messaging import Message, broadcast_message
from bb8.backend.messaging_provider import facebook


class MessageUnittest(unittest.TestCase):
    def test_Button(self):
        with self.assertRaises(RuntimeError):
            Message.Button('wrong_type', 'test', 'http://test.com')

        b = Message.Button(Message.ButtonType.WEB_URL, 'test',
                           url='http://test.com')
        self.assertEquals(str(b), '{"url": "http://test.com", "type": '
                                  '"web_url", "title": "test"}')

    def test_Bubble(self):
        b = Message.Bubble('title')
        self.assertEquals(str(b), '{"title": "title"}')

        b = Message.Bubble('title', 'http://test.com/item_url',
                           'http://test.com/image_url', 'subtitle')
        self.assertEquals(str(b), '{"subtitle": "subtitle", "item_url": '
                          '"http://test.com/item_url", "image_url": '
                          '"http://test.com/image_url", "title": "title"}')
        b.add_button(Message.Button(Message.ButtonType.WEB_URL, 'test',
                                    url='http://test.com'))
        b.add_button(Message.Button(Message.ButtonType.POSTBACK, 'test',
                                    payload='payload'))
        self.assertEquals(str(b), '{"buttons": [{"url": "http://test.com", '
                          '"type": "web_url", "title": "test"}, '
                          '{"postback": "payload", "type": '
                          '"postback", "title": "test"}], '
                          '"subtitle": "subtitle", "item_url": '
                          '"http://test.com/item_url", "image_url": '
                          '"http://test.com/image_url", "title": "title"}')

    def test_Message(self):
        b = Message.Bubble('title', 'http://test.com/item_url',
                           'http://test.com/image_url', 'subtitle')
        b.add_button(Message.Button(Message.ButtonType.WEB_URL, 'test',
                                    url='http://test.com'))
        b.add_button(Message.Button(Message.ButtonType.POSTBACK, 'test',
                                    payload='payload'))

        m = Message('test')
        self.assertEquals(str(m), '{"text": "test"}')

        m = Message(image_url='http://test.com/image_url')
        self.assertEquals(str(m), '{"attachment": {"type": "image", "payload":'
                          ' {"url": "http://test.com/image_url"}}}')

        m = Message()
        m.add_bubble(b)
        self.assertEquals(str(m), '{"attachment": {"type": "template", '
                          '"payload": {"template_type": "generic", "elements":'
                          ' [{"buttons": [{"url": "http://test.com", "type": '
                          '"web_url", "title": "test"}, {"postback": '
                          '"payload", "type": "postback", "title": "test"}], '
                          '"subtitle": "subtitle", '
                          '"item_url": "http://test.com/item_url", '
                          '"image_url": "http://test.com/image_url", '
                          '"title": "title"}]}}}')

        with self.assertRaises(RuntimeError):
            m = Message('test', 'url')


class MessagingUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()
        self.account = None
        self.bot = None
        self.platform = None
        self.setup_prerequisite()

    def tearDown(self):
        self.dbm.disconnect()

    def setup_prerequisite(self):
        self.dbm.reset()

        self.bot = Bot(name='test', description='test',
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
                           last_seen=1464871496).add()
        self.user_2 = User(bot_id=self.bot.id,
                           platform_id=self.platform.id,
                           platform_user_ident='1318395614844436',
                           last_seen=1464871496).add()
        self.dbm.commit()

    def test_broadcast_message(self):
        """Test facebook message sending."""
        # Test card message
        m = Message()
        bubble = Message.Bubble('Bubble Test',
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

        context = {}
        context['count'] = 0

        def send_message_mock(unused_user, unused_messages):
            context['count'] += 1

        facebook.send_message = send_message_mock
        broadcast_message(self.bot, [m, m])

        self.assertEquals(context['count'], 2)


if __name__ == '__main__':
    unittest.main()
