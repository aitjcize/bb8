# -*- coding: utf-8 -*-
"""
    Messaging API
    ~~~~~~~~~~~~~

    Provides a provider-independent messaging API.

    Copyright 2016 bb8 Authors
"""

import time

from bb8 import config
from bb8.backend.database import Conversation, PlatformTypeEnum, SenderEnum
from bb8.backend.messaging_provider import facebook, line


def store_conversation(user, messages, sender=None):
    if config.STORE_CONVERSATION:
        sender_enum = SenderEnum.Bot if not sender else SenderEnum.Manual
        for message in messages:
            Conversation(user_id=user.id,
                         sender_enum=sender_enum,
                         sender=sender,
                         messages=message.as_dict(),
                         timestamp=time.time()).add()


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
    store_conversation(user, messages)


def flush_message(user):
    """Flush the message in the send queue."""
    provider = get_messaging_provider(user.platform.type_enum)
    provider.flush_message(user)


def push_message(user, messages, sender=None):
    """Push message to user proactively."""
    if not isinstance(messages, list):
        messages = [messages]

    provider = get_messaging_provider(user.platform.type_enum)
    provider.push_message(user, messages)
    store_conversation(user, messages, sender)


def download_audio_as_data(user, audio_payload):
    """Download audio file as data."""
    provider = get_messaging_provider(user.platform.type_enum)
    return provider.download_audio_as_data(user, audio_payload)
