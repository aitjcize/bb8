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
            }
        }
    }


def run(content_config, env, unused_variables):
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
    messages = content_config.get('messages', None)
    msgs = []

    if not isinstance(messages, list):
        platform_type = env['platform_type'].value
        messages = messages[platform_type]

    for message in messages:
        msgs.append(Message.FromDict(message))
    return msgs
