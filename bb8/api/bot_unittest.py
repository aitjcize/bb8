#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    unit testing for bot api
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import unittest

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import account, bot
from bb8.constant import HTTPStatus, CustomError
from bb8.backend.database import DatabaseManager, Account, Bot


class BotAPIUnittest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        self.dbm = DatabaseManager()
        self.dbm.connect()
        self.dbm.reset()

        self.app = app.test_client()
        self.setup_prerequisite()

    def tearDown(self):
        self.dbm.disconnect()

    def setup_prerequisite(self):
        Account(name=u'test',
                username='test-account-1',
                email='test@gmail.com') \
            .set_passwd('12345678') \
            .add()
        self.dbm.commit()

    def test_create_get_bot(self):
        rv = self.app.post('/login', data=dict(
            email='test@gmail.com',
            passwd='12345678'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        # Test create bots
        rv = self.app.post('/bots', data=dict(
            name='test-bot',
            description='test-description',
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        data = json.loads(rv.data)
        self.assertEquals('test-bot', data['name'])

        # Test get all bots
        rv = self.app.get('/bots')
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(len(data['bots']), 1)

        # Test get one bots
        rv = self.app.get('/bots/%d' % data['bots'][0]['id'])
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)
        data = json.loads(rv.data)
        self.assertEquals(data['name'], 'test-bot')

        # TODO: Test delete bot


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
