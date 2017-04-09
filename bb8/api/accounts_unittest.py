#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    unit testing for account api
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import unittest

import mock

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import accounts
from bb8.api.test_utils import BearerAuthTestClient
from bb8.backend.database import DatabaseManager, Account, AccountUser
from bb8.constant import HTTPStatus, CustomError


class AccountUserAPIUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()
        DatabaseManager.reset()

        app.test_client_class = BearerAuthTestClient
        self.app = app.test_client()
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def login(self, acnt):
        rv = self.app.post('/api/login', data=json.dumps(dict(
            email=acnt.email,
            passwd='12345678'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.app.set_auth_token(data['auth_token'])

    def setup_prerequisite(self):
        self.account = Account(name=u'test').add()
        AccountUser(name=u'test', email='test@gmail.com',
                    account=self.account).set_passwd('12345678').add()
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

        # Test register with org invite but bad user email
        invite_code = self.account.invite_code('test-3@gmail.com')
        rv = self.app.post('/api/email_register?invite=%s' % invite_code,
                           data=json.dumps(dict(
                               email='test-4@gmail.com',
                               passwd='12345678',
                               timezone='Asia/Taipei'
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test register with org invite
        self.login(AccountUser.get_by(email='test@gmail.com', single=True))
        rv = self.app.post('/api/invite_code',
                           data=json.dumps(dict(email='test-3@gmail.com')),
                           content_type='application/json')
        invite_code = json.loads(rv.data)['invite_code']

        rv = self.app.post('/api/email_register?invite=%s' % invite_code,
                           data=json.dumps(dict(
                               email='test-3@gmail.com',
                               passwd='12345678',
                               timezone='Asia/Taipei'
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        user = AccountUser.get_by(email='test-3@gmail.com', single=True)
        self.assertEquals(self.account.id, user.account_id)

    @mock.patch('bb8.backend.oauth.facebook_verify_token')
    def test_social_auth(self, mock_facebook_verify_token):
        # Test social_auth
        # XXX: temporarily disable social auth without invite
        # mock_facebook_verify_token.return_value = '00000000'
        # rv = self.app.post('/api/social_auth',
        #                    data=json.dumps(dict(
        #                        email='test-1@gmail.com',
        #                        provider='Facebook',
        #                        provider_token='token',
        #                    )), content_type='application/json')
        # self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Test social_auth with org invite, wrong invite code email
        mock_facebook_verify_token.return_value = '11111111'
        invite_code = self.account.invite_code('test-2@gmail.com')
        rv = self.app.post('/api/social_auth?invite=%s' % invite_code,
                           data=json.dumps(dict(
                               email='test-20@gmail.com',
                               provider='Facebook',
                               provider_token='token',
                               invite_code=invite_code
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test social_auth with org invite
        mock_facebook_verify_token.return_value = '22222222'
        invite_code = self.account.invite_code('test-2@gmail.com')
        rv = self.app.post('/api/social_auth',
                           data=json.dumps(dict(
                               email='test-2@gmail.com',
                               provider='Facebook',
                               provider_token='token',
                               invite_code=invite_code
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        user = AccountUser.get_by(email='test-2@gmail.com', single=True)
        self.assertEquals(self.account.id, user.account_id)

    def test_account_login(self):
        # Test for wrong password
        rv = self.app.post('/api/login', data=json.dumps(dict(
            email='test@gmail.com',
            passwd='87654321'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test for login
        rv = self.app.post('/api/login', data=json.dumps(dict(
            email='test@gmail.com',
            passwd='12345678'
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.app.set_auth_token(data['auth_token'])

        # Test for accessing login-only data
        rv = self.app.get('/api/me')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['email'], 'test@gmail.com')


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
