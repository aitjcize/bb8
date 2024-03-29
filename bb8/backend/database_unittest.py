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

from bb8 import app, config
from bb8.backend.bot_parser import get_bot_filename, parse_bot_from_file
from bb8.backend.database import DatabaseManager
from bb8.backend.database import (Account, AccountUser, Bot, CollectedDatum,
                                  Conversation, Event, Node, Module, Platform,
                                  ModuleTypeEnum, PlatformTypeEnum, SenderEnum,
                                  User, Broadcast, FeedEnum, Feed, PublicFeed,
                                  OAuthInfo, OAuthProviderEnum, Label)

from bb8.backend.test_utils import reset_and_setup_bots


class UserUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_session_mutable_tracking(self):
        bot = reset_and_setup_bots(['test/simple.bot'])[0]
        user = User(platform_id=bot.platforms[0].id,
                    platform_user_ident='',
                    last_seen=datetime.datetime.now(), session=1).add()
        DatabaseManager.commit()

        self.assertNotEquals(User.get_by(id=user.id, single=True), None)

        s = User.get_by(id=user.id, single=True)
        s.session.input_transformation = 'Test'
        DatabaseManager.commit()

        s = User.get_by(id=user.id, single=True)
        self.assertEquals(s.session.input_transformation, 'Test')


class DatabaseUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()
        DatabaseManager.reset()

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

        account = Account(name=u'Test Account').add()
        account_user = AccountUser(name=u'Test Account', email='test@test.com',
                                   passwd='test_hashed', account=account).add()

        bot = Bot(name=u'test', description=u'test', interaction_timeout=120,
                  session_timeout=86400).add()
        account.bots.append(bot)

        module = Module(id='test', type=ModuleTypeEnum.Content,
                        name='Content1', description='desc',
                        module_name='test', variables=[]).add()

        # Test for oauth schema
        oauth1 = OAuthInfo(provider=OAuthProviderEnum.Facebook,
                           provider_ident='mock-facebook-id').add()

        oauth2 = OAuthInfo(provider=OAuthProviderEnum.Github,
                           provider_ident='mock-github-id').add()

        account_user.oauth_infos.append(oauth1)
        account_user.oauth_infos.append(oauth2)
        DatabaseManager.commit()

        account_user_ = AccountUser.get_by(id=account_user.id, single=True)
        self.assertNotEquals(account_user_, None)
        self.assertEquals(len(account_user_.oauth_infos), 2)

        oauth_ = OAuthInfo.get_by(provider_ident='mock-facebook-id',
                                  single=True)
        self.assertNotEquals(oauth_, None)
        self.assertNotEquals(oauth_.account_user, None)
        self.assertEquals(oauth_.account_user.id, account_user.id)

        # Test for bot
        account.bots.append(bot)

        DatabaseManager.commit()

        self.assertNotEquals(Account.get_by(id=account.id, single=True), None)
        self.assertNotEquals(Bot.get_by(id=bot.id, single=True), None)
        self.assertNotEquals(Module.get_by(id=module.id, single=True), None)

        # Check acccount_bot association table
        self.assertEquals(len(account.bots), 1)
        self.assertEquals(account.bots[0].id, bot.id)

        platform = Platform(name=u'Test platform',
                            bot_id=bot.id,
                            type_enum=PlatformTypeEnum.Facebook,
                            provider_ident='facebook_page_id',
                            config={}).add()
        DatabaseManager.commit()

        self.assertNotEquals(Platform.get_by(id=platform.id, single=True),
                             None)
        self.assertEquals(len(bot.platforms), 1)
        self.assertEquals(bot.platforms[0].id, platform.id)

        node1 = Node(stable_id='node1', name=u'1', bot_id=bot.id,
                     expect_input=True, module_id=module.id, config={}).add()

        node2 = Node(stable_id='node2', name=u'2', bot_id=bot.id,
                     expect_input=True, module_id=module.id, config={}).add()

        node3 = Node(stable_id='node3', name=u'3', bot_id=bot.id,
                     expect_input=True, module_id=module.id, config={}).add()

        bot.orphan_nodes.append(node3)

        DatabaseManager.commit()

        self.assertNotEquals(Node.get_by(id=node1.id, single=True), None)
        self.assertNotEquals(Node.get_by(id=node2.id, single=True), None)
        self.assertNotEquals(Node.get_by(id=node3.id, single=True), None)

        # Test bot_node association table
        self.assertEquals(bot.orphan_nodes[0].id, node3.id)

        user = User(platform_id=platform.id,
                    platform_user_ident='',
                    last_seen=datetime.datetime.now()).add()
        DatabaseManager.commit()

        self.assertNotEquals(User.get_by(id=user.id, single=True), None)

        event = Event(bot_id=bot.id, user_id=user.id, event_name='event',
                      event_value={}).add()
        DatabaseManager.commit()

        self.assertNotEquals(Event.get_by(id=event.id, single=True), None)

        collected_datum = CollectedDatum(user_id=user.id,
                                         key='key', value={}).add()
        DatabaseManager.commit()

        self.assertNotEquals(CollectedDatum.get_by(id=collected_datum.id,
                                                   single=True), None)
        self.assertEquals(len(user.colleted_data), 1)
        self.assertEquals(user.colleted_data[0].id, collected_datum.id)

        conversation = Conversation(user_id=user.id,
                                    sender_enum=SenderEnum.Bot,
                                    messages=[], timestamp=0).add()
        DatabaseManager.commit()
        self.assertNotEquals(Conversation.get_by(id=conversation.id,
                                                 single=True), None)

        # Broadcast
        bc = Broadcast(account_id=account.id, bot_id=bot.id,
                       name=u'New broadcast', messages=[],
                       scheduled_time=datetime.datetime.utcnow()).add()

        DatabaseManager.commit()
        self.assertNotEquals(Broadcast.get_by(id=bc.id, single=True), None)

        # PublicFeed, Feed
        account = Account(name=u'Test Account - 1').add()
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

        # Label
        label1 = Label(account_id=account.id, name=u'Label1').add()
        label2 = Label(account_id=account.id, name=u'Label2').add()
        label3 = Label(account_id=account.id, name=u'Label3').add()

        user.labels.append(label1)
        user.labels.append(label2)
        user.labels.append(label3)

        DatabaseManager.commit()
        user_ = User.get_by(id=user.id, single=True)
        self.assertNotEquals(user_, None)
        self.assertEquals(len(user_.labels), 3)

    def test_timestamp_update(self):
        """Make sure the updated_at timestamp automatically updates on
        commit."""
        account = Account(name=u'Test account').add()
        account_user = AccountUser(email='test@test.com',
                                   passwd='test_hashed', account=account).add()
        DatabaseManager.commit()

        account_user.refresh()
        self.assertEquals(account_user.created_at, account_user.updated_at)
        last_updated = account_user.updated_at

        time.sleep(1)
        account_user.email = 'test2@test.com'
        DatabaseManager.commit()

        account_user.refresh()
        self.assertNotEquals(last_updated, account_user.updated_at)

    def test_Bot_API(self):
        """Test Bot model APIs."""
        DatabaseManager.reset()

        bots = reset_and_setup_bots(['test/simple.bot', 'test/postback.bot'])
        bot1 = bots[0]
        bot2 = bots[1]

        bot2_node_len = len(bot2.nodes)

        bot1.delete_all_nodes()
        DatabaseManager.commit()

        # All nodes and links related to this bot should be gone.
        self.assertEquals(bot1.nodes, [])

        # Make sure delete_all_nodes does not accidentally delete node
        # of other bot
        self.assertEquals(len(bot2.nodes), bot2_node_len)

        # Test bot reconstruction
        parse_bot_from_file(get_bot_filename('test/simple.bot'), bot1.id)
        DatabaseManager.commit()

        self.assertNotEquals(bot1.nodes, [])
        self.assertEquals(bot1.users, [])

        User(platform_id=bot1.platforms[0].id,
             platform_user_ident='blablabla',
             last_seen=datetime.datetime.now()).add()
        User(platform_id=bot1.platforms[1].id,
             platform_user_ident='blablabla2',
             last_seen=datetime.datetime.now()).add()
        DatabaseManager.commit()
        self.assertEquals(len(bot1.users), 2)

        bot1_id = bot1.id
        bot1.delete()
        DatabaseManager.commit()
        self.assertEquals(Bot.get_by(id=bot1_id, single=True), None)

    def test_json_serializer(self):
        account = Account(name=u'Test account').add()
        account_user = AccountUser(name=u'tester', email='test@test.com',
                                   account=account)

        dt = datetime.datetime(2010, 1, 1, 0, 0, tzinfo=pytz.utc)
        account_user.created_at = dt

        account_user.__json_public__.append('created_at')

        d = account_user.to_json()
        self.assertEquals(d['created_at'], 1262304000)
        self.assertEquals(d['name'], 'tester')
        self.assertEquals(d['email'], 'test@test.com')

    def test_auth(self):
        account = Account(name=u'Test account').add()
        account_user = AccountUser(name=u'Test Account 3',
                                   email='test3@test.com',
                                   account=account).add()

        some_passwd = 'abcdefg'
        account_user.set_passwd(some_passwd)

        DatabaseManager.commit()
        account_user_ = AccountUser.get_by(id=account_user.id, single=True)
        self.assertNotEquals(account_user_.passwd, some_passwd)
        self.assertEquals(account_user_.verify_passwd(some_passwd), True)
        self.assertEquals(account_user_.verify_passwd('wrong'), False)

        token = account_user_.auth_token

        account_user_ = AccountUser.from_auth_token(token)
        self.assertEquals(account_user_.id, account_user_.id)

        fake_token = jwt.encode({
            'iss': 'compose.ai',
            'sub': account_user_.id,
            'jti': str(uuid.uuid4()),
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14)
        }, 'im fake secret')

        with self.assertRaises(RuntimeError):
            AccountUser.from_auth_token(fake_token)

        outdated_token = jwt.encode({
            'iss': 'compose.ai',
            'sub': account_user_.id,
            'jti': str(uuid.uuid4()),
            'iat': datetime.datetime.utcnow() - datetime.timedelta(days=30),
            'exp': datetime.datetime.utcnow() - datetime.timedelta(days=15)
        }, config.JWT_SECRET)

        with self.assertRaises(RuntimeError):
            AccountUser.from_auth_token(outdated_token)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
