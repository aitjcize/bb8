#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Get response from user - Unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

import jsonschema

from bb8.backend.metadata import UserInput
from bb8.backend.parser_modules import get_response


class GetResponseUnittest(unittest.TestCase):
    def test_text_only(self):
        config = {
            'type': 'text',
            'links': []
        }
        jsonschema.validate(config, get_response.schema())

        action, unused_var = get_response.run(config, UserInput.Text('text'))
        self.assertEquals(action, 'got_text')

        action, unused_var = get_response.run(config,
                                              UserInput.Location((25, 121)))
        self.assertEquals(action, 'no_text')

    def test_location_only(self):
        config = {
            'type': 'location',
            'links': []
        }
        jsonschema.validate(config, get_response.schema())

        action, unused_var = get_response.run(config,
                                              UserInput.Location((25, 121)))
        self.assertEquals(action, 'got_location')

        action, unused_var = get_response.run(config, UserInput.Text('text'))
        self.assertEquals(action, 'no_location')

    def test_all(self):
        config = {
            'type': 'all',
            'links': []
        }
        jsonschema.validate(config, get_response.schema())

        action, unused_var = get_response.run(config, UserInput.Text('text'))
        self.assertEquals(action, 'got_text')

        action, unused_var = get_response.run(config,
                                              UserInput.Location((25, 121)))
        self.assertEquals(action, 'got_location')

    def test_error(self):
        config = {
            'type': 'all',
            'links': []
        }
        jsonschema.validate(config, get_response.schema())

        action, unused_var = get_response.run(config, UserInput())
        self.assertEquals(action, '$error')


if __name__ == '__main__':
    unittest.main()
