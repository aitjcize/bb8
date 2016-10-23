# -*- coding: utf-8 -*-
"""
    Default parser
    ~~~~~~~~~~~~~~

    A rule-based parser that accept keyword, location, etc.

    Copyright 2016 bb8 Authors
"""

import re

from bb8.backend.module_api import (SupportedPlatform, ParseResult, Render,
                                    Memory, Settings)


def get_module_info():
    return {
        'id': 'ai.compose.parser.core.default',
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
                    'required': ['rule', 'ack_message'],
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
                                    'collect_as': {
                                        '$ref': '#/definitions/collect_as'
                                    },
                                    'settings_set': {
                                        '$ref': '#/definitions/dict_set'
                                    },
                                    'memory_set': {
                                        '$ref': '#/definitions/dict_set'
                                    }
                                }
                            }, {
                                'properties': {
                                    'type': {'enum': ['location']},
                                    'params': {'type': 'null'},
                                    'collect_as': {
                                        '$ref': '#/definitions/collect_as'
                                    },
                                    'settings_set': {
                                        '$ref': '#/definitions/dict_set'
                                    },
                                    'memory_set': {
                                        '$ref': '#/definitions/dict_set'
                                    }
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
                            }]
                        },
                        'end_node_id': {'type': ['null', 'string']},
                        'ack_message': {'$ref': '#/definitions/ack_message'}
                    }
                }
            },
            'on_error': {
                'type': 'object',
                'required': ['end_node_id'],
                'additionalProperties': False,
                'properties': {
                    'end_node_id': {'type': ['null', 'string']},
                    'ack_message': {'$ref': '#/definitions/ack_message'},
                    'collect_as': {'$ref': '#/definitions/collect_as'}
                }
            }
        },
        'definitions': {
            'ack_message': {
                'oneOf': [{
                    'type': 'string'
                }, {
                    'type': 'array',
                    'items': {'type': 'string'}
                }]
            },
            'collect_as': {
                'type': 'object',
                'required': ['key'],
                'properties': {
                    'key': {'type': 'string'},
                    'value': {'type': 'string'}
                }
            },
            'dict_set': {
                'type': 'object',
                'required': ['key'],
                'properties': {
                    'key': {'type': 'string'},
                    'value': {}
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
               "collect_as": {
                 "key": "keyname",
                 "value": "{{matches#1}}  # if omit, this will be {{text}}
               },
               "memory_set": {
                 "key": "keyname",
                 "value": "{{matches#1}}  # if omit, this will be {{text}}
               },
           },
           "end_node_id": 0,
           "ack_message": "action1 activated"
       }, {
           "rule": {
               "type": "location",
               "params": null
           },
           "end_node_id": 1,
           "ack_message": "action2 activated"
       }]
    }
    """
    collect = {}

    for link in parser_config['links']:
        r_type = link['rule']['type']

        def ret(link, variables, collect):
            end_node_id = link.get('end_node_id', None)
            if end_node_id:
                end_node_id = Render(end_node_id, variables)
            ack_msg = link.get('ack_message', None)
            return ParseResult(end_node_id, ack_msg, variables, collect)

        collect_as = link['rule'].get('collect_as')
        memory_set = link['rule'].get('memory_set')
        settings_set = link['rule'].get('settings_set')

        if r_type == 'regexp' and user_input.text:
            for param in link['rule']['params']:
                m = re.search(unicode(param), user_input.text)
                if m:
                    new_vars = {
                        'text': user_input.text,
                        'matches': [user_input.text] + list(m.groups())
                    }
                    if collect_as:
                        collect[collect_as['key']] = Render(
                            collect_as.get('value', '{{text}}'), new_vars)

                    if memory_set:
                        value = memory_set.get('value', '{{text}}')
                        if (isinstance(value, unicode) or
                                isinstance(value, str)):
                            value = Render(value, new_vars)
                        Memory.Set(memory_set['key'], value)

                    if settings_set:
                        value = settings_set.get('value', '{{text}}')
                        if (isinstance(value, unicode) or
                                isinstance(value, str)):
                            value = Render(value, new_vars)
                        Settings.Set(settings_set['key'], value)

                    return ret(link, new_vars, collect)
        elif r_type == 'location' and user_input.location:
            if collect_as:
                collect[collect_as['key']] = user_input.location
            if memory_set:
                Memory.Set(memory_set['key'], user_input.location)
            if settings_set:
                Settings.Set(settings_set['key'], user_input.location)
            return ret(link, {'location': user_input.location}, collect)
        elif r_type == 'event' and user_input.event:
            for param in link['rule']['params']:
                if re.search(param, user_input.event.key):
                    return ret(link, {'event': user_input.event}, {})
        elif r_type == 'sticker' and user_input.sticker:
            for param in link['rule']['params']:
                if re.search(param, user_input.sticker):
                    return ret(link, {'sticker': user_input.sticker}, {})

    if as_root:
        return ParseResult(errored=True)

    on_error = parser_config.get('on_error')
    if on_error:
        collect_as = on_error.get('collect_as')
        if collect_as:
            value = collect_as.get('value', '{{text}}')
            collect[collect_as['key']] = Render(value,
                                                {'text': user_input.text})

        variables = {'text': user_input.text}
        return ParseResult(Render(on_error['end_node_id'], variables),
                           on_error.get('ack_message'),
                           variables, collect, errored=True)

    return ParseResult(None, 'Invalid input, please re-enter',
                       {'text': user_input.text}, collect, errored=True)


def get_linkages(parser_config):
    links = []
    for link in parser_config['links']:
        if 'end_node_id' in link:
            links.append(link['end_node_id'])
    return links
