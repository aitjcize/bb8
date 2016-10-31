# -*- coding: utf-8 -*-
"""
    Send generic messages
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.content.core.generic_message',
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
                'oneOf': [{
                    'type': 'array',
                    'items': Message.schema()
                }, {
                    'type': 'object',
                    'required': ['Facebook', 'Line'],
                    'additionalProperties': False,
                    'properties': {
                        'Facebook': {
                            'type': 'array',
                            'items': Message.schema()
                        },
                        'Line': {
                            'type': 'array',
                            'items': Message.schema()
                        }
                    }
                }]
            },
            'quick_replies': {
                'type': 'array',
                'items': {'$ref': '#/definitions/quick_reply'}
            }
        },
        'definitions': {
            'button': Message.Button.schema(),
            'bubble': Message.Bubble.schema(),
            'quick_reply': Message.QuickReply.schema()
        }
    }


def run(content_config, env, variables):
    """
    content_config schema:

    Platform independent message:
    {
        'messages': [Message, ...]
    }

    Platform dependent message:
    {
        'message': {
            'Facebook': [Message,  ... ]
            'Line': [Message, ... ]
            ...
        }
    }
    """
    messages = content_config.get('messages')
    msgs = []

    if not isinstance(messages, list):
        platform_type = env['platform_type'].value
        messages = messages[platform_type]

    for message in messages:
        msgs.append(Message.FromDict(message, variables))

    for quick_reply in content_config.get('quick_replies', []):
        msgs[-1].add_quick_reply(Message.QuickReply.FromDict(quick_reply))

    return msgs
