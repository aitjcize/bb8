# -*- coding: utf-8 -*-
"""
    Test User.memory and User.settings Operations
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import (Message, Memory, Settings,
                                    SupportedPlatform, PureContentModule,
                                    ModuleTypeEnum)


def properties():
    return {
        'id': 'ai.compose.content.test.memory_settings',
        'type': ModuleTypeEnum.Content,
        'name': 'Memory & Settings',
        'description': 'Test user memory and settings',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
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


@PureContentModule
def run(config, unused_user_input, unused_env, unused_variables):
    if config['target'] == 'memory':
        target = Memory
    else:
        target = Settings

    if config['mode'] == 'set':
        target.Set('data', config['data'])
    elif config['mode'] == 'get':
        return [Message(target.Get('data'))]
    elif config['mode'] == 'clear':
        target.Clear()

    return []
