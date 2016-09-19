# -*- coding: utf-8 -*-
"""
    No operation
    ~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.content.core.noop',
        'name': 'No operation',
        'description': 'Do nothing',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'noop',
        'ui_module_name': 'noop',
    }


def schema():
    return {
        'type': 'object'
    }


def run(unused_content_config, unused_env, unused_variables):
    return []
