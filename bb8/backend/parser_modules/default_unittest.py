#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Default Parser - Unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

import jsonschema

from flask import g

from bb8 import app
from bb8.backend.database import DatabaseManager
from bb8.backend.metadata import UserInput
from bb8.backend.parser_modules import default
from bb8.backend.test_utils import BaseMessagingMixin


class DefaultUnittest(unittest.TestCase, BaseMessagingMixin):
    def setUp(self):
        DatabaseManager.connect()
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_rules(self):
        config = {
            'links': [{
                'rule': {
                    'type': 'regexp',
                    'params': [u'^action1-([0-9])$', u'action[23]-1'],
                    'collect_as': {'key': 'action'},
                    'memory_set': {'key': 'action'},
                    'settings_set': {'key': 'action'}
                },
                'end_node_id': 'Node1',
                'ack_message': 'action1 activated'
            }, {
                'rule': {
                    'type': 'regexp',
                    'params': [u'中(文|語)'],
                    'collect_as': {'key': 'group', 'value': '{{matches#1}}'},
                    'memory_set': {'key': 'group', 'value': '{{matches#1}}'},
                    'settings_set': {'key': 'group', 'value': '{{matches#1}}'}
                },
                'end_node_id': 'Node2',
                'ack_message': 'action2 activated'
            }, {
                'rule': {
                    'type': 'regexp',
                    'params': [u'action3'],
                },
                'ack_message': 'reply by parser'
            }, {
                'rule': {
                    'type': 'location',
                    'params': None
                },
                'end_node_id': 'Node3',
                'ack_message': 'action4 activated'
            }, {
                'rule': {
                    'type': 'event',
                    'params': ['TEST_EVENT']
                },
                'end_node_id': 'Node4',
                'ack_message': 'event activated'
            }]
        }
        jsonschema.validate(config, default.schema())

        g.user = self.user_1
        result = default.run(config, UserInput.Text('action1-0'), False)
        self.assertEquals(result.end_node_id, 'Node1')
        self.assertEquals(result.ack_message, 'action1 activated')
        self.assertEquals(result.variables['text'], 'action1-0')
        self.assertEquals(result.variables['matches'], ['action1-0', '0'])
        self.assertEquals(result.collected_datum['action'], 'action1-0')
        self.assertEquals(self.user_1.memory['action'], 'action1-0')
        self.assertEquals(self.user_1.settings['action'], 'action1-0')

        result = default.run(config, UserInput.Text('action2-1'), False)
        self.assertEquals(result.end_node_id, 'Node1')
        self.assertEquals(result.ack_message, 'action1 activated')
        self.assertEquals(result.variables['text'], 'action2-1')
        self.assertEquals(result.variables['matches'], ['action2-1'])

        result = default.run(config, UserInput.Text(u'中文'), False)
        self.assertEquals(result.end_node_id, 'Node2')
        self.assertEquals(result.ack_message, 'action2 activated')
        self.assertEquals(result.variables['text'], u'中文')
        self.assertEquals(result.variables['matches'], [u'中文', u'文'])
        self.assertEquals(result.collected_datum['group'], u'文')
        self.assertEquals(self.user_1.memory['group'], u'文')
        self.assertEquals(self.user_1.settings['group'], u'文')

        result = default.run(config, UserInput.Text(u'action3'), False)
        self.assertEquals(result.end_node_id, None)
        self.assertEquals(result.ack_message, 'reply by parser')
        self.assertEquals(result.variables['text'], u'action3')

        result = default.run(config, UserInput.Location((25, 121)), False)
        self.assertEquals(result.end_node_id, 'Node3')

        result = default.run(
            config, UserInput.Event('TEST_EVENT', 'event value'), False)
        self.assertEquals(result.end_node_id, 'Node4')


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
