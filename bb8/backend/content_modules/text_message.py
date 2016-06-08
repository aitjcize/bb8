# -*- coding: utf-8 -*-
"""
    Send a text message
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message


def get_module_info():
    return {
        'id': 'ai.compose.core.text_message',
        'name': 'Text message',
        'description': 'Show text-only message',
        'module_name': 'text_message',
        'ui_module_name': 'text_message',
    }


def run(content_config, unused_env, unused_variables):
    text = content_config.get('text', None)
    if text:
        return [Message(text)]
    return []
