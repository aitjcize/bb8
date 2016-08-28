# -*- coding: utf-8 -*-
"""
    Backend test utilities
    ~~~~~~~~~~~~~~~~~~~~~~

    Provide common test utilities for unittest

    Copyright 2016 bb8 Authors
"""

import datetime

import pytz

from bb8.backend.bot_parser import get_bot_filename, parse_bot
from bb8.backend.database import (DatabaseManager, Bot, User, Platform,
                                  PlatformTypeEnum)
from bb8.backend.module_registration import register_all_modules


def reset_and_setup_bots(bot_names):
    """Reset database and setup bots.

    Args:
        bot_names: a list of bot names to setup
    """
    DatabaseManager.reset()
    bots = []
    register_all_modules()
    for bot_name in bot_names:
        bots.append(parse_bot(get_bot_filename(bot_name)))
    return bots


class BaseMessagingMixin(object):
    """A mixin for setting up prerequisite for messaging related unittests."""
    def setup_prerequisite(self):
        DatabaseManager.reset()

        self.bot = Bot(name=u'test', description=u'test',
                       interaction_timeout=120, session_timeout=86400).add()
        DatabaseManager.flush()

        self.platform = Platform(bot_id=self.bot.id,
                                 type_enum=PlatformTypeEnum.Facebook,
                                 provider_ident='facebook_page_id',
                                 config={}).add()
        DatabaseManager.flush()

        self.user_1 = User(bot_id=self.bot.id,
                           platform_id=self.platform.id,
                           platform_user_ident='1153206858057166',
                           last_seen=datetime.datetime(2016, 6, 2, 12, 44, 56,
                                                       tzinfo=pytz.utc)).add()
        self.user_2 = User(bot_id=self.bot.id,
                           platform_id=self.platform.id,
                           platform_user_ident='1318395614844436',
                           last_seen=datetime.datetime(2016, 6, 2, 12, 44, 56,
                                                       tzinfo=pytz.utc)).add()
        DatabaseManager.commit()
