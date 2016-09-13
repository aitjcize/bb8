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
from bb8.backend.database import DatabaseManager, Node, Platform, User
from bb8.backend.engine import Engine
from bb8.backend.metadata import UserInput, InputTransformation
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
        self.user = User(bot_id=self.bot.id,
                         platform_id=Platform.get_by(id=1, single=True).id,
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

        def get_node_id(name):
            return Node.get_by(name=unicode(name), single=True).id

        engine.step(self.bot, self.user)  # start display
        self.assertEquals(self.user.session.node_id, get_node_id('root'))

        # We should now be in root node
        engine.step(self.bot, self.user)  # root display
        self.assertEquals(self.user.session.message_sent, True)

        # Try global gotoA command
        engine.step(self.bot, self.user, UserInput.Text('gotoA'))
        self.assertEquals(self.user.session.node_id, get_node_id('nodeA'))
        self.assertEquals(self.user.session.message_sent, True)
        self.assertEquals(self.send_message_mock.called, True)

        # Try error path: go back to current node
        engine.step(self.bot, self.user, UserInput.Text('error'))
        self.assertEquals(self.user.session.message_sent, True)
        self.assertEquals(self.user.session.node_id, get_node_id('nodeA'))

        # Try normal path
        engine.step(self.bot, self.user, UserInput.Text('gotoB'))
        self.assertEquals(self.user.session.node_id, get_node_id('nodeB'))

        # Another normal path try
        engine.step(self.bot, self.user, UserInput.Text('gotoC'))
        self.assertEquals(self.user.session.node_id, get_node_id('nodeC'))

        # Try global command
        engine.step(self.bot, self.user, UserInput.Text('help'))
        self.assertEquals(self.user.session.node_id, get_node_id('root'))
        self.assertEquals(self.user.session.message_sent, True)

        # Try invalid global command in root_node_id
        engine.step(self.bot, self.user, UserInput.Text('blablabla'))
        self.assertEquals(self.user.session.node_id, get_node_id('root'))
        self.assertEquals(self.user.session.message_sent, True)

        # Try global gotoA command
        engine.step(self.bot, self.user, UserInput.Text('gotoA'))
        self.assertEquals(self.user.session.node_id, get_node_id('nodeA'))
        self.assertEquals(self.user.session.message_sent, True)

        # Try global gotoD command
        engine.step(self.bot, self.user, UserInput.Text('gotoD'))
        self.assertEquals(self.user.session.node_id, get_node_id('nodeD'))

        engine.step(self.bot, self.user, UserInput.Text('gotoE'))
        self.assertEquals(self.user.session.message_sent, True)
        self.assertEquals(self.user.session.node_id, get_node_id('root'))

    def test_postback(self):
        self.setup_prerequisite('test/postback.bot')

        engine = Engine()

        def get_node_id(name):
            return Node.get_by(name=unicode(name), single=True).id

        engine.step(self.bot, self.user)  # start display
        self.assertEquals(self.user.session.node_id, get_node_id('root'))

        # We should now be in root node
        engine.step(self.bot, self.user)  # root display
        self.assertEquals(self.user.session.message_sent, True)

        postback = {
            'postback': {
                'payload': '{"message": {"text": "PAYLOAD_TEXT"}, '
                           '"node_id": %d}' % get_node_id('postback')
            }
        }

        # Try postback
        engine.step(self.bot, self.user,
                    UserInput.FromFacebookMessage(postback))
        self.assertEquals(self.user.session.node_id, get_node_id('show'))
        self.assertEquals(self.user.session.message_sent, True)

        sent_msg = self.send_message_mock.call_args[0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'PAYLOAD_TEXT')

        # Use global postback command to goto postback node
        engine.step(self.bot, self.user, UserInput.Text('postback'))
        self.assertEquals(self.user.session.node_id, get_node_id('postback'))
        self.assertEquals(self.user.session.message_sent, True)

        engine.step(self.bot, self.user, UserInput.Text('TEXT'))
        self.assertEquals(self.user.session.node_id, get_node_id('show'))
        self.assertEquals(self.user.session.message_sent, True)

        sent_msg = self.send_message_mock.call_args[0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'TEXT')

    def test_input_transformation(self):
        """Test input transformation.

        If input transformation is set. Test that the user input is correctly
        transformed then tirgger the actually parser rule.
        """
        self.setup_prerequisite('test/input_transformation.bot')

        engine = Engine()

        def get_node_id(name):
            return Node.get_by(name=unicode(name), single=True).id

        engine.step(self.bot, self.user)  # start display
        self.assertEquals(self.user.session.node_id, get_node_id('root'))

        # We should now be in root node
        engine.step(self.bot, self.user)  # root display
        self.assertEquals(self.user.session.message_sent, True)

        # Button title should work
        engine.step(self.bot, self.user, UserInput.Text('option 1'))
        self.assertEquals(self.user.session.node_id, get_node_id('option1'))
        self.assertEquals(self.user.session.message_sent, True)
        sent_msg = self.send_message_mock.call_args[0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'payload1')

        # Back to root
        engine.step(self.bot, self.user)
        self.assertEquals(self.user.session.node_id, get_node_id('root'))

        # acceptable_inputs should work
        engine.step(self.bot, self.user, UserInput.Text('D'))
        self.assertEquals(self.user.session.node_id, get_node_id('option2'))
        self.assertEquals(self.user.session.message_sent, True)
        sent_msg = self.send_message_mock.call_args[0][1][0]
        self.assertEquals(sent_msg.as_dict()['text'], 'payload2')

        # Back to root
        engine.step(self.bot, self.user)
        self.assertEquals(self.user.session.node_id, get_node_id('root'))

        # numbers should work
        engine.step(self.bot, self.user, UserInput.Text('1'))
        self.assertEquals(self.user.session.node_id, get_node_id('option1'))
        self.assertEquals(self.user.session.message_sent, True)


if __name__ == '__main__':
    with app.test_request_context():
        unittest.main()
