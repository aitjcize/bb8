# -*- coding: utf-8 -*-
"""
    No operation
    ~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import (SupportedPlatform, PureContentModule,
                                    ModuleTypeEnum)


def properties():
    return {
        'id': 'ai.compose.content.core.noop',
        'type': ModuleTypeEnum.Content,
        'name': 'No operation',
        'description': 'Do nothing',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
    }


def schema():
    return {
        'type': 'object'
    }


@PureContentModule
def run(unused_content_config, unused_env, unused_variables):
    return []
