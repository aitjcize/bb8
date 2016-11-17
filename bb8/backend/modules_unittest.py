#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for Modules
    ~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8 import app
from bb8.backend import modules


class ModuleRegistrationUnittest(unittest.TestCase):
    def test_register_modules(self):
        modules.register_all()


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
