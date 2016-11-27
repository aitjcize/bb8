#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for Label API
    ~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import unittest

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import accounts, bots, platforms
from bb8.api.test_utils import BearerAuthTestClient
from bb8.constant import HTTPStatus, CustomError
from bb8.backend.platform_parser import get_platform_filename, parse_platform
from bb8.backend.database import (DatabaseManager, AccountUser, User,
                                  SenderEnum, Conversation)
from bb8.backend.message import Message
from bb8.backend.modules import register_all


class LabelAPIUnittest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        DatabaseManager.connect()
        DatabaseManager.reset()

        app.test_client_class = BearerAuthTestClient
        self.app = app.test_client()
        self.bot_ids = []
        self.platform_ids = []
        self.user_ids = []
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
        register_all()

        self.account_user1 = AccountUser.register(dict(
            name=u'test', email='test@gmail.com', passwd='12345678'))
        self.account_user2 = AccountUser.register(dict(
            name=u'test2', email='test2@gmail.com', passwd='12345678'))
        DatabaseManager.commit()

        self.login(self.account_user1)

    def test_label_listing(self):
        """Test label listing."""
        # Test get all threads for an account
        rv = self.app.get('/api/labels')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['labels']), 0)

        # Add a new label
        rv = self.app.post('/api/labels',
                           data=json.dumps(dict(
                               name='Label1',
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Listing should contain one label
        rv = self.app.get('/api/labels')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['labels']), 1)

    def test_post_label(self):
        """Test label posting."""
        rv = self.app.post('/api/labels',
                           data=json.dumps(dict(
                               name='Label1',
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Duplicate entry
        rv = self.app.post('/api/labels',
                           data=json.dumps(dict(
                               name='Label1',
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Login with account2 and add label with the same name
        self.login(self.account_user2)
        rv = self.app.post('/api/labels',
                           data=json.dumps(dict(
                               name='Label1',
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
