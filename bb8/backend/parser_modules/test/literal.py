# -*- coding: utf-8 -*-
"""
    Literal test parser module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Return what user input as action_ident.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem


def run(unused_parser_config, user_input):
    return user_input.text


def get_linkages(parser_config):
    links = []
    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))
    return links
