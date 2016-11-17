#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Engine unittest
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest
import datetime

import mock

from bb8 import app
from bb8.backend.database import DatabaseManager, Platform, User
from bb8.backend.engine import Engine
from bb8.backend.message import UserInput, InputTransformation
from bb8.backend.test_utils import reset_and_setup_bots


class EngineUnittest(unittest.TestCase):
    def setUp(self):
        self.bot = None
        self.user = None
        self.send_message_mock = mock.patch(
            'bb8.backend.messaging.send_message').start()

        DatabaseManager.connect()

    def tearDown(self):
        DatabaseManager.disconnect()
        self.send_message_mock.stop()  # pylint: disable=E1101

    def setup_prerequisite(self, bot_file):
        InputTransformation.clear()
        self.bot = reset_and_setup_bots([bot_file])[0]
        self.user = User(platform_id=Platform.get_by(id=1, single=True).id,
                         platform_user_ident='blablabla',
                         last_seen=datetime.datetime.now()).add()

        DatabaseManager.commit()

    def test_simple_graph(self):
        """Test a simple graph (test/simple.bot)

        start -----> root -- > D --> E
                      |
                      v
                      A --> B --> C
                      .           ^
                       `----------`
        """
        self.setup_prerequisite('test/simple.bot')

        engine = Engine()

        engine.run(self.bot, self.user)  # start and root display
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        # Try global gotoA command
        engine.run(self.bot, self.user, UserInput.Text('gotoA'))
        self.assertEquals(self.user.session.node_id, 'NodeARouter')
        self.assertEquals(self.send_message_mock.called, True)

        # Try error path: go back to current node
        engine.run(self.bot, self.user, UserInput.Text('error'))
        self.assertEquals(self.user.session.node_id, 'NodeARouter')

        # Try normal path
        engine.run(self.bot, self.user, UserInput.Text('gotoB'))
        self.assertEquals(self.user.session.node_id, 'NodeBRouter')

        # Another normal path try
        engine.run(self.bot, self.user, UserInput.Text('gotoC'))
        self.assertEquals(self.user.session.node_id, 'NodeCRouter')

        # Try global command
        engine.run(self.bot, self.user, UserInput.Text('help'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        # Try invalid global command in root_node_id
        engine.run(self.bot, self.user, UserInput.Text('blablabla'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        # Try global gotoA command
        engine.run(self.bot, self.user, UserInput.Text('gotoA'))
        self.assertEquals(self.user.session.node_id, 'NodeARouter')

        # Try global gotoD command
        engine.run(self.bot, self.user, UserInput.Text('gotoD'))
        self.assertEquals(self.user.session.node_id, 'NodeDRouter')

        engine.run(self.bot, self.user, UserInput.Text('gotoE'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')

    def test_postback(self):
        self.setup_prerequisite('test/postback.bot')

        engine = Engine()

        engine.run(self.bot, self.user)  # start and root display
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        postback = {
            'postback': {
                'payload': '{"message": {"text": "PAYLOAD_TEXT"}, '
                           '"node_id": "PostbackRouter"}'
            }
        }

        # Try postback
        engine.run(self.bot, self.user,
                   UserInput.FromFacebookMessage(postback))
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        sent_msg = self.send_message_mock.call_args_list[-2][0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'PAYLOAD_TEXT')

        # Goto back to root node
        engine.run(self.bot, self.user, None)

        # Goto postback node
        engine.run(self.bot, self.user, UserInput.Text('postback'))
        self.assertEquals(self.user.session.node_id, 'PostbackRouter')

        engine.run(self.bot, self.user, UserInput.Text('TEXT'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        sent_msg = self.send_message_mock.call_args_list[-2][0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'TEXT')

    def test_input_transformation(self):
        """Test input transformation.

        If input transformation is set. Test that the user input is correctly
        transformed then tirgger the actually parser rule.
        """
        self.setup_prerequisite('test/input_transformation.bot')

        engine = Engine()

        engine.run(self.bot, self.user)  # start and root display
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        # Button title should work
        engine.run(self.bot, self.user, UserInput.Text('option 1'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')
        sent_msg = self.send_message_mock.call_args_list[-2][0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'payload1')

        # Back to root parser
        engine.run(self.bot, self.user)
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        # acceptable_inputs should work
        engine.run(self.bot, self.user, UserInput.Text('D'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')
        sent_msg = self.send_message_mock.call_args_list[-2][0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'payload2')

        # Back to root
        engine.run(self.bot, self.user)
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        # numbers should work
        engine.run(self.bot, self.user, UserInput.Text('1'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')
        sent_msg = self.send_message_mock.call_args_list[-2][0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'payload1')

    def test_memory_settings(self):
        self.setup_prerequisite('test/memory_settings.bot')

        engine = Engine()

        engine.run(self.bot, self.user)  # start and root display
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        engine.run(self.bot, self.user, UserInput.Text('memory_set'))
        self.assertEquals(self.user.session.node_id, 'RootRouter')

        sent_msg = self.send_message_mock.call_args_list[-2][0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'abc')
        self.assertEquals(len(self.user.memory), 0)

        engine.run(self.bot, self.user, UserInput.Text('settings_set'))

        sent_msg = self.send_message_mock.call_args_list[-2][0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'def')
        self.assertEquals(len(self.user.settings), 1)
        self.assertNotEqual(self.user.settings.get('subscribe', None), None)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
