# -*- coding: utf-8 -*-
"""
    Literal test parser module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Return what user input as action_ident.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.test.literal',
        'name': 'Literal',
        'description': 'Return user input as action_ident.',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'test.literal',
        'ui_module_name': 'literal',
        'variables': [],
    }


def schema():
    return {
        'type': 'object',
        'required': ['links'],
        'additionalProperties': False,
        'properties': {
            'links': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'required': ['action_ident', 'end_node_id', 'ack_message'],
                    'additionalProperties': False,
                    'properties': {
                        'action_ident': {'type': 'string'},
                        'end_node_id': {'type': ['integer', 'null']},
                        'ack_message': {'type': 'string'}
                    }
                }
            }
        }
    }


def run(parser_config, user_input):
    text = user_input.text
    if text in [x['action_ident'] for x in parser_config['links']]:
        return text, {}
    return '$error', {}


def get_linkages(parser_config):
    links = []
    links.append(LinkageItem('$error', None,
                             'Invalid command, please re-enter.'))
    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))
    return links
