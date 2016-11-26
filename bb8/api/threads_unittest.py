#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for Thread API
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import json
import time
import unittest

import mock

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


class ThreadAPIUnittest(unittest.TestCase):
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

    def create_bot(self):
        rv = self.app.post('/api/bots', data=json.dumps(dict(
            name='test-bot',
            description='test-description',
        )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals('test-bot', data['name'])
        self.bot_ids.append(data['id'])

    def create_platform(self, platform_filename, bot_id):
        # Test create platforms
        with open(get_platform_filename(platform_filename), 'r') as f:
            data = json.load(f)

        data['bot_id'] = bot_id
        rv = self.app.post('/api/platforms', data=json.dumps(data),
                           content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['provider_ident'],
                          platform_filename.lstrip('dev/'))
        self.platform_ids.append(data['id'])

    def add_user(self, platform_id, ident):
        user = User(platform_id=platform_id,
                    platform_user_ident=ident,
                    last_seen=datetime.datetime.now()).add()
        DatabaseManager.commit()
        self.user_ids.append(user.id)

    def add_conversation(self, user_id, sender_enum, messages):
        Conversation(user_id=user_id, sender_enum=sender_enum,
                     messages=messages, timestamp=time.time()).add()

    def setup_prerequisite(self):
        register_all()

        self.account_user1 = AccountUser.register(dict(
            name=u'test', email='test@gmail.com', passwd='12345678'))
        self.account_user2 = AccountUser.register(dict(
            name=u'test2', email='test2@gmail.com', passwd='12345678'))
        DatabaseManager.commit()

        self.login(self.account_user1)
        self.create_bot()
        self.create_platform('dev/bb8.test.platform', self.bot_ids[0])
        # account-bot-platform-user
        self.add_user(self.platform_ids[0], '1-1-1-1')
        self.add_user(self.platform_ids[0], '1-1-1-2')
        self.create_platform('dev/bb8.test2.platform', self.bot_ids[0])
        self.add_user(self.platform_ids[1], '1-1-2-1')
        self.add_user(self.platform_ids[1], '1-1-2-2')

        self.create_bot()
        self.create_platform('dev/bb8.test3.platform', self.bot_ids[1])
        self.add_user(self.platform_ids[2], '2-1-2-1')
        self.add_user(self.platform_ids[2], '2-1-2-2')

        # Login as account2
        self.login(self.account_user2)
        self.create_bot()
        self.create_platform('dev/bb8.test4.platform', self.bot_ids[2])
        self.add_user(self.platform_ids[3], '2-1-2-1')
        self.add_user(self.platform_ids[3], '2-1-2-2')

        # Login back as account1
        self.login(self.account_user1)

    def test_thread_listing(self):
        """Test thread listing."""
        # Test get all threads for an account
        rv = self.app.get('/api/threads')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals([x['platform_user_ident'] for x in data['threads']],
                          [u'1-1-1-1', u'1-1-1-2', u'1-1-2-1', u'1-1-2-2',
                           u'2-1-2-1', u'2-1-2-2'])

        # Test get all threads for an account, filter by bot
        rv = self.app.get('/api/threads?filter=bot_id:%d' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals([x['platform_user_ident'] for x in data['threads']],
                          [u'1-1-1-1', u'1-1-1-2', u'1-1-2-1', u'1-1-2-2'])

        # Test get all threads for an account, filter by platform
        rv = self.app.get('/api/threads?filter=platform_id:%d' %
                          self.platform_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals([x['platform_user_ident'] for x in data['threads']],
                          [u'1-1-2-1', u'1-1-2-2'])

    def test_show_thread(self):
        """Test thread showing."""
        for i in range(50):
            self.add_conversation(
                self.user_ids[0],
                SenderEnum.User if i % 2 == 0 else SenderEnum.Bot,
                i + 1)

        for i in range(50):
            self.add_conversation(
                self.user_ids[4],
                SenderEnum.User if i % 2 == 0 else SenderEnum.Bot,
                i + 1)

        # No argumnet specified
        rv = self.app.get('/api/threads/%s' % self.user_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['conversation']), 30)

        # Specify limit and offset
        rv = self.app.get('/api/threads/%s?limit=10&offset=2' %
                          self.user_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['conversation']), 10)
        self.assertEquals(data['conversation'][0]['messages'], 48)

        # Specify limit, offset and last_id
        last_id = data['conversation'][-1]['id']
        rv = self.app.get('/api/threads/%s?limit=10&last_id=%d' %
                          (self.user_ids[0], last_id))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['conversation']), 10)
        self.assertEquals(data['conversation'][0]['id'], 38)

        # Access thread(user) owned by acccount2
        rv = self.app.get('/api/threads/%s' % self.user_ids[6])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

    def test_update_thread(self):
        """Test thread updating."""
        rv = self.app.patch('/api/threads/%s' % self.user_ids[0],
                            data=json.dumps(dict(
                                status='Assigned',
                                assignee=self.account_user1.id,
                                comment='Test comment',
                            )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        rv = self.app.patch('/api/threads/%s' % self.user_ids[0],
                            data=json.dumps(dict(
                                status='Assigned',
                                assignee=self.account_user2.id,
                                comment='Test comment',
                            )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

    @mock.patch('bb8.backend.messaging_provider.facebook.push_message')
    def test_post_thread(self, mock_push_message):
        """Test thread posting."""
        rv = self.app.post('/api/threads/%s' % self.user_ids[0],
                           data=json.dumps(dict(
                               message=Message('test').as_dict(),
                           )), content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        mock_push_message.assert_called_once()

        # Make sure the conversation is stored.
        rv = self.app.get('/api/threads/%s' % self.user_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['conversation']), 1)
        self.assertEquals(data['conversation'][0]['sender'],
                          self.account_user1.id)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
