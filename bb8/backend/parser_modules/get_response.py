# -*- coding: utf-8 -*-
"""
    Get response from user
    ~~~~~~~~~~~~~~~~~~~~~~

    Get response from user and pass it as variable to the next node.

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import LinkageItem, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.core.get_response',
        'name': 'User Response',
        'description': 'Get reponse from user.',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'get_response',
        'ui_module_name': 'get_response',
        'variables': ['response'],
    }


def schema():
    return {
        'type': 'object',
        'required': ['type', 'links'],
        'additionalProperties': False,
        'properties': {
            'type': {'enum': ['text', 'location', 'all']},
            'links': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'required': ['action_ident', 'end_node_id', 'ack_message'],
                    'additionalProperties': False,
                    'properties': {
                        'action_ident': {'type': 'string'},
                        'end_node_id': {'type': 'integer'},
                        'ack_message': {'type': 'string'}
                    }
                }
            }
        }
    }


def run(parser_config, user_input):
    """
    parser_config schema:
    {
       "type": "text, location or all",
    }

    action_ident:
    - got_text
    - got_location
    - no_text
    - no_location
    - $error
    """
    r_type = parser_config['type']

    if r_type == 'text' or r_type == 'all':
        if user_input.text:
            return 'got_text', {'response': user_input.text}
        elif r_type == 'text':
            return 'no_text', {}

    if r_type == 'location' or r_type == 'all':
        if user_input.location:
            return 'got_location', {'response': user_input.location}
        elif r_type == 'location':
            return 'no_location', {}

    return '$error', {}


def get_linkages(parser_config):
    links = []

    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))

    if '$error' not in parser_config['links']:
        links.append(LinkageItem('$error', None,
                                 'Invalid response, please re-enter.'))
    return links
