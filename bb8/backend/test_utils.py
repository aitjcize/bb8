# -*- coding: utf-8 -*-
"""
    Backend test utilities
    ~~~~~~~~~~~~~~~~~~~~~~

    Provide common test utilities for unittest

    Copyright 2016 bb8 Authors
"""

from bb8.backend.database import DatabaseManager

from bb8.backend.bot_parser import get_bot_filename, parse_bot
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
