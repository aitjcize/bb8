#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Engine unittest
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest
import datetime

import pytz

from bb8.backend.database import DatabaseManager
from bb8.backend.database import Bot, Node, Platform, User

from bb8.backend import messaging
from bb8.backend.engine import Engine
from bb8.backend.metadata import UserInput
from bb8.backend.module_registration import register_all_modules
from bb8.backend.bot_parser import get_bot_filename, parse_bot


class EngineUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = DatabaseManager()
        self.dbm.connect()
        self.setup_prerequisite()

    def tearDown(self):
        self.dbm.disconnect()

    def setup_prerequisite(self):
        self.dbm.reset()

        # Register all modules
        register_all_modules()

        # Construct test bot
        parse_bot(get_bot_filename('test/simple.bot'))

        self.bot = Bot.get_by(id=1, single=True)

        self.user = User(bot_id=self.bot.id,
                         platform_id=Platform.get_by(id=1, single=True).id,
                         platform_user_ident='blablabla',
                         last_seen=datetime.datetime(2016, 6, 2, 12, 44, 56,
                                                     tzinfo=pytz.utc)).add()

        self.dbm.commit()

    def test_simple_graph(self):
        """Test a simple graph (test/simple.bot)

        start -----> root -- > D --> E
                      |
                      v
                      A --> B --> C
                      .           ^
                       `----------`
        """
        engine = Engine()

        # Override module API method for testing
        context = {'message_sent': False}

        def send_message_mock(unused_user, unused_x):
            context['message_sent'] = True

        messaging.send_message = send_message_mock

        def get_node_id(name):
            return Node.get_by(name=name, single=True).id

        engine.step(self.bot, self.user)  # start display
        self.assertEquals(self.user.session.node_id, get_node_id('root'))

        # We should now be in root node
        engine.step(self.bot, self.user)  # root display
        self.assertEquals(self.user.session.message_sent, True)

        # Try global gotoA command
        context['message_sent'] = False
        engine.step(self.bot, self.user, UserInput.Text('gotoA'))
        self.assertEquals(self.user.session.node_id, get_node_id('nodeA'))
        self.assertEquals(self.user.session.message_sent, True)
        self.assertEquals(context['message_sent'], True)

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


if __name__ == '__main__':
    unittest.main()
