#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Database ORM definition unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.database import DatabaseManager
from bb8.backend.database import (Account, Bot, ContentModule, Node,
                                  ParserModule, Platform, PlatformTypeEnum)

from bb8.backend.engine import Engine


class PopulateTestDataUnitTest(unittest.TestCase):
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

        config = {
            "validation_token": "meow_meow_meow",
            "access_token": "EAAP0okfsZCVkBANNgGSRPG0fsOWJKSQCNegqX8s1qxS7bVd"
                            "AIsfofqEeoiTtVm11Xgy5vm0MQGHyGtji5AwAXSQTQMAfZBua"
                            "wZCfy4prQ7IZBoTFyu8EGAYRGFZBwcgBjU2sXUtFMNbzp1M9m"
                            "MfTNZBdfjjRe3S0PM08vvCYkQ6QZDZD"
        }

        self.platform = Platform(bot_id=self.bot.id,
                                 type_enum=PlatformTypeEnum.Facebook,
                                 provider_ident='facebook_page_id',
                                 config=config).add()
        self.dbm.commit()

        self.account.bots.append(self.bot)

        self.passthrough = ParserModule(name='Passthrough',
                                        module_name='passthrough',
                                        description='Passthrough to some node',
                                        ui_module_name='', variables={}).add()
        self.dbm.commit()

    def test_populate(self):
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
        imgur_content = ContentModule(name='Imgur',
                                      description='Imgur',
                                      module_name='imgur',
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
                          content_module_id=content.id,
                          content_config={
                              'text': 'Hi there, this is a demo bot.'
                          },
                          parser_module_id=self.passthrough.id,
                          parser_config={}).add()
        node_root = Node(bot_id=self.bot.id, expect_input=True,
                         content_module_id=content.id,
                         content_config={
                             'text': 'Type "help" for command usage. You are '
                                     'now in root node, available global '
                                     'commands: "help", "globalA", "globalD", '
                                     '"imgur".'
                         },
                         parser_module_id=global_parser.id,
                         parser_config={}).add()
        node_imgur = Node(bot_id=self.bot.id, expect_input=False,
                          content_module_id=imgur_content.id, content_config={
                              'type': 'random',
                              'term': 'bb8',
                              'max_count': 5,
                              'auth': {
                                  'client_id': '1c98ef2ca07eff6',
                                  'client_secret': 'a804baeb1e569521d27cf914f'
                                                   'f76a313bb835148'
                              }
                          }).add()
        node_A = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={
                          'text': 'You are in node A. Available command: '
                                  '"error", "gotoB", "gotoC"'
                      },
                      parser_module_id=parser.id, parser_config={}).add()
        node_B = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={
                          'text': 'You are in node B. Available command: '
                                  '"gotoC"'
                      },
                      parser_module_id=parser.id, parser_config={}).add()
        node_C = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={
                          'text': 'You are in node C. Available command: '
                                  '"gotoA"'
                      },
                      parser_module_id=parser.id, parser_config={}).add()
        node_D = Node(bot_id=self.bot.id, expect_input=True,
                      content_module_id=content.id, content_config={
                          'text': 'You are in node D. Available command: '
                                  '"gotoE"'
                      },
                      parser_module_id=parser.id, parser_config={}).add()
        node_E = Node(bot_id=self.bot.id, expect_input=False,
                      content_module_id=content.id, content_config={
                          'text': 'You are in node E'
                      }).add()
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
                    'action_ident': 'globalA',
                    'end_node_id': node_A.id,
                    'ack_message': 'Goto global command A',
                },
                {
                    'action_ident': 'globalD',
                    'end_node_id': node_D.id,
                    'ack_message': 'Goto global command D',
                },
                {
                    'action_ident': 'imgur',
                    'end_node_id': node_imgur.id,
                    'ack_message': '',
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
                    'action_ident': 'gotoA',
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


if __name__ == '__main__':
    unittest.main()
