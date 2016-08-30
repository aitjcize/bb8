#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Message unittest
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import time
import unittest

import jsonschema
import pytz

from flask import g

from bb8 import app
from bb8.backend.database import (Bot, ColletedDatum, DatabaseManager,
                                  Platform, PlatformTypeEnum, User)
from bb8.backend.message import Message


class MessageUnittest(unittest.TestCase):
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

    def test_QuickReply(self):
        q1 = Message.QuickReply('quick_reply_1',
                                acceptable_inputs=['1', '2'])
        jsonschema.validate(q1.as_dict(), Message.QuickReply.schema())
        self.assertEquals(q1, q1.FromDict(q1.as_dict()))

        q2 = Message.QuickReply('quick_reply_2',
                                acceptable_inputs=['3', '4'])

        m = Message('test')
        m.add_quick_reply(q1)
        m.add_quick_reply(q2)

        jsonschema.validate(m.as_dict(), Message.schema())
        self.assertEquals(m, m.FromDict(m.as_dict()))

        transform_keys = reduce(lambda x, y: x + y,
                                [x[0] for x in g.input_transformation], [])
        self.assertTrue('quick_reply_1' in transform_keys)
        self.assertTrue('1' in transform_keys)
        self.assertTrue('3' in transform_keys)

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
        m = Message(buttons_text='question')
        m.add_button(but1)
        m.add_button(but2)
        jsonschema.validate(m.as_dict(), Message.schema())
        self.assertEquals(m, m.FromDict(m.as_dict()))

        transform_keys = reduce(lambda x, y: x + y,
                                [x[0] for x in g.input_transformation], [])
        self.assertTrue('^1$' not in transform_keys)
        self.assertTrue('^2$' in transform_keys)

        # Generic message
        g.input_transformation = []
        m = Message()
        m.add_bubble(b)
        m.add_bubble(b)
        jsonschema.validate(m.as_dict(), Message.schema())
        self.assertEquals(m, m.FromDict(m.as_dict()))

        transform_keys = reduce(lambda x, y: x + y,
                                [x[0] for x in g.input_transformation], [])
        self.assertTrue('^1-2$' in transform_keys)
        self.assertTrue('^2-2$' in transform_keys)

        with self.assertRaises(RuntimeError):
            m = Message('test', 'url')

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

        # Test error
        wrong_tmpl = 'Hi {{some.key}}'
        m = Message(wrong_tmpl)
        self.assertEquals(m.as_dict()['text'], wrong_tmpl)

    def test_query_expression_rendering(self):
        """Test that query expresssion can be query and rendered correctly."""
        ColletedDatum(user_id=self.user_1.id, key='data', value='value1').add()
        DatabaseManager.commit()
        time.sleep(1)
        ColletedDatum(user_id=self.user_1.id, key='data', value='value2').add()
        DatabaseManager.commit()
        time.sleep(1)
        ColletedDatum(user_id=self.user_1.id, key='data', value='value3').add()
        ColletedDatum(user_id=self.user_1.id, key='aaa', value='aaa').add()
        ColletedDatum(user_id=self.user_2.id, key='data', value='value4').add()
        DatabaseManager.commit()

        g.user = self.user_1
        m = Message('{{q.data|first|upper}}')
        self.assertEquals(m.as_dict()['text'], 'VALUE1')

        m = Message("{{q.data|get(1)}}")
        self.assertEquals(m.as_dict()['text'], 'value2')

        m = Message("{{q.data|last}}")
        self.assertEquals(m.as_dict()['text'], 'value3')

        m = Message("{{q.data|lru(0)}}")
        self.assertEquals(m.as_dict()['text'], 'value3')

        m = Message("{{q.data|lru(1)}}")
        self.assertEquals(m.as_dict()['text'], 'value2')

        m = Message("{{q.data|get(5)|fallback('valuef')}}")
        self.assertEquals(m.as_dict()['text'], 'valuef')

        m = Message("{{q.data|order_by('-created_at')|first}}")
        self.assertEquals(m.as_dict()['text'], 'value3')

        m = Message("{{q.data|count}}")
        self.assertEquals(m.as_dict()['text'], '3')

        m = Message("{{qall.data|count}}")
        self.assertEquals(m.as_dict()['text'], '4')

        # Test error
        wrong_tmpl = '{{q.data|some_filter}}'
        m = Message(wrong_tmpl)
        self.assertEquals(m.as_dict()['text'], wrong_tmpl)

        wrong_tmpl = '{{q.some_key|first}}'
        m = Message(wrong_tmpl)
        self.assertEquals(m.as_dict()['text'], wrong_tmpl)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()