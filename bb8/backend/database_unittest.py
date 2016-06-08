#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Database ORM definition unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.database import DatabaseManager
from bb8.backend.database import (Account, Bot, ColletedDatum, Conversation,
                                  ContentModule, Event, Linkage, Node,
                                  ParserModule, Platform, PlatformTypeEnum,
                                  SenderEnum, User)


class UserUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()

    def tearDown(self):
        self.dbm.disconnect()

    def test_session_mutable_tracking(self):
        # Exploit the fact that SQLite foreign key constraint has really no
        # effect on insert/deletion. see: # http://docs.sqlalchemy.org/en/\
        # latest/dialects/sqlite.html#foreign-key-support
        user = User(bot_id=1, platform_id=2, platform_user_ident='',
                    last_seen=1464871496, session=1).add()
        self.dbm.commit()

        self.assertNotEquals(User.get_by(id=user.id, single=True), None)

        s = User.get_by(id=user.id, single=True)
        s.session.message_sent = True
        s.commit()

        s = User.get_by(id=user.id, single=True)
        self.assertEquals(s.session.message_sent, True)


class SchemaUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()

    def tearDown(self):
        self.dbm.disconnect()

    def test_schema(self):
        """Test database schema and make sure all the tables can be created
        without problems."""
        self.dbm.reset()
        self.dbm.commit()

    def test_schema_sanity(self):
        """Populate data into all tables and make sure there are no error."""
        self.dbm.reset()

        account = Account(name='Test Account', email='test@test.com',
                          passwd='test_hashed').add()

        bot = Bot(name='test', description='test', interaction_timeout=120,
                  session_timeout=86400).add()

        content = ContentModule(id='test', name='Content1', description='desc',
                                module_name='', ui_module_name='').add()
        parser = ParserModule(id='test', name='Parser1', description='desc',
                              module_name='passthrough', ui_module_name='',
                              variables={}).add()

        account.bots.append(bot)

        self.dbm.commit()

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
        self.dbm.commit()

        self.assertNotEquals(Platform.get_by(id=platform.id, single=True),
                             None)
        self.assertEquals(len(bot.platforms), 1)
        self.assertEquals(bot.platforms[0].id, platform.id)

        node1 = Node(name='1', bot_id=bot.id, expect_input=True,
                     content_module_id=content.id, content_config={},
                     parser_module_id=parser.id, parser_config={}).add()

        node2 = Node(name='2', bot_id=bot.id, expect_input=True,
                     content_module_id=content.id, content_config={},
                     parser_module_id=parser.id, parser_config={}).add()

        node3 = Node(name='3', bot_id=bot.id, expect_input=True,
                     content_module_id=content.id, content_config={},
                     parser_module_id=parser.id, parser_config={}).add()

        bot.orphan_nodes.append(node3)

        self.dbm.commit()

        self.assertNotEquals(Node.get_by(id=node1.id, single=True), None)
        self.assertNotEquals(Node.get_by(id=node2.id, single=True), None)
        self.assertNotEquals(Node.get_by(id=node3.id, single=True), None)

        # Test bot_node association table
        self.assertEquals(bot.orphan_nodes[0].id, node3.id)

        l1 = Linkage(start_node_id=node1.id, end_node_id=node2.id,
                     action_ident='action0', ack_message='').add()
        l2 = Linkage(start_node_id=node2.id, end_node_id=node1.id,
                     action_ident='action1', ack_message='').add()

        self.dbm.commit()

        self.assertNotEquals(Linkage.get_by(id=l1.id, single=True), None)
        self.assertNotEquals(Linkage.get_by(id=l1.id, single=True), None)

        self.assertEquals(len(node1.linkages), 1)
        self.assertEquals(node1.linkages[0].id, l1.id)

        self.assertEquals(len(node2.linkages), 1)
        self.assertEquals(node2.linkages[0].id, l2.id)

        self.dbm.commit()

        user = User(bot_id=bot.id, platform_id=platform.id,
                    platform_user_ident='', last_seen=1464871496).add()
        self.dbm.commit()

        self.assertNotEquals(User.get_by(id=user.id, single=True), None)

        event = Event(bot_id=bot.id, user_id=user.id, event_name='event',
                      event_value={}).add()
        self.dbm.commit()

        self.assertNotEquals(Event.get_by(id=event.id, single=True), None)

        collected_datum = ColletedDatum(account_id=account.id, user_id=user.id,
                                        key='key', value={}).add()
        self.dbm.commit()

        self.assertNotEquals(ColletedDatum.get_by(id=collected_datum.id,
                                                  single=True), None)
        self.assertEquals(len(user.colleted_data), 1)
        self.assertEquals(user.colleted_data[0].id, collected_datum.id)

        conversation = Conversation(bot_id=bot.id, user_id=user.id,
                                    sender_enum=SenderEnum.Bot, msg={}).add()
        self.dbm.commit()
        self.assertNotEquals(Conversation.get_by(id=conversation.id,
                                                 single=True), None)


if __name__ == '__main__':
    unittest.main()
