# -*- coding: utf-8 -*-
"""
    Generates Report
    ~~~~~~~~~~~~~~~~

    Generates report and relay it to bot amdins.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.database import User
from bb8.backend.metadata import ModuleResult
from bb8.backend.module_api import (Message, SupportedPlatform, Memory,
                                    ModuleTypeEnum, CollectedData)
from bb8.backend.messaging_tasks import push_message


def properties():
    return {
        'id': 'ai.compose.function.core.report',
        'type': ModuleTypeEnum.Function,
        'name': 'report',
        'description': 'Generates report',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
    }


def schema():
    return {
        'type': 'object',
        'required': ['admins', 'template', 'keys', 'report_key'],
        'additionalProperties': False,
        'properties': {
            'admins': {
                'type': 'array',
                'items': {'type': 'string'},
            },
            'template': {'type': 'string'},
            'keys': {
                'type': 'array',
                'items': {'type': 'string'},
            },
            'report_key': {'type': 'string'},
        },
    }


def run(config, unused_input, unused_env, variables):
    """
    config example:
    {
        'admins': ['12345', '67890'],
        'template': '{{key1}} bla bla bla',
        'keys': ['key1', 'key2', 'key3'],
        'report_key': 'application_form'
    }
    """
    data = {}
    for key in config['keys']:
        data[key] = Memory.Get(key, variables.get(key))

    CollectedData.Add(config['report_key'], data)

    variables.update(data)
    msg = Message(config['template'], variables=variables)

    for admin in config['admins']:
        user = User.get_by(platform_user_ident=admin, single=True)
        if user:
            push_message.apply_async((user, msg))

    return ModuleResult()
