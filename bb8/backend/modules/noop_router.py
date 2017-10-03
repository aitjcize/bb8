# -*- coding: utf-8 -*-
"""
    No operation Router
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import (SupportedPlatform, ModuleTypeEnum,
                                    RouteResult)


def properties():
    return {
        'id': 'ai.compose.router.core.noop',
        'type': ModuleTypeEnum.Router,
        'name': 'No operation router',
        'description': 'Do nothing',
        'supported_platform': SupportedPlatform.All,
        'variables': [],
    }


def schema():
    return {
        'type': 'object',
        'properties': {
            'next_node_id': {'type': 'string'}
        }
    }


def run(config, unused_user_input, unused_as_root):
    return RouteResult(config['next_node_id'], '', {}, errored=False)


def get_linkages(unused_config):
    return []
