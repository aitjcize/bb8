# -*- coding: utf-8 -*-
"""
    Send messages
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import (Message, SupportedPlatform,
                                    PureContentModule, ModuleTypeEnum)


def properties():
    return {
        'id': 'ai.compose.content.core.message',
        'type': ModuleTypeEnum.Content,
        'name': 'message',
        'description': 'Send messages',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
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
            'default_action': Message.DefaultAction.schema(),
            'list_item': Message.ListItem.schema(),
            'quick_reply': Message.QuickReply.schema()
        }
    }


@PureContentModule
def run(config, unused_input, env, variables):
    """
    config schema:

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
    messages = config.get('messages')
    msgs = []

    if not isinstance(messages, list):
        platform_type = env['platform_type'].value
        messages = messages[platform_type]

    for message in messages:
        msgs.append(Message.FromDict(message, variables))

    for quick_reply in config.get('quick_replies', []):
        msgs[-1].add_quick_reply(Message.QuickReply.FromDict(quick_reply))

    return msgs
