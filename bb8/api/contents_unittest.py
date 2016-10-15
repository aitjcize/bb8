#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Unittest for Content API
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import unittest

from bb8 import app
# Register request handlers, pylint: disable=W0611
from bb8.api import accounts, contents
from bb8.constant import HTTPStatus, CustomError
from bb8.backend.database import DatabaseManager, Account, Feed, FeedEnum


class ContentAPIUnittest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True

        DatabaseManager.connect()
        DatabaseManager.reset()

        self.app = app.test_client()
        self.setup_prerequisite()

    def tearDown(self):
        DatabaseManager.disconnect()

    def setup_prerequisite(self):
        acc = Account(name=u'test',
                      username='test-account-1',
                      email='test@gmail.com') \
            .set_passwd('12345678') \
            .add()
        for i in range(50):
            feed = Feed(url='example%d.com' % i,
                        type=FeedEnum.RSS,
                        title=u'example%d.com' % i,
                        image_url='example%d.com/logo' % i).add()
            acc.feeds.append(feed)
        DatabaseManager.commit()

    def test_pagnination(self):
        rv = self.app.post('/api/login', data=dict(
            email='test@gmail.com',
            passwd='12345678'
        ))
        rv = self.app.get('/api/feeds?limit=5')
        data = json.loads(rv.data)
        self.assertEquals(len(data['feeds']), 5)

        rv = self.app.get('/api/feeds?offset=25&limit=50')
        data = json.loads(rv.data)
        self.assertEquals(len(data['feeds']), 25)

        rv = self.app.get('/api/feeds')
        data = json.loads(rv.data)
        self.assertEquals(len(data['feeds']), 10)

        rv = self.app.get('/api/feeds?offset=10')
        data = json.loads(rv.data)
        self.assertEquals(len(data['feeds']), 10)

        rv = self.app.get('/api/feeds?offset=b&limit=a')
        data = json.loads(rv.data)
        self.assertEquals(len(data['feeds']), 10)

    def test_feed(self):
        rv = self.app.post('/api/login', data=dict(
            email='test@gmail.com',
            passwd='12345678'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        rv = self.app.post('/api/feeds', data=dict(
            url='www.appledaily.com',
            type='RSS',
            title=u'apple daily',
            image_url='appledaily.com/logo'
        ))
        self.assertEquals(rv.status_code, HTTPStatus.STATUS_OK)

        data = json.loads(rv.data)
        self.assertEquals(data['feed']['title'], 'apple daily')


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
