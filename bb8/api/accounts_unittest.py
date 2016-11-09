#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    unit testing for account api
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import unittest

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import accounts
from bb8.api.test_utils import BearerAuthTestClient
from bb8.backend.database import DatabaseManager, Account
from bb8.constant import HTTPStatus, CustomError


class AccountAPIUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()
        DatabaseManager.reset()

        app.test_client_class = BearerAuthTestClient
        self.app = app.test_client()
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def setup_prerequisite(self):
        Account(name=u'test',
                email='test@gmail.com').set_passwd('12345678').add()
        DatabaseManager.commit()

    def test_account(self):
        # Test for accessing login-only data, should fail
        rv = self.app.get('/api/me')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test for existing email
        rv = self.app.post('/api/email_register', data=json.dumps(dict(
            email='test@gmail.com',
            passwd='12345678',
            timezone='Asia/Taipei'
        )), content_type='application/json')
        data = json.loads(rv.data)
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)
        self.assertEquals(data['error_code'], CustomError.ERR_USER_EXISTED)

        # Test for invalid email
        rv = self.app.post('/api/email_register', data=json.dumps(dict(
            email='not-valid-email',
            passwd='12345678',
            timezone='Asia/Taipei'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test for invalid timezone
        rv = self.app.post('/api/email_register', data=json.dumps(dict(
            email='test-2@gmail.com',
            passwd='12345678',
            timezone='Not-A-Timezone'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test for successful register
        rv = self.app.post('/api/email_register', data=json.dumps(dict(
            email='test-2@gmail.com',
            passwd='12345678',
            timezone='Asia/Taipei'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Test for wrong password
        rv = self.app.post('/api/login', data=json.dumps(dict(
            email='test-2@gmail.com',
            passwd='87654321'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test for login
        rv = self.app.post('/api/login', data=json.dumps(dict(
            email='test-2@gmail.com',
            passwd='12345678'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.app.set_auth_token(data['auth_token'])

        # Test for accessing login-only data
        rv = self.app.get('/api/me')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['email'], 'test-2@gmail.com')


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
