#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Message unittest
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import time
import unittest

import jsonschema

from flask import g

from bb8 import app
from bb8.backend.database import CollectedDatum, DatabaseManager
from bb8.backend.message import (Message, TextPayload, LocationPayload,
                                 IsVariable, Resolve, Render)
from bb8.backend.test_utils import BaseTestMixin


class MockNode(object):
    def __init__(self, _id):
        self.id = _id  # pylint: disable=W0622
        self.stable_id = str(_id)


class MessageUnittest(unittest.TestCase, BaseTestMixin):
    def setUp(self):
        DatabaseManager.connect()
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_TextPayload(self):
        g.node = MockNode(1)
        self.assertEquals(TextPayload('test'),
                          {'message': {'text': 'test'}, 'node_id': '1'})

    def test_LocationPayload(self):
        g.node = MockNode(1)
        ans = {
            'message': {
                'attachments': [{
                    'type': 'location',
                    'payload': {
                        'coordinates': {
                            'lat': 1,
                            'long': 1
                        }
                    }
                }]
            },
            'node_id': '1'
        }
        self.assertEquals(LocationPayload((1, 1)), ans)

    def test_Render(self):
        # Basic rendering
        variables = {'target': 'Isaac', 'name': 'bb8', 'age': 100}
        text = Render('Hi {{target|upper}}, I am {{name}}. '
                      'I am {{age|inc|str}} years old.', variables)
        self.assertEquals(text, 'Hi ISAAC, I am bb8. I am 101 years old.')

        # "One-of" var rendering
        variables = {'target': {'name': 'Isaac'}}
        text = Render('Hi {{name,target.name|upper}}', variables)
        self.assertEquals(text, 'Hi ISAAC')

        variables = {'name': 'Isaac'}
        text = Render('Hi {{name,target.name|upper}}', variables)
        self.assertEquals(text, 'Hi ISAAC')

    def test_IsVariable(self):
        self.assertEquals(IsVariable("xx{{aaa}}"), False)
        self.assertEquals(IsVariable("{{aaa}}yy"), False)
        self.assertEquals(IsVariable("{{aaa}}"), True)

    def test_Resolve(self):
        variables = {'a': 'A'}
        self.assertEquals(Resolve('xx{{a}}', variables), 'xx{{a}}')
        self.assertEquals(Resolve('{{a}}', variables), 'A')

        variables = {'b': 'B'}
        self.assertEquals(Resolve('{{a,b}}', variables), 'B')
        self.assertEquals(Resolve('{{a,b}}', {}), '{{a,b}}')

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

        b = Message.Button(Message.ButtonType.ELEMENT_SHARE)
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
        q1 = Message.QuickReply(Message.QuickReplyType.TEXT, 'quick_reply_1',
                                acceptable_inputs=['1', '2'])
        jsonschema.validate(q1.as_dict(), Message.QuickReply.schema())
        self.assertEquals(q1, q1.FromDict(q1.as_dict()))

        q2 = Message.QuickReply(Message.QuickReplyType.LOCATION)
        jsonschema.validate(q2.as_dict(), Message.QuickReply.schema())
        self.assertEquals(q2, q2.FromDict(q2.as_dict()))

        q3 = Message.QuickReply(Message.QuickReplyType.TEXT, 'quick_reply_2',
                                acceptable_inputs=['3', '4'])

        m = Message('test')
        m.add_quick_reply(q1)
        m.add_quick_reply(q2)
        m.add_quick_reply(q3)

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
        CollectedDatum(user_id=self.user_1.id, key='data',
                       value='value1').add()
        DatabaseManager.commit()
        time.sleep(1)
        CollectedDatum(user_id=self.user_1.id, key='data',
                       value='value2').add()
        DatabaseManager.commit()
        time.sleep(1)
        CollectedDatum(user_id=self.user_1.id, key='data',
                       value='value3').add()
        CollectedDatum(user_id=self.user_1.id, key='aaa',
                       value='aaa').add()
        CollectedDatum(user_id=self.user_2.id, key='data',
                       value='value4').add()
        DatabaseManager.commit()

        g.user = self.user_1
        m = Message("{{data('data').first|upper}}")
        self.assertEquals(m.as_dict()['text'], 'VALUE1')

        m = Message("{{data('data').get(1)}}")
        self.assertEquals(m.as_dict()['text'], 'value2')

        m = Message("{{data('data').last}}")
        self.assertEquals(m.as_dict()['text'], 'value3')

        m = Message("{{data('data').lru(0)}}")
        self.assertEquals(m.as_dict()['text'], 'value3')

        m = Message("{{data('data').lru(1)}}")
        self.assertEquals(m.as_dict()['text'], 'value2')

        m = Message("{{data('data').get(5).fallback('valuef')}}")
        self.assertEquals(m.as_dict()['text'], 'valuef')

        m = Message("{{data('data').order_by('-created_at').first}}")
        self.assertEquals(m.as_dict()['text'], 'value3')

        m = Message("{{data('data').count}}")
        self.assertEquals(m.as_dict()['text'], '3')

        # Test error
        wrong_tmpl = "{{data('data')|some_filter}}"
        m = Message(wrong_tmpl)
        self.assertEquals(m.as_dict()['text'], wrong_tmpl)

        wrong_tmpl = "{{data('some_key').first}}"
        m = Message(wrong_tmpl)
        self.assertEquals(m.as_dict()['text'], wrong_tmpl)

    def test_settings_memory_rendering(self):
        """Test memory and setting variable access."""

        g.user = self.user_1
        g.user.settings['key1'] = 'value1'
        m = Message("{{settings.key1|upper}}")
        self.assertEquals(m.as_dict()['text'], 'VALUE1')

        g.user = self.user_1
        g.user.memory['key2'] = 'value2'
        m = Message("{{memory.key2|upper}}")
        self.assertEquals(m.as_dict()['text'], 'VALUE2')

    def test_input_transformation_reconstruction(self):
        """Test that input transformation is applied when constructing message
        with Message.FromDict."""

        msg_dict = {
            "text": "test",
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": "A",
                },
                {
                    "content_type": "text",
                    "title": "B"
                },
                {
                    "content_type": "location",
                }
            ]
        }

        g.input_transformation = []
        Message.FromDict(msg_dict)
        transform_keys = reduce(lambda x, y: x + y,
                                [x[0] for x in g.input_transformation], [])
        self.assertTrue('A' in transform_keys)
        self.assertTrue('B' in transform_keys)
        self.assertFalse(None in transform_keys)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
