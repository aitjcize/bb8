#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for Platform API
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import unittest

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import accounts, platforms
from bb8.constant import HTTPStatus, CustomError
from bb8.backend.platform_parser import get_platform_filename, parse_platform
from bb8.backend.database import DatabaseManager, Account
from bb8.backend.module_registration import register_all_modules


class BotAPIUnittest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        DatabaseManager.connect()
        DatabaseManager.reset()

        self.app = app.test_client()
        self.platform_ids = []
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def login(self, acnt):
        rv = self.app.post('/login', data=dict(
            email=acnt.email,
            passwd='12345678'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

    def create_platform(self):
        # Test create bots
        with open(get_platform_filename('dev/bb8.test.platform'), 'r') as f:
            data = f.read()

        rv = self.app.post('/platforms', data=data,
                           content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals('bb8 unittest fake platform', data['name'])
        self.platform_ids.append(data['id'])

    def setup_prerequisite(self):
        register_all_modules()

        self.account1 = Account(
            name=u'test', username='test-account-1',
            email='test@gmail.com').set_passwd('12345678').add()
        self.account2 = Account(
            name=u'test2', username='test-account-2',
            email='test2@gmail.com').set_passwd('12345678').add()
        DatabaseManager.commit()

        self.login(self.account1)
        self.create_platform()

        self.login(self.account2)
        self.create_platform()

        # Login back as account1
        self.login(self.account1)

    def test_bot_listing(self):
        """Test bot listing."""
        # Create a second bot
        self.create_bot()

        # Test get all bots
        rv = self.app.get('/bots')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['bots']), 2)

    def test_create_get_bot(self):
        """Test bot create and access.

        Also very that bot access permision is bound by account.
        """
        # Test get one bots
        rv = self.app.get('/platforms/%d' % self.platform_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['name'], 'test-bot')

        # Test invalid bot_id
        rv = self.app.get('/platforms/9999999')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test invalid bot_id (bot owned by account2
        rv = self.app.get('/platforms/%s' % self.platform_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Login as account2, and should have access to the second bot
        self.login(self.account2)
        rv = self.app.get('/platforms/%s' % self.platform_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
