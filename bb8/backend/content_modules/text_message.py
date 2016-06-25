# -*- coding: utf-8 -*-
"""
    Send a text message
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.core.text_message',
        'name': 'Text message',
        'description': 'Show text-only message',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'text_message',
        'ui_module_name': 'text_message',
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
            }
        },
        "definitions": {
            "messages": {
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
            }
        }
    }


def run(content_config, env, variables):
    """
    content_config schema:

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
    text = content_config['text']

    if not isinstance(text, list):
        text = [text]

    # Platform independent message
    if not isinstance(text[0], dict):
        return [Message(t, variables=variables) for t in text]

    platform_type = env['platform_type'].value
    return [Message(t[platform_type], variables=variables) for t in text]
