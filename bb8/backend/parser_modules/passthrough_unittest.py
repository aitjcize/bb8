#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Passthrough module - Unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

import jsonschema

from bb8.backend.parser_modules import passthrough


class PassthroughUnittest(unittest.TestCase):
    def test_next(self):
        config = {
            'end_node_id': 0,
            'ack_message': 'ack'
        }
        jsonschema.validate(config, passthrough.schema())

        result = passthrough.run(
            config, None, False)
        self.assertEquals(result.action_ident, 'next')


if __name__ == '__main__':
    unittest.main()
