# -*- coding: utf-8 -*-
"""
    Messaging API
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import g

from bb8 import app, config, logger, celery
from bb8.backend.database import (Conversation, DatabaseSession, User,
                                  PlatformTypeEnum, SenderEnum)
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


@celery.task
def send_message(user, messages):
    if isinstance(messages, Message):
        messages = [messages]

    def send_message_(user, messages):
        provider = get_messaging_provider(user.platform.type_enum)
        provider.send_message(user, messages)

        if config.STORE_CONVERSATION:
            for message in messages:
                Conversation(bot_id=user.bot_id,
                             user_id=user.id,
                             sender_enum=SenderEnum.Bot,
                             msg=message.as_dict()).add()

    if user.has_session():
        send_message_(user, messages)
    else:
        # If user does not have session, means we are running in a celery
        # task and the object is detached, merge it back to the session.
        with DatabaseSession():
            user.refresh()
            send_message_(user, messages)


def send_message_async(user, messages):
    send_message.apply_async((user, messages))


@celery.task
def _send_message_from_dict(users, messages_dict):
    """Send messages to users from a list of dictionary.

    This method should never be called directly. It should be always called
    asynchronously by send_message_from_dict_async().
    """
    with app.test_request_context():
        with DatabaseSession():
            user_count = User.count()
            for user in users:
                user.refresh()
                g.user = user
                variables = {
                    'statistic': {
                        'user_count': user_count
                    },
                    'user': user.to_json()
                }
                msgs = [Message.FromDict(m, variables) for m in messages_dict]
                send_message.apply_async((user, msgs))


def send_message_from_dict_async(users, messages_dict):
    """Send messages to users from a list of dictionary."""
    _send_message_from_dict.apply_async((users, messages_dict))


@celery.task
def _broadcast_message(bot, messages):
    """Broadcast message to bot users.

    This method should never be called directly. It should be always called
    asynchronously by broadcast_message_async().
    """
    with DatabaseSession():
        for user in User.get_by(bot_id=bot.id):
            try:
                logger.info('Sending message to %s ...' % user)
                send_message_async(user, messages)
            except Exception as e:
                logger.exception(e)


def broadcast_message_async(bot, messages):
    """Broadcast message to bot users."""
    _broadcast_message.apply_async((bot, messages))
