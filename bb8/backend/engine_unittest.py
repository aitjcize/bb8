#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Engine unittest
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.database import DatabaseManager
from bb8.backend.database import (Account, Bot, ContentModule, Node,
                                  ParserModule, Platform, PlatformTypeEnum,
                                  User)

from bb8.backend import messaging
from bb8.backend.engine import Engine
from bb8.backend.metadata import UserInput


class EngineUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()
        self.account = None
        self.bot = None
        self.platform = None
        self.setup_prerequisite()

    def tearDown(self):
        self.dbm.disconnect()

    def setup_prerequisite(self):
        self.dbm.reset()

        self.account = Account(name='Test Account', email='test@test.com',
                               passwd='test_hashed').add()

        self.bot = Bot(name='test', description='test',
                       interaction_timeout=120, session_timeout=86400).add()
        self.dbm.commit()

        self.platform = Platform(bot_id=self.bot.id,
                                 type_enum=PlatformTypeEnum.Facebook,
                                 provider_ident='facebook_page_id',
                                 config={}).add()
        self.dbm.commit()

        self.user = User(bot_id=self.bot.id,
                         platform_id=self.platform.id,
                         platform_user_ident='blablabla',
                         last_seen=1464871496).add()

        self.account.bots.append(self.bot)

        self.passthrough = ParserModule(name='Passthrough',
                                        module_name='passthrough',
                                        description='Passthrough to some node',
                                        ui_module_name='', variables={}).add()
        self.dbm.commit()

    def test_simple_graph(self):
        """Test a simple graph

        start -----> root -- > D --> E
                      |
                      v
                      A --> B --> C
                      .           ^
                       `----------`
        """

        content = ContentModule(name='Empty', description='Send text message',
                                module_name='text_message',
                                ui_module_name='').add()
        parser = ParserModule(name='Literal', module_name='test.literal',
                              description='Return user input as action_ident',
                              ui_module_name='', variables={}).add()
        global_parser = ParserModule(name='Global command',
                                     module_name='test.literal_root',
                                     description='Global command parser',
                                     ui_module_name='', variables={}).add()
        self.dbm.commit()

        # Build test graph
        node_start = Node(bot_id=self.bot.id, expect_input=False,
                          content_module_id=content.id, content_config={},
                          parser_module_id=self.passthrough.id,
                          parser_config={}).add()
        node_root = Node(bot_id=self.bot.id, expect_input=True,
                         content_module_id=content.id,
                         content_config={}, parser_module_id=global_parser.id,
                         parser_config={}).add()
        node_A = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={},
                      parser_module_id=parser.id, parser_config={}).add()
        node_B = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={},
                      parser_module_id=parser.id, parser_config={}).add()
        node_C = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={},
                      parser_module_id=parser.id, parser_config={}).add()
        node_D = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={},
                      parser_module_id=parser.id, parser_config={}).add()
        node_E = Node(bot_id=self.bot.id, expect_input=False,
                      content_module_id=content.id, content_config={}).add()
        self.dbm.commit()

        node_start.parser_config = {
            'end_node_id': node_root.id,
            'ack_message': 'Goto root',
        }
        node_root.parser_config = {
            'links': [
                {
                    'action_ident': 'help',
                    'end_node_id': node_root.id,
                    'ack_message': 'Goto help',
                },
                {
                    'action_ident': 'gotoA',
                    'end_node_id': node_A.id,
                    'ack_message': 'Goto A',
                },
                {
                    'action_ident': 'gotoD',
                    'end_node_id': node_D.id,
                    'ack_message': 'Goto D',
                },
            ]
        }
        node_A.parser_config = {
            'links': [
                {
                    'action_ident': 'error',
                    'end_node_id': None,
                    'ack_message': 'Goto A',
                },
                {
                    'action_ident': 'gotoB',
                    'end_node_id': node_B.id,
                    'ack_message': 'Goto B',
                },
                {
                    'action_ident': 'gotoC',
                    'end_node_id': node_C.id,
                    'ack_message': 'Goto C',
                },
            ]
        }
        node_B.parser_config = {
            'links': [
                {
                    'action_ident': 'gotoC',
                    'end_node_id': node_C.id,
                    'ack_message': 'Goto C',
                },
            ]
        }
        node_C.parser_config = {
            'links': [
                {
                    'action_ident': 'default',
                    'end_node_id': node_A.id,
                    'ack_message': 'Goto A',
                },
            ]
        }
        node_D.parser_config = {
            'links': [
                {
                    'action_ident': 'gotoE',
                    'end_node_id': node_E.id,
                    'ack_message': 'Goto E',
                },
            ]
        }
        self.dbm.commit()

        # Bot setup
        self.bot.root_node_id = node_root.id
        self.bot.start_node_id = node_start.id

        engine = Engine()

        pm = engine.get_parser_module(self.passthrough.module_name)
        node_start.build_linkages(pm.get_linkages(node_start.parser_config))

        pm = engine.get_parser_module(parser.module_name)
        for n in [node_root, node_A, node_B, node_C, node_D]:
            n.build_linkages(pm.get_linkages(n.parser_config))

        # Override module API method for testing
        context = {'message_sent': False}

        def send_message_mock(unused_user, unused_x):
            context['message_sent'] = True

        messaging.send_message = send_message_mock

        engine.step(self.bot, self.user)  # start display
        self.assertEquals(self.user.session.node_id, node_root.id)

        # We should now be in root node
        engine.step(self.bot, self.user)  # node_root display
        self.assertEquals(self.user.session.message_sent, True)

        # Try global gotoA command
        context['message_sent'] = False
        engine.step(self.bot, self.user, UserInput.Text('gotoA'))
        self.assertEquals(self.user.session.node_id, node_A.id)
        self.assertEquals(self.user.session.message_sent, True)
        self.assertEquals(context['message_sent'], True)

        # Try error path: go back to current node
        engine.step(self.bot, self.user, UserInput.Text('error'))
        self.assertEquals(self.user.session.message_sent, True)
        self.assertEquals(self.user.session.node_id, node_A.id)

        # Try normal path
        engine.step(self.bot, self.user, UserInput.Text('gotoB'))
        self.assertEquals(self.user.session.node_id, node_B.id)

        # Another normal path try
        engine.step(self.bot, self.user, UserInput.Text('gotoC'))
        self.assertEquals(self.user.session.node_id, node_C.id)

        # Try global command
        engine.step(self.bot, self.user, UserInput.Text('help'))
        self.assertEquals(self.user.session.node_id, node_root.id)
        self.assertEquals(self.user.session.message_sent, True)

        # Try invalid global command in root_node_id
        engine.step(self.bot, self.user, UserInput.Text('blablabla'))
        self.assertEquals(self.user.session.node_id, node_root.id)
        self.assertEquals(self.user.session.message_sent, True)

        # Try global gotoA command
        engine.step(self.bot, self.user, UserInput.Text('gotoA'))
        self.assertEquals(self.user.session.node_id, node_A.id)
        self.assertEquals(self.user.session.message_sent, True)

        # Try global gotoD command
        engine.step(self.bot, self.user, UserInput.Text('gotoD'))
        self.assertEquals(self.user.session.node_id, node_D.id)

        engine.step(self.bot, self.user, UserInput.Text('gotoE'))
        self.assertEquals(self.user.session.message_sent, True)
        self.assertEquals(self.user.session.node_id, node_root.id)


if __name__ == '__main__':
    unittest.main()
