# -*- coding: utf-8 -*-
"""
    Literal test parser module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Return what user input as action_ident.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem


def run(parser_config, user_input):
    action_idents = [x['action_ident'] for x in parser_config['links']]

    if user_input.text in action_idents:
        return user_input.text
    return '$error'


def get_linkages(parser_config):
    links = []
    links.append(LinkageItem('$error', None,
                             'Invalid command, please re-enter'))
    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))
    return links
