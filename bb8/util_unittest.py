#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Util Unittest
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8 import util


class UtilUnittest(unittest.TestCase):
    def test_get_schema(self):
        """Test get_schema for all available schema file."""
        for name in ['app', 'bot', 'misc-resource']:
            util.get_schema(name)

        with self.assertRaises(Exception):
            util.get_schema('test/test')


if __name__ == '__main__':
    unittest.main()
