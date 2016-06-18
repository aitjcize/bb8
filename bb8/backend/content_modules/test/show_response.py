# -*- coding: utf-8 -*-
"""
    Show response from variables
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, Resolve, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.test.show_response',
        'name': 'show response',
        'description': 'show response',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'test.show_response',
        'ui_module_name': 'show_response',
    }


def schema():
    return {
        'type': 'object',
        'required': ['response'],
        'properties': {
            'response': {'type': 'string'}
        }
    }


def run(content_config, unused_env, variables):
    """
    content_config schema:
    {
       "response": "{{variable}",
    }
    """
    m = Message(Resolve(content_config['response'], variables))
    return [m]
