#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API unittest
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import time
import unittest

from flask import g

from bb8 import app
from bb8.backend.database import DatabaseManager, CollectedDatum
from bb8.backend.module_api import Config, CollectedData
from bb8.backend.test_utils import BaseTestMixin


class ModuleAPIUnittest(unittest.TestCase, BaseTestMixin):
    def setUp(self):
        DatabaseManager.connect()
        DatabaseManager.reset()
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_Config(self):
        self.assertIsNotNone(Config('HTTP_ROOT'))

    def test_CollectedData_API(self):
        for i in range(3):
            CollectedDatum(user_id=self.user_1.id,
                           key='K', value='V%d' % i).add()
            time.sleep(1)
            DatabaseManager.commit()

        g.user = self.user_1
        self.assertEquals(CollectedData.GetLast('K'), 'V2')
        self.assertEquals(CollectedData.Get('K', 3), ['V2', 'V1', 'V0'])
        self.assertEquals(CollectedData.Get('K', 2, 1), ['V1', 'V0'])

        # pylint: disable=W0212
        for i in range(CollectedData._MAX_RETURN_RESULTS + 10):
            CollectedDatum(user_id=self.user_2.id,
                           key='K', value='V%d' % i).add()
        DatabaseManager.commit()

        g.user = self.user_2
        self.assertEquals(len(CollectedData.Get('K', 110)), 100)
        self.assertEquals(CollectedData.Count('K'), 110)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
