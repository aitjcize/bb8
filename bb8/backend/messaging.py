# -*- coding: utf-8 -*-
"""
    Messaging API
    ~~~~~~~~~~~~~

    Provides a provider-independent messaging API.

    Copyright 2016 bb8 Authors
"""

from bb8 import config
from bb8.backend.database import Conversation, PlatformTypeEnum, SenderEnum
from bb8.backend.messaging_provider import facebook, line


def get_messaging_provider(platform_type):
    if platform_type == PlatformTypeEnum.Facebook:
        return facebook
    elif platform_type == PlatformTypeEnum.Line:
        return line


def get_user_profile(platform, user_ident):
    """Get user profile."""
    provider = get_messaging_provider(platform.type_enum)
    return provider.get_user_profile(platform, user_ident)


def send_message(user, messages):
    """Send message to user."""
    if not isinstance(messages, list):
        messages = [messages]

    provider = get_messaging_provider(user.platform.type_enum)
    provider.send_message(user, messages)

    if config.STORE_CONVERSATION:
        for message in messages:
            Conversation(bot_id=user.bot_id,
                         user_id=user.id,
                         sender_enum=SenderEnum.Bot,
                         msg=message.as_dict()).add()


def push_message(user, messages):
    """Push message to user proactively."""
    if not isinstance(messages, list):
        messages = [messages]

    provider = get_messaging_provider(user.platform.type_enum)
    provider.push_message(user, messages)

    if config.STORE_CONVERSATION:
        for message in messages:
            Conversation(bot_id=user.bot_id,
                         user_id=user.id,
                         sender_enum=SenderEnum.Bot,
                         msg=message.as_dict()).add()


def download_audio_as_data(user, audio_payload):
    """Download audio file as data."""
    provider = get_messaging_provider(user.platform.type_enum)
    return provider.download_audio_as_data(user, audio_payload)
