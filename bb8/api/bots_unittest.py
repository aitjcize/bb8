#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for Bot API
    ~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import unittest

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import accounts, bots
from bb8.api.test_utils import BearerAuthTestClient
from bb8.constant import HTTPStatus, CustomError
from bb8.backend import account
from bb8.backend.bot_parser import get_bot_filename, parse_bot_from_file
from bb8.backend.database import DatabaseManager, AccountUser
from bb8.backend.modules import register_all


class BotAPIUnittest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        DatabaseManager.connect()
        DatabaseManager.reset()

        app.test_client_class = BearerAuthTestClient
        self.app = app.test_client()
        self.bot_ids = []
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

    def setup_prerequisite(self):
        register_all()

        self.account_user1 = account.register(dict(
            name=u'test', email='test@gmail.com', passwd='12345678'))
        self.account_user2 = account.register(dict(
            name=u'test2', email='test2@gmail.com', passwd='12345678'))
        DatabaseManager.commit()

        self.login(self.account_user1)
        self.create_bot()

        self.login(self.account_user2)
        self.create_bot()

        # Login back as account1
        self.login(self.account_user1)

    def test_bot_listing(self):
        """Test bot listing."""
        # Create a second bot
        self.create_bot()

        # Test get all bots
        rv = self.app.get('/api/bots')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['bots']), 2)

    def test_bot_create_get(self):
        """Test bot create and access.

        Also very that bot access permision is bound by account.
        """
        # Test get one bots
        rv = self.app.get('/api/bots/%d' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['name'], 'test-bot')
        self.assertTrue('staging' in data)

        # Test invalid bot_id
        rv = self.app.get('/api/bots/9999999')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test invalid bot_id (bot own by account2)
        rv = self.app.get('/api/bots/%s' % self.bot_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Login as account2, and should have access to the second bot
        self.login(self.account_user2)
        rv = self.app.get('/api/bots/%s' % self.bot_ids[1])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

    def test_bot_revisions(self):
        # Test update_bot with new bot definition
        bot_file = get_bot_filename('test/bot_fmt_test.bot')
        with open(bot_file, 'r') as f:
            bot_json_text = f.read()

        # Modify the staging area
        rv = self.app.patch('/api/bots/%d' % self.bot_ids[0],
                            data=bot_json_text,
                            content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Commit the bot
        rv = self.app.put('/api/bots/%d' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['version'], 1)

        # Test schema validation
        rv = self.app.patch('/api/bots/%d' % self.bot_ids[0],
                            data='{"test": 1}',
                            content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Test account scoping
        rv = self.app.patch('/api/bots/%d' % self.bot_ids[1],
                            data=bot_json_text,
                            content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_CLIENT_ERROR)

        # Add another new revision
        bot_json = json.loads(bot_json_text)
        bot_json['bot']['name'] = 'a_new_bot'
        rv = self.app.patch('/api/bots/%d' % self.bot_ids[0],
                            data=json.dumps(bot_json),
                            content_type='application/json')
        data = json.loads(rv.data)
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # The bot name should changed when the bot is saved
        rv = self.app.get('/api/bots/%d' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['name'], 'a_new_bot')

        # Commit the bot
        rv = self.app.put('/api/bots/%d' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['version'], 2)

        # Make sure that the name of bot has changed after v2 submitted
        rv = self.app.get('/api/bots/%d' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['name'], 'a_new_bot')

        # Test bot revision listing
        rv = self.app.get('/api/bots/%d/revisions' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['bot_defs']), 2)

        rv = self.app.get('/api/bots/%d/revisions/1' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['bot_json']['bot']['name'], u'simple')

        rv = self.app.get('/api/bots/%d/revisions/2' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['bot_json']['bot']['name'], u'a_new_bot')

    def test_bot_deletion(self):
        bot_file = get_bot_filename('test/bot_fmt_test.bot')
        with open(bot_file, 'r') as f:
            bot_json_text = f.read()

        # Make a revision
        rv = self.app.patch('/api/bots/%d' % self.bot_ids[0],
                            data=bot_json_text,
                            content_type='application/json')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        rv = self.app.put('/api/bots/%d' % self.bot_ids[0])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['version'], 1)

        # Test get all bots
        rv = self.app.get('/api/bots')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['bots']), 1)

        # Delete the bot
        self.app.delete('/api/bots/%d' % data['bots'][0]['id'])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)

        # Make sure we don't have any bots left
        rv = self.app.get('/api/bots')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['bots']), 0)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
