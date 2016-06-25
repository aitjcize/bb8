# -*- coding: utf-8 -*-
"""
    Passthrough module
    ~~~~~~~~~~~~~~~~~~

    Pass through next node without any action.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.core.passthrough',
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
            'end_node_id': {'type': 'integer'},
            'ack_message': {'type': 'string'}
        }
    }


def run(unused_parser_config, unused_user_input):
    return ('next', {}, {})


def get_linkages(parser_config):
    links = []
    links.append(LinkageItem('next', parser_config['end_node_id'],
                             parser_config['ack_message']))
    return links
