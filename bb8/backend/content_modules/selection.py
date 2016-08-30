# -*- coding: utf-8 -*-
"""
    Show a selection message
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, SupportedPlatform, TextPayload


def get_module_info():
    return {
        'id': 'ai.compose.core.selection',
        'name': 'Selection',
        'description': 'Show a selection message',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'selection',
        'ui_module_name': 'selection',
    }


def schema():
    return {
        'type': 'object',
        'additionalProperties': False,
        'required': ['text', 'choices'],
        'properties': {
            'text': {'type': 'string'},
            'choices': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'required': ['title', 'payload', 'acceptable_inputs'],
                    'additionalProperties': False,
                    'properties': {
                        'title': {'type': 'string'},
                        'payload': {'type': 'string'},
                        'acceptable_inputs': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                }
            }
        },
    }


def run(content_config, env, variables):
    """
    content_config schema:

    Platform dependent message:
    {
        'text': 'blablabla',
        'choices': [
            {
                'title': 'option 1',
                'payload': '1',
                'acceptable_inputs': ['opt 1']
            },
            ...
        ]
    }
    """
    platform_type = env['platform_type'].value

    m = Message(buttons_text=content_config['text'], variables=variables)

    for i, choice in enumerate(content_config['choices']):
        # Facebook only support 3 buttons
        if i == 3 and platform_type == SupportedPlatform.Facebook:
            break

        b = Message.Button(Message.ButtonType.POSTBACK,
                           choice['title'],
                           payload=TextPayload(choice['payload']),
                           acceptable_inputs=choice['acceptable_inputs'],
                           variables=variables)
        m.add_button(b)

    return [m]
