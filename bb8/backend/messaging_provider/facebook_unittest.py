#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Messaging unittest
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from bb8.backend.database import DatabaseManager
from bb8.backend.database import Bot, Platform, PlatformTypeEnum, User
from bb8.backend.messaging import Message
from bb8.backend.messaging_provider import facebook


class Facebook(unittest.TestCase):
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

        self.bot = Bot(name='test', description='test',
                       interaction_timeout=120, session_timeout=86400).add()
        self.dbm.commit()

        config = {
            'access_token': 'EAAP0okfsZCVkBANNgGSRPG0fsOWJKSQCNegqX8s1qxS7bVd'
                            'AIsfofqEeoiTtVm11Xgy5vm0MQGHyGtji5AwAXSQTQMAfZBu'
                            'awZCfy4prQ7IZBoTFyu8EGAYRGFZBwcgBjU2sXUtFMNbzp1M'
                            '9mMfTNZBdfjjRe3S0PM08vvCYkQ6QZDZD'
        }
        self.platform = Platform(bot_id=self.bot.id,
                                 type_enum=PlatformTypeEnum.Facebook,
                                 provider_ident='facebook_page_id',
                                 config=config).add()
        self.dbm.commit()

        self.user = User(bot_id=self.bot.id,
                         platform_id=self.platform.id,
                         platform_user_ident='1153206858057166',
                         last_seen=1464871496).add()

        self.dbm.commit()

    def test_send_message(self):
        """Test facebook message sending."""

        # Test simple text message
        m = Message('test')
        facebook.send_message(self.user, [m])

        # Test image message
        m = Message(image_url='http://i.imgur.com/4loi6PJ.jpg')
        facebook.send_message(self.user, [m])

        # Test card message
        m = Message()
        bubble = Message.Bubble('Bubble Test',
                                'http://www.starwars.com/',
                                'http://i.imgur.com/4loi6PJ.jpg',
                                'Bubble subtitle')
        bubble.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                         'Starwars',
                                         url='http://www.starwars.com/'))
        bubble.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                         'Google',
                                         url='http://www.google.com/'))
        bubble.add_button(Message.Button(Message.ButtonType.WEB_URL,
                                         '17',
                                         url='http://www.17.media/'))
        m.add_bubble(bubble)
        m.add_bubble(bubble)
        m.add_bubble(bubble)

        facebook.send_message(self.user, [m])


if __name__ == '__main__':
    unittest.main()
