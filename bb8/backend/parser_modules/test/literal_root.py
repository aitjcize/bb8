# -*- coding: utf-8 -*-
"""
    Literal Root test parser module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Return user input as action_ident only if global command is matched, else
    $bb8.global.nomatch.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem


BB8_GLOBAL_NOMATCH_IDENT = '$bb8.global.nomatch'


def get_module_info():
    return {
        'id': 'ai.compose.test.literal_root',
        'name': 'Literal',
        'description': 'Return user input as action_ident only if global '
                       'command is matched, else return $bb8.global.nomatch.',
        'module_name': 'test.literal_root',
        'ui_module_name': 'literal_root',
        'variables': ['location'],
    }


def run(parser_config, user_input):
    if user_input.location:
        return '$location', {'location': user_input.location}

    text = user_input.text
    if text in [x['action_ident'] for x in parser_config['links']]:
        return text, {}
    return BB8_GLOBAL_NOMATCH_IDENT, {}


def get_linkages(parser_config):
    links = []
    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))
    return links
