#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    unit testing for account api
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os
import json
import unittest
import tempfile

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import account
from bb8.constant import HTTPStatus, CustomError
from bb8.backend.database import DatabaseManager, Account


class AccountAPIUnittest(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True

        self.dbm = DatabaseManager()
        self.dbm.connect()
        self.dbm.reset()

        self.app = app.test_client()
        self.setup_prerequisite()

    def tearDown(self):
        self.dbm.disconnect()
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def setup_prerequisite(self):
        Account(name='test',
                username='test-account-1',
                email='test@gmail.com') \
            .set_passwd('12345678') \
            .add()
        self.dbm.commit()

    def test_account(self):
        # Test for accessing login-only data, should fail
        rv = self.app.get('/me')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test for existing email and username
        rv = self.app.post('/email_register', data=dict(
            email='test@gmail.com',
            username='test-account-1',
            passwd='12345678'
        ))
        data = json.loads(rv.data)
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)
        self.assertEquals(data['error_code'], CustomError.ERR_USER_EXISTED)

        # Test for successful register
        rv = self.app.post('/email_register', data=dict(
            email='test-2@gmail.com',
            username='test-account-2',
            passwd='12345678'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Test for wrong password
        rv = self.app.post('/login', data=dict(
            email='test-2@gmail.com',
            passwd='87654321'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test for login
        rv = self.app.post('/login', data=dict(
            email='test-2@gmail.com',
            passwd='12345678'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Test for accessing login-only data
        rv = self.app.get('/me')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['email'], 'test-2@gmail.com')


if __name__ == '__main__':
    unittest.main()
