# -*- coding: utf-8 -*-
"""
    Literal test parser module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Return what user input as action_ident.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem


def get_module_info():
    return {
        'id': 'ai.compose.test.literal',
        'name': 'Literal',
        'description': 'Return user input as action_ident.',
        'module_name': 'test.literal',
        'ui_module_name': 'literal',
        'variables': [],
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
