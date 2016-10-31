#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Text message Unittest
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.content_modules import generic_message
from bb8.backend.module_api import SupportedPlatform


class GenericMessageUnittest(unittest.TestCase):
    def setUp(self):
        self.messages = [
            {
                'text': 'text'
            },
            {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'button',
                        'text': 'A',
                        'buttons': [
                            {
                                'type': 'web_url',
                                'title': 'button 1',
                                'url': 'http://example.com'
                            },
                            {
                                'type': 'web_url',
                                'title': 'button 2',
                                'url': 'http://example2.com'
                            }
                        ]
                    }
                }
            }
        ]

    def test_run_independent(self):
        # Test Platform independent
        content_config = {
            'messages': self.messages
        }
        env = {
            'platform_type': SupportedPlatform.Facebook
        }
        msgs = generic_message.run(content_config, env, {})
        self.assertEquals(msgs[0].as_dict()['text'], 'text')
        payload = msgs[1].as_dict()['attachment']['payload']
        self.assertEquals(payload['text'], 'A')
        self.assertEquals(payload['buttons'][0]['title'], 'button 1')

    def test_run_dependent(self):
        # Test Platform independent
        content_config = {
            'messages': {
                'Facebook': self.messages,
                'Line': self.messages
            }
        }
        env = {
            'platform_type': SupportedPlatform.Line
        }
        msgs = generic_message.run(content_config, env, {})
        self.assertEquals(msgs[0].as_dict()['text'], 'text')
        payload = msgs[1].as_dict()['attachment']['payload']
        self.assertEquals(payload['text'], 'A')
        self.assertEquals(payload['buttons'][0]['title'], 'button 1')


if __name__ == '__main__':
    unittest.main()
