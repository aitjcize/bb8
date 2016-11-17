# -*- coding: utf-8 -*-
"""
    Backend test utilities
    ~~~~~~~~~~~~~~~~~~~~~~

    Provide common test utilities for unittest

    Copyright 2016 bb8 Authors
"""

import datetime
import subprocess

import pytz

from bb8.backend.bot_parser import get_bot_filename, parse_bot_from_file
from bb8.backend.platform_parser import (get_platform_filename,
                                         parse_platform_from_file)
from bb8.backend.database import (DatabaseManager, Bot, User, Platform,
                                  PlatformTypeEnum)
from bb8.backend.modules import register_all


def reset_and_setup_bots(bot_names):
    """Reset database and setup bots.

    Args:
        bot_names: a list of bot names to setup
    """
    bots = []
    DatabaseManager.reset()
    register_all()
    for platform_name in ['dev/bb8.test.platform', 'dev/bb8.test2.platform']:
        parse_platform_from_file(get_platform_filename(platform_name))

    for bot_name in bot_names:
        bots.append(parse_bot_from_file(get_bot_filename(bot_name)))
    return bots


def start_celery_worker():
    return subprocess.Popen('celery -A bb8.celery worker --loglevel=info '
                            '--concurrency 4', shell=True)


def stop_celery_worker():
    subprocess.call('pkill -9 -f celery', shell=True)


class BaseTestMixin(object):
    """A mixin for setting up prerequisite for messaging related unittests."""
    def setup_prerequisite(self):
        DatabaseManager.reset()

        self.bot = Bot(name=u'test', description=u'test',
                       interaction_timeout=120, session_timeout=86400).add()
        DatabaseManager.flush()

        config = {
            'access_token': 'EAAP0okfsZCVkBAI3BCU5s3u8O0iVFh6NAwFHa7X2bKZCGQ'
                            'Lw6VYeTpeTsW5WODeDbekU3ZA0JyVCBSmXq8EqwL1GDuZBO'
                            '7aAlcNEHQ3AZBIx0ZBfFLh95TlJWlLrYetzm9owKNR8Qju8'
                            'HF6qra20ZC6HqNXwGpaP74knlNvQJqUmwZDZD'
        }

        self.platform = Platform(name=u'Test platform',
                                 bot_id=self.bot.id,
                                 type_enum=PlatformTypeEnum.Facebook,
                                 provider_ident='1155924351125985',
                                 config=config).add()
        DatabaseManager.flush()

        self.user_1 = User(platform_id=self.platform.id,
                           platform_user_ident='1153206858057166',
                           last_seen=datetime.datetime(2016, 6, 2, 12, 44, 56,
                                                       tzinfo=pytz.utc),
                           settings={'subscribe': True}).add()
        self.user_2 = User(platform_id=self.platform.id,
                           platform_user_ident='1318395614844436',
                           last_seen=datetime.datetime(2016, 6, 2, 12, 44, 56,
                                                       tzinfo=pytz.utc),
                           settings={'subscribe': True}).add()
        DatabaseManager.commit()
