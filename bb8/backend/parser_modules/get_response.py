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
        return 'next', {'response': user_input.location}
    else:
        return '$error', {}


def get_linkages(parser_config):
    links = []
    links.append(LinkageItem('$error', None,
                             'Invalid reponse, please re-enter'))
    links.append(LinkageItem('next', parser_config['end_node_id'],
                             parser_config['ack_message']))
    return links


def get_variables():
    return ['response']
