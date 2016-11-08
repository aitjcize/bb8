
# -*- coding: utf-8 -*-
"""
    Messaging Celery Tasks
    ~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from datetime import datetime, timedelta

import pytz

from flask import g

from bb8 import app, logger, celery
from bb8.backend import messaging
from bb8.backend.database import DatabaseSession
from bb8.backend.message import Message


def _get_account_timezone_offset(account):
    return int(pytz.timezone(account.timezone).localize(
        datetime.now()).strftime('%z')) / 100


@celery.task
def push_message(user, messages):
    with DatabaseSession():
        user.refresh()
        messaging.push_message(user, messages)


@celery.task
def _push_message_from_dict(users, messages_dict, eta=None,
                            user_localtime=False):
    """Send messages to users from a list of dictionary.

    This method should never be called directly. It should be always called
    asynchronously by push_message_from_dict_async().
    """
    if not users or not messages_dict:
        return

    with app.test_request_context():
        with DatabaseSession():
            user = users[0]
            user.refresh()

            if eta:
                base_eta = datetime.utcfromtimestamp(eta)
                account_tz_offset = _get_account_timezone_offset(
                    user.platform.account)

            bot_id = user.platform.bot.id

            for user in users:
                if not user.settings.get('subscribe', True):
                    continue

                if eta:
                    eta = base_eta
                    if user_localtime:
                        tz_offset = account_tz_offset - user.timezone
                        eta += timedelta(hours=tz_offset)
                else:
                    eta = None

                user.refresh()
                g.user = user
                variables = {
                    'user': user.to_json(),
                    'bot_id': bot_id
                }
                msgs = [Message.FromDict(m, variables) for m in messages_dict]
                push_message.apply_async((user, msgs), eta=eta)


def push_message_from_dict_async(users, messages_dict, eta=None,
                                 user_localtime=False):
    """Send messages to users from a list of dictionary.

    Args:
        eta: Unix timestamp
    """
    _push_message_from_dict.apply_async((users, messages_dict, eta,
                                         user_localtime))


@celery.task
def _broadcast_message(bot, messages):
    """Broadcast message to bot users.

    This method should never be called directly. It should be always called
    asynchronously by broadcast_message_async().
    """
    with DatabaseSession():
        for user in bot.users:
            if not user.settings.get('subscribe', True):
                continue
            try:
                logger.info('Sending message to %s ...' % user)
                push_message.apply_async((user, messages))
            except Exception as e:
                logger.exception(e)


def broadcast_message_async(bot, messages, eta=None):
    """Broadcast message to bot users.

    Args:
        eta: Unix timestamp
    """
    if eta:
        eta = datetime.fromtimestamp(eta)
    _broadcast_message.apply_async((bot, messages), eta=eta)
