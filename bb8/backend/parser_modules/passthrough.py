# -*- coding: utf-8 -*-
"""
    Passthrough module
    ~~~~~~~~~~~~~~~~~~

    Pass through next node without any action.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import ParseResult, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.parser.core.passthrough',
        'name': 'Passthrough',
        'description': 'Passthrough to the next node without any response.',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'passthrough',
        'ui_module_name': 'passthrough',
        'variables': [],
    }


def schema():
    return {
        'type': 'object',
        'required': ['end_node_id', 'ack_message'],
        'additionalProperties': False,
        'properties': {
            'end_node_id': {'type': 'string'},
            'ack_message': {'type': 'string'}
        }
    }


def run(parser_config, unused_user_input, unused_as_root):
    return ParseResult(parser_config['end_node_id'])


def get_linkages(parser_config):
    return [parser_config['end_node_id']]
