# -*- coding: utf-8 -*-
"""
    Passthrough module
    ~~~~~~~~~~~~~~~~~~

    Pass through next node without any action.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem


def run(unused_parser_config, unused_user_input):
    return 'next', {}


def get_linkages(parser_config):
    links = []
    links.append(LinkageItem('next', parser_config['end_node_id'],
                             parser_config['ack_message']))
    return links


def get_variables():
    return []
