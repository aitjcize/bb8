#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API unittest
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8 import app
from bb8.backend.module_api import Config


class ModuleAPIUnittest(unittest.TestCase):
    def test_Config(self):
        self.assertIsNotNone(Config('HTTP_ROOT'))


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
