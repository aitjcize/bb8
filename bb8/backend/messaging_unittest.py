#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Messaging unittest
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest
import datetime

import jsonschema
import pytz

from bb8 import app
from bb8.backend.database import DatabaseManager
from bb8.backend.database import Bot, Platform, PlatformTypeEnum, User
from bb8.backend.messaging import Message, broadcast_message
from bb8.backend.messaging_provider import facebook


class MessageUnittest(unittest.TestCase):
    def test_Button(self):
        with self.assertRaises(RuntimeError):
            Message.Button('wrong_type', 'test', 'http://test.com')

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            b = Message.Button(Message.ButtonType.WEB_URL, 'test',
                               payload='payload')
            jsonschema.validate(b.as_dict(), Message.Button.schema())

        b = Message.Button(Message.ButtonType.WEB_URL, 'test',
                           url='http://test.com')
        jsonschema.validate(b.as_dict(), Message.Button.schema())
        self.assertEquals(b, b.FromDict(b.as_dict()))

        b = Message.Button(Message.ButtonType.POSTBACK, 'postback',
                           payload='postback')
        jsonschema.validate(b.as_dict(), Message.Button.schema())
        self.assertEquals(b, b.FromDict(b.as_dict()))

    def test_Bubble(self):
        b = Message.Bubble('title')
        jsonschema.validate(b.as_dict(), Message.Bubble.schema())
        self.assertEquals(b, b.FromDict(b.as_dict()))

        b = Message.Bubble('title', 'http://test.com/item_url',
                           'http://test.com/image_url', 'subtitle')
        jsonschema.validate(b.as_dict(), Message.Bubble.schema())
        self.assertEquals(b, b.FromDict(b.as_dict()))

        b.add_button(Message.Button(Message.ButtonType.WEB_URL, 'test',
                                    url='http://test.com'))
        b.add_button(Message.Button(Message.ButtonType.POSTBACK, 'test',
                                    payload='payload'))
        jsonschema.validate(b.as_dict(), Message.Bubble.schema())
        self.assertEquals(b, b.FromDict(b.as_dict()))

    def test_Message(self):
        but1 = Message.Button(Message.ButtonType.WEB_URL, 'test',
                              url='http://test.com')
        but2 = Message.Button(Message.ButtonType.POSTBACK, 'test',
                              payload='payload')
        b = Message.Bubble('title', 'http://test.com/item_url',
                           'http://test.com/image_url', 'subtitle')
        b.add_button(but1)
        b.add_button(but2)

        m = Message('test')
        jsonschema.validate(m.as_dict(), Message.schema())
        self.assertEquals(m, m.FromDict(m.as_dict()))

        m = Message(image_url='http://test.com/image_url')
        jsonschema.validate(m.as_dict(), Message.schema())
        self.assertEquals(m, m.FromDict(m.as_dict()))

        # Button message
        m = Message()
        m.set_buttons_text('question')
        m.add_button(but1)
        m.add_button(but2)
        jsonschema.validate(m.as_dict(), Message.schema())
        self.assertEquals(m, m.FromDict(m.as_dict()))

        # Generic message
        m = Message()
        m.add_bubble(b)
        m.add_bubble(b)
        jsonschema.validate(m.as_dict(), Message.schema())
        self.assertEquals(m, m.FromDict(m.as_dict()))

        with self.assertRaises(RuntimeError):
            m = Message('test', 'url')


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

    def test_message_variable_rendering(self):
        """Test that variable in message can be rendered correctly."""
        variables = {
            'user': {
                'first_name': 'Isaac',
                'last_name': 'Huang',
            },
            'date': 'today'
        }
        m = Message('Hi {{user.first_name}}', variables=variables)
        self.assertEquals(m.as_dict()['text'], 'Hi Isaac')

        m = Message()
        bubble = Message.Bubble('Bubble Test',
                                'http://www.starwars.com/',
                                'http://i.imgur.com/4loi6PJ.jpg',
                                '{{user.first_name}}', variables=variables)
        bubble.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                         '{{user.last_name}}',
                                         url='http://www.starwars.com/',
                                         variables=variables))
        m.add_bubble(bubble)
        bubble = m.as_dict()['attachment']['payload']['elements'][0]

        self.assertEquals(bubble['subtitle'], 'Isaac')
        self.assertEquals(bubble['buttons'][0]['title'], 'Huang')


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
