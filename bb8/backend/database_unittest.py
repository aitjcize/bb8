#!/usr/bin/env python
"""
    Database ORM definition unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""


import unittest

from bb8.backend.database import DatabaseManager
from bb8.backend.database import (Account, Action, Bot, ColletedDatum,
                                  Conversation, ContentModule, Event, Linkage,
                                  Node, ParserModule, Platform,
                                  PlatformTypeEnum, SenderEnum, User)


class DatabaseUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()

    def tearDown(self):
        self.dbm.disconnect()

    def testSchema(self):
        """Test database schema and make sure all the tables can be created
        without problems."""
        self.dbm.reset()
        self.dbm.commit()

    def testSchemaSanity(self):
        """Populate data into all tables and make sure there are no error."""
        self.dbm.reset()

        account = Account(name='Test Account', email='test@test.com',
                          passwd='test_hashed').add()
        action = Action(name='action', description='desc').add()

        bot = Bot(description='test', interaction_timeout=120,
                  session_timeout=86400).add()

        content = ContentModule(name='Content1', content_filename='',
                                ui_filename='').add()
        parser = ParserModule(name='Parser1', content_filename='',
                              ui_filename='', variables={}).add()

        account.bots.append(bot)

        self.dbm.commit()

        assert Account.get_by(id=account.id, single=True) is not None
        assert Action.get_by(id=action.id, single=True) is not None
        assert Bot.get_by(id=bot.id, single=True) is not None
        assert ContentModule.get_by(id=content.id, single=True) is not None
        assert ParserModule.get_by(id=parser.id, single=True) is not None

        # Check acccount_bot association table
        assert len(account.bots) == 1 and account.bots[0].id == bot.id

        platform = Platform(bot_id=bot.id, type_enum=PlatformTypeEnum.Facebook,
                            provider_ident='facebook_page_id',
                            configuration={}).add()
        self.dbm.commit()

        assert Platform.get_by(id=platform.id, single=True) is not None
        assert len(bot.platforms) == 1 and bot.platforms[0].id == platform.id

        node1 = Node(bot_id=bot.id, content_module_id=content.id,
                     content_config={}, parser_module_id=parser.id,
                     parser_config={}).add()

        node2 = Node(bot_id=bot.id, content_module_id=content.id,
                     content_config={}, parser_module_id=parser.id,
                     parser_config={}).add()

        node3 = Node(bot_id=bot.id, content_module_id=content.id,
                     content_config={}, parser_module_id=parser.id,
                     parser_config={}).add()

        bot.orphan_nodes.append(node3)

        self.dbm.commit()

        assert Node.get_by(id=node1.id, single=True) is not None
        assert Node.get_by(id=node2.id, single=True) is not None
        assert Node.get_by(id=node3.id, single=True) is not None

        # Test bot_node association table
        assert bot.orphan_nodes[0].id == node3.id

        l1 = Linkage(start_node_id=node1.id, end_node_id=node2.id,
                     action_id=action.id,
                     ack_message='').add()
        l2 = Linkage(start_node_id=node2.id, end_node_id=node1.id,
                     action_id=action.id,
                     ack_message='').add()

        self.dbm.commit()

        assert Linkage.get_by(id=l1.id, single=True) is not None
        assert Linkage.get_by(id=l1.id, single=True) is not None

        assert len(node1.linkages) == 1 and node1.linkages[0].id == l1.id

        assert len(node2.linkages) == 1 and node2.linkages[0].id == l2.id

        user = User(account_id=account.id,
                    platform_type_enum=PlatformTypeEnum.Facebook,
                    platform_user_id='blablabla',
                    session_stack=[]).add()
        self.dbm.commit()

        assert User.get_by(id=user.id, single=True) is not None
        assert len(account.users) == 1 and account.users[0].id == user.id

        event = Event(bot_id=bot.id, user_id=user.id, event_name='event',
                      event_value={}).add()
        self.dbm.commit()

        assert Event.get_by(id=event.id, single=True) is not None

        collected_datum = ColletedDatum(account_id=account.id, user_id=user.id,
                                        key='key', value={}).add()
        self.dbm.commit()

        assert (ColletedDatum.get_by(id=collected_datum.id, single=True)
                is not None)
        assert (len(user.colleted_data) == 1 and
                user.colleted_data[0].id == collected_datum.id)

        conversation = Conversation(bot_id=bot.id, user_id=user.id,
                                    sender_enum=SenderEnum.Bot, msg={}).add()
        self.dbm.commit()
        assert (Conversation.get_by(id=conversation.id, single=True)
                is not None)


if __name__ == '__main__':
    unittest.main()
