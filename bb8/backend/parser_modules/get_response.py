# -*- coding: utf-8 -*-
"""
    Get response from user
    ~~~~~~~~~~~~~~~~~~~~~~

    Get response from user and pass it as variable to the next node.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem


def run(parser_config, user_input):
    if parser_config['type'] == 'text' and user_input.text:
        return 'next', {'response': user_input.text}
    elif parser_config['type'] == 'location':
        if user_input.location:
            return 'next', {'response': user_input.location}
        return '$wrong_location', {}
    else:
        return '$error', {}


def get_linkages(parser_config):
    links = []

    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))

    if '$error' not in parser_config['links']:
        links.append(LinkageItem('$error', None,
                                 'Invalid reponse, please re-enter.'))

    if '$wrong_location' not in parser_config['links']:
        links.append(LinkageItem('$wrong_location', None,
                                 'Invalid location, pelase re-send.'))

    return links


def get_variables():
    return ['response']
