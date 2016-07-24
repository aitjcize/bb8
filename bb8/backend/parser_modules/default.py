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
        'variables': ['text', 'matches', 'location'],
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
                                    'type': {'enum': ['event']},
                                    'params': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            }, {
                                'properties': {
                                    'type': {'enum': ['sticker']},
                                    'params': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
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
                        'ack_message': {
                            'oneOf': [{
                                'type': 'string'
                            }, {
                                'type': 'array',
                                'items': {'type': 'string'}
                            }]
                        }
                    }
                }
            }
        }
    }


def run(parser_config, user_input, as_root):
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
    def parse_collect(collect_as, match):
        """Parse collect_as attribute and return the corresponding collect
        dictionary.

        The collect_as syntax is as follows:
            key(#group_index)?
        """
        collect = {}
        if '#' in collect_as:
            try:
                parts = collect_as.split('#')
                group = int(parts[1])
                collect[parts[0]] = match.group(group)
            except Exception:
                collect[collect_as] = user_input.text
        else:
            collect[collect_as] = user_input.text
        return collect

    for link in parser_config['links']:
        if 'rule' not in link:
            continue

        collect = {}
        r_type = link['rule']['type']

        if r_type == 'regexp' and user_input.text:
            for param in link['rule']['params']:
                m = re.search(unicode(param), user_input.text)
                if m:
                    if 'collect_as' in link['rule']:
                        collect = parse_collect(link['rule']['collect_as'], m)
                    return (link['action_ident'], {
                        'text': user_input.text,
                        'matches': m.groups()
                    }, collect)
        elif r_type == 'location' and user_input.location:
            if 'collect_as' in link['rule']:
                collect[link['rule']['collect_as']] = user_input.location

            return (link['action_ident'], {'location': user_input.location},
                    collect)
        elif r_type == 'event' and user_input.event:
            for param in link['rule']['params']:
                if re.search(param, user_input.event.key):
                    return (link['action_ident'],
                            {'event': user_input.event}, {})
        elif r_type == 'sticker' and user_input.sticker:
            for param in link['rule']['params']:
                if re.search(param, user_input.sticker):
                    return (link['action_ident'],
                            {'sticker': user_input.sticker}, {})

    if as_root:
        return ('$bb8.global.nomatch', {}, {})

    return ('$error', {}, {})


def get_linkages(parser_config):
    links = []

    for link in parser_config['links']:
        links.append(LinkageItem(link['action_ident'], link['end_node_id'],
                                 link['ack_message']))

    if '$error' not in [l['action_ident'] for l in parser_config['links']]:
        links.append(LinkageItem('$error', None,
                                 'Invalid response, please re-enter.'))
    return links
