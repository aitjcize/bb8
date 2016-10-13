# -*- coding: utf-8 -*-
"""
    Messaging API
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from datetime import datetime, timedelta

import pytz

from flask import g

from bb8 import app, config, logger, celery
from bb8.backend.database import (Conversation, DatabaseSession, User,
                                  Platform, PlatformTypeEnum, SenderEnum)
from bb8.backend.message import Message
from bb8.backend.messaging_provider import facebook, line


def get_messaging_provider(platform_type):
    if platform_type == PlatformTypeEnum.Facebook:
        return facebook
    elif platform_type == PlatformTypeEnum.Line:
        return line


def get_user_profile(platform, user_ident):
    provider = get_messaging_provider(platform.type_enum)
    return provider.get_user_profile(platform, user_ident)


def send_message(user, messages):
    if isinstance(messages, Message):
        messages = [messages]

    provider = get_messaging_provider(user.platform.type_enum)
    provider.send_message(user, messages)

    if config.STORE_CONVERSATION:
        for message in messages:
            Conversation(bot_id=user.bot_id,
                         user_id=user.id,
                         sender_enum=SenderEnum.Bot,
                         msg=message.as_dict()).add()


@celery.task
def push_message(user, messages):
    if isinstance(messages, Message):
        messages = [messages]

    with DatabaseSession():
        user.refresh()

        provider = get_messaging_provider(user.platform.type_enum)
        provider.push_message(user, messages)

        if config.STORE_CONVERSATION:
            for message in messages:
                Conversation(bot_id=user.bot_id,
                             user_id=user.id,
                             sender_enum=SenderEnum.Bot,
                             msg=message.as_dict()).add()


def push_message_async(user, messages):
    push_message.apply_async((user, messages))


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
            if eta:
                base_eta = datetime.utcfromtimestamp(eta)
                user = users[0]
                user.refresh()
                tz = user.platform.account.timezone
                account_tz_offset = int(pytz.timezone(tz).localize(
                    datetime.now()).strftime('%z')) / 100

            user_count = User.count()

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
                    'statistic': {
                        'user_count': user_count
                    },
                    'user': user.to_json()
                }
                msgs = [Message.FromDict(m, variables) for m in messages_dict]
                push_message.apply_async((user, msgs), eta=eta)


def push_message_from_dict_async(users, messages_dict, eta=None,
                                 user_localtime=False):
    """Send messages to users from a list of dictionary."""
    _push_message_from_dict.apply_async((users, messages_dict, eta,
                                         user_localtime))


@celery.task
def _broadcast_message(bot, messages, eta=None):
    """Broadcast message to bot users.

    This method should never be called directly. It should be always called
    asynchronously by broadcast_message_async().
    """
    with DatabaseSession():
        platform_ids = [p.id for p in Platform.get_by(bot_id=bot.id)]
        if not platform_ids:  # No associated platform
            return

        users = User.query().filter(
            User.platform_id.in_(platform_ids)).all()
        for user in users:
            if not user.settings.get('subscribe', True):
                continue
            try:
                logger.info('Sending message to %s ...' % user)
                push_message.apply_async((user, messages),
                                         eta=datetime.utcfromtimestamp(eta))
            except Exception as e:
                logger.exception(e)


def broadcast_message_async(bot, messages, eta=None):
    """Broadcast message to bot users."""
    _broadcast_message.apply_async((bot, messages, eta))
