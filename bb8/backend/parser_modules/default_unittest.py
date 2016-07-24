#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Default Parser - Unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

import jsonschema

from bb8.backend.metadata import UserInput
from bb8.backend.parser_modules import default


class DefaultUnittest(unittest.TestCase):
    def test_rules(self):
        config = {
            'links': [{
                'rule': {
                    'type': 'regexp',
                    'params': [u'^action1-([0-9])$', u'action[23]-1'],
                },
                'action_ident': 'action1',
                'end_node_id': 0,
                'ack_message': 'action1 activated'
            }, {
                'rule': {
                    'type': 'regexp',
                    'params': [u'中(文|語)'],
                },
                'action_ident': 'action2',
                'end_node_id': 1,
                'ack_message': 'action2 activated'
            }, {
                'rule': {
                    'type': 'location',
                    'params': None
                },
                'action_ident': 'action3',
                'end_node_id': 2,
                'ack_message': 'action3 activated'
            }, {
                'rule': {
                    'type': 'event',
                    'params': ['TEST_EVENT']
                },
                'action_ident': 'event',
                'end_node_id': 3,
                'ack_message': 'event activated'
            }]
        }
        jsonschema.validate(config, default.schema())

        action, var, unused_data = default.run(
            config, UserInput.Text('action1-0'), False)
        self.assertEquals(action, 'action1')
        self.assertEquals(var['text'], 'action1-0')
        self.assertEquals(var['matches'], ('0',))

        action, var, unused_data = default.run(
            config, UserInput.Text('action2-1'), False)
        self.assertEquals(action, 'action1')
        self.assertEquals(var['text'], 'action2-1')
        self.assertEquals(var['matches'], ())

        action, var, unused_data = default.run(
            config, UserInput.Text(u'中文'), False)
        self.assertEquals(action, 'action2')
        self.assertEquals(var['text'], u'中文')
        self.assertEquals(var['matches'], (u'文',))

        action, unused_var, unused_data = default.run(
            config, UserInput.Location((25, 121)), False)
        self.assertEquals(action, 'action3')

        action, unused_var, unused_data = default.run(
            config, UserInput.Event('TEST_EVENT', 'event value'), False)
        self.assertEquals(action, 'event')


if __name__ == '__main__':
    unittest.main()
