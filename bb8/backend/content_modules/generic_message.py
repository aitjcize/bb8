# -*- coding: utf-8 -*-
"""
    Send generic messages
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.core.generic_message',
        'name': 'Generic message',
        'description': 'Show generic message',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'generic_message',
        'ui_module_name': 'generic_message',
    }


def schema():
    return {
        'type': 'object',
        'required': ['messages'],
        'additionalProperties': False,
        'properties': {
            'messages': {
                'type': 'array',
                'items': Message.schema()
            }
        }
    }


def run(content_config, unused_env, unused_variables):
    """
    content_config schema

    {
        'messages': [Message schema, ...]
    }
    """
    messages = content_config.get('messages', None)
    msgs = []
    if messages:
        for message in messages:
            msgs.append(Message.FromDict(message))
    return msgs
