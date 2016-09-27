# -*- coding: utf-8 -*-
"""
    Settings
    ~~~~~~~~

    Apply settings according to module config.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import SupportedPlatform, Render, Settings, Message


def get_module_info():
    return {
        'id': 'ai.compose.content.core.settings',
        'name': 'Settings',
        'description': 'Apply settings to user',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'settings',
        'ui_module_name': 'settings',
    }


def schema():
    return {
        'type': 'object',
        'required': ['settings', 'message'],
        'properties': {
            'settings': {'type': 'object'},
            'message': {'type': 'string'}
        }
    }


def run(content_config, unused_env, variables):
    """
    content_config schema:
    {
        "settings": {
            "key1": "value1",
            "key2": "value2",
        },
        "message": "message"
    }
    """

    for key, value in content_config['settings'].iteritems():
        if isinstance(value, str):
            value = Render(value, variables)
        Settings.Set(key, value)

    return [Message(content_config['message'], variables=variables)]
