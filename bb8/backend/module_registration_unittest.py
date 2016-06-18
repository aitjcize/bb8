#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for testing module registration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend import module_registration


class ModuleRegistrationUnittest(unittest.TestCase):
    def test_register_content_modules(self):
        module_registration.register_content_modules()

    def test_register_parser_modules(self):
        module_registration.register_parser_modules()


if __name__ == '__main__':
    unittest.main()
