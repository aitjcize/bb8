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
from bb8.api import accounts, bots, platforms
from bb8.constant import HTTPStatus, CustomError
from bb8.backend.platform_parser import get_platform_filename, parse_platform
from bb8.backend.database import DatabaseManager, Account
from bb8.backend.module_registration import register_all_modules


class PlatformAPIUnittest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        DatabaseManager.connect()
        DatabaseManager.reset()

        self.app = app.test_client()
        self.bot_ids = []
        self.platform_ids = []
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def login(self, acnt):
        rv = self.app.post('/api/login', data=dict(
            email=acnt.email,
            passwd='12345678'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

    def create_bot(self):
        # Test create bots
        rv = self.app.post('/api/bots', data=dict(
            name='test-bot',
            description='test-description',
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals('test-bot', data['name'])
        self.bot_ids.append(data['id'])

    def create_platform(self, platform_filename):
        # Test create platforms
        with open(get_platform_filename(platform_filename), 'r') as f:
            data = f.read()

        rv = self.app.post('/api/platforms', data=data,
                           content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['provider_ident'],
                          platform_filename.lstrip('dev/'))
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
        self.create_bot()
        self.create_platform('dev/bb8.test.platform')

        self.login(self.account2)
        self.create_bot()
        self.create_platform('dev/bb8.test2.platform')

        # Login back as account1
        self.login(self.account1)

    def test_platform_listing(self):
        """Test platform listing."""
        # Create a second platform
        self.create_platform('dev/bb8.test3.platform')

        # Test get all platforms
        rv = self.app.get('/api/platforms')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['platforms']), 2)
        self.assertEquals(data['platforms'][0]['id'], self.platform_ids[0])
        self.assertEquals(data['platforms'][1]['id'], self.platform_ids[2])

    def test_platform_create_get(self):
        """Test platform create and access.

        Also very that platform access permision is bound by account.
        """
        # Test get one platforms
        rv = self.app.get('/api/platforms/%d' % self.platform_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['provider_ident'], 'bb8.test.platform')
        self.assertEquals(data['config']['access_token'], 'access_token')

        # Test invalid platform_id
        rv = self.app.get('/api/platforms/9999999')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test invalid platform_id (platform own by account2)
        rv = self.app.get('/api/platforms/%s' % self.platform_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Login as account2, and should have access to the second platform
        self.login(self.account2)
        rv = self.app.get('/api/platforms/%s' % self.platform_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

    def test_platform_update(self):
        with open(get_platform_filename('dev/bb8.test3.platform'), 'r') as f:
            data = f.read()

        rv = self.app.put('/api/platforms/%d' % self.platform_ids[0],
                          data=data, content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        rv = self.app.get('/api/platforms/%d' % self.platform_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['provider_ident'], 'bb8.test3.platform')

    def test_platform_bot_binding(self):
        with open(get_platform_filename('dev/bb8.test.platform'), 'r') as f:
            input_data = json.load(f)

        # Bind platform1 with bot1
        input_data['bot_id'] = self.bot_ids[0]
        rv = self.app.put('/api/platforms/%d' % self.platform_ids[0],
                          data=json.dumps(input_data),
                          content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Check binding
        rv = self.app.get('/api/platforms/%d' % self.platform_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['bot_id'], self.bot_ids[0])

        # Try to bind account2's bot
        input_data['bot_id'] = self.bot_ids[1]
        rv = self.app.put('/api/platforms/%d' % self.platform_ids[0],
                          data=json.dumps(input_data),
                          content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

    def test_platform_deletion(self):
        # Test get all platforms
        rv = self.app.get('/api/platforms')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)

        # Delete the platform
        self.app.delete('/api/platforms/%d' % data['platforms'][0]['id'])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)

        # Make sure we don't have any platforms left
        rv = self.app.get('/api/platforms')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['platforms']), 0)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
