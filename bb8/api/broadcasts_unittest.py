#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for Broadcast API
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import time
import unittest

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import accounts, bots, broadcasts
from bb8.api.test_utils import BearerAuthTestClient
from bb8.backend.database import (DatabaseManager, Account, Broadcast,
                                  BroadcastStatusEnum)
from bb8.backend.message import Message
from bb8.backend.modules import register_all_modules
from bb8.constant import HTTPStatus, CustomError


class BroadcastAPIUnittest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        DatabaseManager.connect()
        DatabaseManager.reset()

        app.test_client_class = BearerAuthTestClient
        self.app = app.test_client()
        self.bot_ids = []
        self.broadcast_ids = []
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

    def create_bot(self):
        rv = self.app.post('/api/bots', data=json.dumps(dict(
            name='test-bot',
            description='test-description',
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals('test-bot', data['name'])
        self.bot_ids.append(data['id'])

    def create_broadcast(self, bot_id, eta=int(time.time())):
        # Test create broadcasts
        input_data = {
            'bot_id': bot_id,
            'name': 'New broadcast',
            'messages': [Message('Test message').as_dict()],
            'scheduled_time': eta,
        }

        rv = self.app.post('/api/broadcasts', data=json.dumps(input_data),
                           content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['name'], input_data['name'])
        self.assertEquals(data['status'], 'Queued')
        self.broadcast_ids.append(data['id'])

    def setup_prerequisite(self):
        register_all_modules()

        self.account1 = Account(
            name=u'test',
            email='test@gmail.com').set_passwd('12345678').add()
        self.account2 = Account(
            name=u'test2',
            email='test2@gmail.com').set_passwd('12345678').add()
        DatabaseManager.commit()

        self.login(self.account1)
        self.create_bot()
        self.create_broadcast(self.bot_ids[0])

        self.login(self.account2)
        self.create_bot()
        self.create_broadcast(self.bot_ids[1])

        # Login back as account1
        self.login(self.account1)

    def test_broadcast_listing(self):
        """Test broadcast listing."""
        # Create a second broadcast
        self.create_broadcast(self.bot_ids[0])

        # Test get all broadcasts
        rv = self.app.get('/api/broadcasts')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['broadcasts']), 2)

    def test_broadcast_create_get(self):
        """Test broadcast create and access.

        Also very that broadcast access permision is bound by account.
        """
        # Create an invalid broadcast
        input_data = {
            'bot_id': self.bot_ids[0],
            'name': 'New broadcast',
            'messages': [{'some_invalid': 'format'}],
            'scheduled_time': int(time.time()),
        }

        rv = self.app.post('/api/broadcasts', data=json.dumps(input_data),
                           content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Create an invalid broadcast targeting bot own by account2
        input_data = {
            'bot_id': self.bot_ids[1],
            'name': 'New broadcast',
            'messages': [Message('test').as_dict()],
            'scheduled_time': int(time.time()),
        }

        rv = self.app.post('/api/broadcasts', data=json.dumps(input_data),
                           content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test get one broadcasts
        rv = self.app.get('/api/broadcasts/%d' % self.broadcast_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['name'], 'New broadcast')

        # Test invalid broadcast_id
        rv = self.app.get('/api/broadcasts/9999999')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test invalid broadcast_id (broadcast own by account2)
        rv = self.app.get('/api/broadcasts/%s' % self.broadcast_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Login as account2, and should have access to the second broadcast
        self.login(self.account2)
        rv = self.app.get('/api/broadcasts/%s' % self.broadcast_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Test sending immediately (scheduled_time = 0)
        self.create_broadcast(self.bot_ids[1], eta=0)

    def test_broadcast_update(self):
        # Test get all broadcasts
        rv = self.app.get('/api/broadcasts')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)

        broadcast_id = data['broadcasts'][0]['id']

        # Test invalid status update, status can only be 'Canceled'
        input_data = {
            'bot_id': self.bot_ids[0],
            'name': 'New broadcast',
            'messages': [Message('1234').as_dict()],
            'scheduled_time': int(time.time()),
            'status': 'Queued'
        }
        rv = self.app.put('/api/broadcasts/%d' % broadcast_id,
                          data=json.dumps(input_data),
                          content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test broadcast cancelation
        input_data = {
            'bot_id': self.bot_ids[0],
            'name': 'New broadcast',
            'messages': [Message('1234').as_dict()],
            'scheduled_time': int(time.time()),
            'status': 'Canceled'
        }
        rv = self.app.put('/api/broadcasts/%d' % broadcast_id,
                          data=json.dumps(input_data),
                          content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        rv = self.app.get('/api/broadcasts/%d' % broadcast_id)
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['messages'][0]['text'], '1234')

        # Broadcast is canceled, should be unmodifiable
        input_data = {
            'bot_id': self.bot_ids[0],
            'name': 'New broadcast 2',
            'messages': [Message('1234').as_dict()],
            'scheduled_time': int(time.time()),
        }
        rv = self.app.put('/api/broadcasts/%d' % broadcast_id,
                          data=json.dumps(input_data),
                          content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

    def test_broadcast_deletion(self):
        # Test get all broadcasts
        rv = self.app.get('/api/broadcasts')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)

        broadcast_id = data['broadcasts'][0]['id']

        # Set broadcast status to SENT
        b = Broadcast.get_by(id=broadcast_id, single=True)
        b.status = BroadcastStatusEnum.SENT
        DatabaseManager.commit()

        # Delete the broadcast (should fail becuase it's sent already)
        rv = self.app.delete('/api/broadcasts/%d' % broadcast_id)
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)
        data = json.loads(rv.data)

        # Set broadcast status back to QUEUED
        b2 = Broadcast.get_by(id=broadcast_id, single=True)
        b2.status = BroadcastStatusEnum.QUEUED
        DatabaseManager.commit()

        # Delete the broadcast
        rv = self.app.delete('/api/broadcasts/%d' % broadcast_id)
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)

        # Make sure we don't have any broadcasts left
        rv = self.app.get('/api/broadcasts')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['broadcasts']), 0)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
