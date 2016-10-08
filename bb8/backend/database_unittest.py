#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Database ORM definition unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import time
import unittest
import uuid

import jwt
import pytz

from sqlalchemy.exc import IntegrityError

from bb8 import app, config
from bb8.error import AppError
from bb8.backend.bot_parser import get_bot_filename, parse_bot
from bb8.backend.database import DatabaseManager
from bb8.backend.database import (Account, Bot, ColletedDatum, Conversation,
                                  ContentModule, Event, Linkage, Node,
                                  ParserModule, Platform, PlatformTypeEnum,
                                  SenderEnum, User, Broadcast,
                                  FeedEnum, Feed, PublicFeed, OAuthInfo,
                                  OAuthProviderEnum)

from bb8.backend.test_utils import reset_and_setup_bots


class UserUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_session_mutable_tracking(self):
        bot = reset_and_setup_bots(['test/simple.bot'])[0]
        user = User(bot_id=bot.id, platform_id=bot.platforms[0].id,
                    platform_user_ident='',
                    last_seen=datetime.datetime.now(), session=1).add()
        DatabaseManager.commit()

        self.assertNotEquals(User.get_by(id=user.id, single=True), None)

        s = User.get_by(id=user.id, single=True)
        s.session.message_sent = True
        DatabaseManager.commit()

        s = User.get_by(id=user.id, single=True)
        self.assertEquals(s.session.message_sent, True)


class SchemaUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_schema(self):
        """Test database schema and make sure all the tables can be created
        without problems."""
        DatabaseManager.reset()
        DatabaseManager.commit()

    def test_schema_sanity(self):
        """Populate data into all tables and make sure there are no error."""
        DatabaseManager.reset()

        account = Account(name=u'Test Account', username='test',
                          email='test@test.com', passwd='test_hashed').add()

        bot = Bot(name=u'test', description=u'test', interaction_timeout=120,
                  session_timeout=86400).add()

        content = ContentModule(id='test', name='Content1', description='desc',
                                module_name='', ui_module_name='').add()
        parser = ParserModule(id='test', name='Parser1', description='desc',
                              module_name='passthrough', ui_module_name='',
                              variables={}).add()

        # Test for oauth schema
        oauth1 = OAuthInfo(provider=OAuthProviderEnum.Facebook,
                           provider_ident='mock-facebook-id').add()

        oauth2 = OAuthInfo(provider=OAuthProviderEnum.Github,
                           provider_ident='mock-github-id').add()

        account.oauth_infos.append(oauth1)
        account.oauth_infos.append(oauth2)
        DatabaseManager.commit()

        account_ = Account.get_by(id=account.id, single=True)
        self.assertNotEquals(account_, None)
        self.assertEquals(len(account_.oauth_infos), 2)

        oauth_ = OAuthInfo.get_by(provider_ident='mock-facebook-id',
                                  single=True)
        self.assertNotEquals(oauth_, None)
        self.assertNotEquals(oauth_.account, None)
        self.assertEquals(oauth_.account.id, account.id)

        # Test for bot
        account.bots.append(bot)

        DatabaseManager.commit()

        self.assertNotEquals(Account.get_by(id=account.id, single=True), None)
        self.assertNotEquals(Bot.get_by(id=bot.id, single=True), None)
        self.assertNotEquals(ContentModule.get_by(id=content.id, single=True),
                             None)
        self.assertNotEquals(ParserModule.get_by(id=parser.id, single=True),
                             None)

        # Check acccount_bot association table
        self.assertEquals(len(account.bots), 1)
        self.assertEquals(account.bots[0].id, bot.id)

        platform = Platform(bot_id=bot.id, type_enum=PlatformTypeEnum.Facebook,
                            provider_ident='facebook_page_id',
                            config={}).add()
        DatabaseManager.commit()

        self.assertNotEquals(Platform.get_by(id=platform.id, single=True),
                             None)
        self.assertEquals(len(bot.platforms), 1)
        self.assertEquals(bot.platforms[0].id, platform.id)

        node1 = Node(name=u'1', bot_id=bot.id, expect_input=True,
                     content_module_id=content.id, content_config={},
                     parser_module_id=parser.id, parser_config={}).add()

        node2 = Node(name=u'2', bot_id=bot.id, expect_input=True,
                     content_module_id=content.id, content_config={},
                     parser_module_id=parser.id, parser_config={}).add()

        node3 = Node(name=u'3', bot_id=bot.id, expect_input=True,
                     content_module_id=content.id, content_config={},
                     parser_module_id=parser.id, parser_config={}).add()

        bot.orphan_nodes.append(node3)

        DatabaseManager.commit()

        self.assertNotEquals(Node.get_by(id=node1.id, single=True), None)
        self.assertNotEquals(Node.get_by(id=node2.id, single=True), None)
        self.assertNotEquals(Node.get_by(id=node3.id, single=True), None)

        # Test bot_node association table
        self.assertEquals(bot.orphan_nodes[0].id, node3.id)

        l1 = Linkage(bot_id=bot.id, start_node_id=node1.id,
                     end_node_id=node2.id, action_ident='action0',
                     ack_message=u'').add()
        l2 = Linkage(bot_id=bot.id, start_node_id=node2.id,
                     end_node_id=node1.id, action_ident='action1',
                     ack_message=u'').add()

        DatabaseManager.commit()

        self.assertNotEquals(Linkage.get_by(id=l1.id, single=True), None)
        self.assertNotEquals(Linkage.get_by(id=l1.id, single=True), None)

        self.assertEquals(len(node1.linkages), 1)
        self.assertEquals(node1.linkages[0].id, l1.id)

        self.assertEquals(len(node2.linkages), 1)
        self.assertEquals(node2.linkages[0].id, l2.id)

        DatabaseManager.commit()

        user = User(bot_id=bot.id, platform_id=platform.id,
                    platform_user_ident='',
                    last_seen=datetime.datetime.now()).add()
        DatabaseManager.commit()

        self.assertNotEquals(User.get_by(id=user.id, single=True), None)

        event = Event(bot_id=bot.id, user_id=user.id, event_name='event',
                      event_value={}).add()
        DatabaseManager.commit()

        self.assertNotEquals(Event.get_by(id=event.id, single=True), None)

        collected_datum = ColletedDatum(user_id=user.id,
                                        key='key', value={}).add()
        DatabaseManager.commit()

        self.assertNotEquals(ColletedDatum.get_by(id=collected_datum.id,
                                                  single=True), None)
        self.assertEquals(len(user.colleted_data), 1)
        self.assertEquals(user.colleted_data[0].id, collected_datum.id)

        conversation = Conversation(bot_id=bot.id, user_id=user.id,
                                    sender_enum=SenderEnum.Bot, msg={}).add()
        DatabaseManager.commit()
        self.assertNotEquals(Conversation.get_by(id=conversation.id,
                                                 single=True), None)

        # Broadcast
        bc = Broadcast(message={},
                       scheduled_time=datetime.datetime.utcnow()).add()

        DatabaseManager.commit()
        self.assertNotEquals(Broadcast.get_by(id=bc.id, single=True), None)

        # PublicFeed, Feed
        account = Account(name=u'Test Account - 1', username='test1',
                          email='test1@test.com', passwd='test_hashed').add()
        feed1 = Feed(url='example.com/rss', type=FeedEnum.RSS,
                     title=u'foo.com', image_url='foo.com/logo').add()
        feed2 = Feed(url='example.com/rss', type=FeedEnum.RSS,
                     title=u'bar.com', image_url='bar.com/logo').add()
        feed3 = Feed(url='example.com/rss', type=FeedEnum.RSS,
                     title=u'baz.com', image_url='baz.com/logo').add()

        account.feeds.append(feed1)
        account.feeds.append(feed2)
        account.feeds.append(feed3)

        DatabaseManager.commit()
        self.assertNotEquals(Feed.get_by(id=feed1.id, single=True), None)

        feeds = Feed.search_title('ba')
        self.assertEquals(len(list(feeds)), 2)

        pfeed = PublicFeed(url='example.com/rss', type=FeedEnum.RSS,
                           title=u'example.com',
                           image_url='example.com/logo').add()

        DatabaseManager.commit()
        self.assertNotEquals(PublicFeed.get_by(id=pfeed.id, single=True), None)

    def test_timestamp_update(self):
        """Make sure the updated_at timestamp automatically updates on
        commit."""
        account = Account(username=u'user', email='test@test.com',
                          passwd='test_hashed').add()
        DatabaseManager.commit()

        account.refresh()
        self.assertEquals(account.created_at, account.updated_at)
        last_updated = account.updated_at

        time.sleep(1)
        account.username = 'user2'
        DatabaseManager.commit()

        account.refresh()
        self.assertNotEquals(last_updated, account.updated_at)

    def test_Bot_API(self):
        """Test Bot model APIs."""
        DatabaseManager.reset()

        bots = reset_and_setup_bots(['test/simple.bot', 'test/postback.bot'])
        bot1 = bots[0]
        bot2 = bots[1]

        bot2_node_len = len(bot2.nodes)
        bot2_linkage_len = len(bot2.linkages)

        bot1.delete_all_node_and_links()
        DatabaseManager.commit()

        # All nodes and links related to this bot should be gone.
        self.assertEquals(bot1.nodes, [])
        self.assertEquals(bot1.linkages, [])

        # Make sure delete_all_node_and_links does not accidentally delete node
        # of other bot
        self.assertEquals(len(bot2.nodes), bot2_node_len)
        self.assertEquals(len(bot2.linkages), bot2_linkage_len)

        # Test bot reconstruction
        parse_bot(get_bot_filename('test/simple.bot'), bot1.id)
        DatabaseManager.commit()

        self.assertNotEquals(bot1.nodes, [])
        self.assertNotEquals(bot1.linkages, [])

        user = User(bot_id=bot1.id,
                    platform_id=bot1.platforms[0].id,
                    platform_user_ident='blablabla',
                    last_seen=datetime.datetime.now()).add()

        # Delete should fail because of foreign key constraint
        with self.assertRaises(IntegrityError):
            bot1.delete()

        user.delete()
        DatabaseManager.commit()

        bot1_id = bot1.id
        bot1.delete()
        DatabaseManager.commit()
        self.assertEquals(Bot.get_by(id=bot1_id, single=True), None)

    def test_json_serializer(self):
        DatabaseManager.reset()
        account = Account(name=u'tester', username='test1',
                          email='test@test.com')

        dt = datetime.datetime(2010, 1, 1, 0, 0, tzinfo=pytz.utc)
        account.created_at = dt

        account.__json_public__.append('created_at')

        d = account.to_json()
        self.assertEquals(d['created_at'], 1262304000)
        self.assertEquals(d['username'], 'test1')
        self.assertEquals(d['name'], 'tester')
        self.assertEquals(d['email'], 'test@test.com')

    def test_auth(self):
        DatabaseManager.reset()
        account = Account(name=u'Test Account 3', username='test3',
                          email='test3@test.com').add()

        some_passwd = 'abcdefg'
        account.set_passwd(some_passwd)

        DatabaseManager.commit()
        account_ = Account.get_by(id=account.id, single=True)
        self.assertNotEquals(account_.passwd, some_passwd)
        self.assertEquals(account_.verify_passwd(some_passwd), True)
        self.assertEquals(account_.verify_passwd('should be wrong'), False)

        token = account_.auth_token

        account_t = Account.from_auth_token(token)
        self.assertEquals(account_.id, account_t.id)

        fake_token = jwt.encode({
            'iss': 'compose.ai',
            'sub': account_.id,
            'jti': str(uuid.uuid4()),
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14)
        }, 'im fake secret')

        with self.assertRaises(AppError):
            Account.from_auth_token(fake_token)

        outdated_token = jwt.encode({
            'iss': 'compose.ai',
            'sub': account_.id,
            'jti': str(uuid.uuid4()),
            'iat': datetime.datetime.utcnow() - datetime.timedelta(days=30),
            'exp': datetime.datetime.utcnow() - datetime.timedelta(days=15)
        }, config.JWT_SECRET)

        with self.assertRaises(AppError):
            Account.from_auth_token(outdated_token)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
