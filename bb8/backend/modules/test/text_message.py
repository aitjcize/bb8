# -*- coding: utf-8 -*-
"""
    Send a text message
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import (Message, SupportedPlatform,
                                    PureContentModule, ModuleTypeEnum)


def properties():
    return {
        'id': 'ai.compose.content.test.text_message',
        'type': ModuleTypeEnum.Content,
        'name': 'Text message',
        'description': 'Show text-only message',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
    }


def schema():
    return {
        'type': 'object',
        'required': ['text'],
        'additionalProperties': False,
        'properties': {
            'text': {
                'oneOf': [{
                    '$ref': '#/definitions/messages'
                }, {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/messages'}
                }]
            },
            'quick_replies': {
                'type': 'array',
                'items': {'$ref': '#/definitions/quick_reply'}
            }
        },
        'definitions': {
            'messages': {
                'oneOf': [{
                    'type': 'string'
                }, {
                    'type': 'object',
                    'required': ['Facebook', 'Line'],
                    'additionalProperties': False,
                    'properties': {
                        'Facebook': {'type': 'string'},
                        'Line': {'type': 'string'}
                    }
                }]
            },
            'quick_reply': Message.QuickReply.schema()
        }
    }


@PureContentModule
def run(config, unused_user_input, env, variables):
    """
    config schema:

    Platform independent message:
    {
        'text': 'text to send'
    }

    Platform dependent message:
    {
        'text': {
            'Facebook': 'text to send',
            'Line': 'text to send',
            ...
        }
    }
    """
    text = config['text']

    if not isinstance(text, list):
        text = [text]

    # Platform independent message
    if not isinstance(text[0], dict):
        msgs = [Message(t, variables=variables) for t in text]
    else:
        platform_type = env['platform_type'].value
        msgs = [Message(t[platform_type], variables=variables) for t in text]

    for qr in config.get('quick_replies', []):
        msgs[-1].add_quick_reply(
            Message.QuickReply.FromDict(qr, variables=variables))

    return msgs
