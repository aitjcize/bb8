# -*- coding: utf-8 -*-
"""
    Show response from variables
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import (Message, Resolve, SupportedPlatform,
                                    PureContentModule, ModuleTypeEnum)


def properties():
    return {
        'id': 'ai.compose.content.test.show_response',
        'type': ModuleTypeEnum.Content,
        'name': 'show response',
        'description': 'show response',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
    }


def schema():
    return {
        'type': 'object',
        'required': ['response'],
        'properties': {
            'response': {'type': 'string'}
        }
    }


@PureContentModule
def run(config, unused_user_input, unused_env, variables):
    """
    config schema:
    {
       "response": "{{variable}",
    }
    """
    m = Message(Resolve(config['response'], variables))
    return [m]
