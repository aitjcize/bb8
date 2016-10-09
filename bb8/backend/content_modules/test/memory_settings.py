# -*- coding: utf-8 -*-
"""
    Test User.memory and User.settings Operations
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, Memory, Settings, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.content.test.memory_settings',
        'name': 'Memory & Settings',
        'description': 'Test user memory and settings',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'test.memory_settings',
        'ui_module_name': 'memory_settings',
    }


def schema():
    return {
        'type': 'object',
        'required': ['mode'],
        'properties': {
            'mode': {'enum': ['set', 'get', 'clear']},
            'target': {'enum': ['memory', 'settings']},
            'data': {'type': 'string'}
        }
    }


def run(content_config, unused_env, unused_variables):
    if content_config['target'] == 'memory':
        target = Memory
    else:
        target = Settings

    if content_config['mode'] == 'set':
        target.Set('data', content_config['data'])
    elif content_config['mode'] == 'get':
        return [Message(target.Get('data'))]
    elif content_config['mode'] == 'clear':
        target.Clear()

    return []
