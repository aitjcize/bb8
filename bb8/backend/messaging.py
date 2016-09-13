# -*- coding: utf-8 -*-
"""
    Messaging API
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8 import config, logger
from bb8.backend.database import (Conversation, User, PlatformTypeEnum,
                                  SenderEnum)
from bb8.backend.module_api import Message
from bb8.backend.messaging_provider import facebook, line


def get_messaging_provider(platform_type):
    if platform_type == PlatformTypeEnum.Facebook:
        return facebook
    elif platform_type == PlatformTypeEnum.Line:
        return line


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


def get_user_profile(platform, user_ident):
    provider = get_messaging_provider(platform.type_enum)
    return provider.get_user_profile(platform, user_ident)


def broadcast_message(bot, messages):
    for user in User.get_by(bot_id=bot.id):
        try:
            logger.info('Sending message to %s ...' % user)
            send_message(user, messages)
        except Exception as e:
            logger.exception(e)
