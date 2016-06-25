# -*- coding: utf-8 -*-
"""
    Default parser
    ~~~~~~~~~~~~~~

    A rule-based parser that accept keyword, location, etc.

    Copyright 2016 bb8 Authors
"""

import re

from bb8.backend.module_api import LinkageItem, SupportedPlatform


def get_module_info():
    return {
        'id': 'ai.compose.core.default',
        'name': 'Default',
        'description': 'A rule-based parser that accepts keyword, '
                       'location, sticker, etc',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'default',
        'ui_module_name': 'default',
        'variables': ['matches'],
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
                        'rule': {
                            'type': 'object',
                            'required': ['type'],
                            'oneOf': [{
                                'properties': {
                                    'type': {'enum': ['regexp']},
                                    'params': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    },
                                    'collect_as': {'type': 'string'}
                                }
                            }, {
                                'properties': {
                                    'type': {'enum': ['location']},
                                    'params': {'type': 'null'},
                                    'collect_as': {'type': 'string'}
                                },
                            }, {
                                'properties': {
                                    'type': {'enum': ['sticker']},
                                    'params': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    },
                                    'collect_as': {'type': 'string'}
                                }
                            }, {
                                'properties': {
                                    'type': {'enum': ['force']},
                                    'params': {'type': 'null'}
                                },
                            }]
                        },
                        'action_ident': {'type': 'string'},
                        'end_node_id': {'type': ['null', 'integer']},
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
       "links": [{
           "rule": {
               "type": "regexp",
               "params": ["^action1-[0-9]$", "action[23]-1"],
           },
           "action_ident": "action1",
           "end_node_id": 0,
           "ack_message": "action1 activated"
       }, {
           "rule": {
               "type": "location",
               "params": null
           },
           "action_ident": "action2",
           "end_node_id": 1,
           "ack_message": "action2 activated"
       }]
    }
    """
    for link in parser_config['links']:
        if 'rule' not in link:
            continue

        r_type = link['rule']['type']

        if r_type == 'regexp' and user_input.text:
            for param in link['rule']['params']:
                m = re.search(unicode(param), user_input.text)
                if m:
                    collect = {}
                    if 'collect_as' in link['rule']:
                        collect[link['rule']['collect_as']] = user_input.text

                    return (link['action_ident'], {
                        'text': user_input.text,
                        'matches': m.groups()
                    }, collect)
        elif r_type == 'location' and user_input.location:
            collect = {}
            if 'collect_as' in link['rule']:
                collect[link['rule']['collect_as']] = user_input.location

            return (link['action_ident'], {'location': user_input.location},
                    collect)
        elif r_type == 'sticker' and user_input.sticker:
            for param in link['rule']['params']:
                if re.search(param, user_input.sticker):
                    return (link['action_ident'],
                            {'sticker': user_input.sticker}, {})
        elif r_type == 'force':
            return (link['action_ident'], {}, {})

    return ('$error', {}, {})


def get_linkages(parser_config):
    links = []

    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))

    if '$error' not in parser_config['links']:
        links.append(LinkageItem('$error', None,
                                 'Invalid response, please re-enter.'))
    return links
