#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API unittest
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from flask import g

from bb8 import app
from bb8.backend.module_api import (Config, IsVariable, Render, Resolve,
                                    TextPayload, LocationPayload)


class MockNode(object):
    def __init__(self, _id):
        self.id = _id  # pylint: disable=W0622


class ModuleAPIUnittest(unittest.TestCase):
    def test_Config(self):
        self.assertIsNotNone(Config('HTTP_ROOT'))

    def test_TextPayload(self):
        g.node = MockNode(1)
        self.assertEquals(TextPayload('test'),
                          {'message': {'text': 'test'}, 'node_id': 1})

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
            'node_id': 1
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


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
