# -*- coding: utf-8 -*-
"""
    Default parser
    ~~~~~~~~~~~~~~

    A rule-based parser that accept keyword, location, etc.

    Copyright 2016 bb8 Authors
"""

import re

from bb8.backend.module_api import (CollectedData, SupportedPlatform,
                                    RouteResult, Render, ModuleTypeEnum,
                                    Memory, Settings)


def properties():
    return {
        'id': 'ai.compose.router.core.default',
        'type': ModuleTypeEnum.Router,
        'name': 'Default',
        'description': 'A rule-based parser that accepts keyword, '
                       'location, sticker, etc',
        'supported_platform': SupportedPlatform.All,
        'variables': ['text', 'matches', 'location'],
    }


def schema():
    return {
        'type': 'object',
        'required': ['links', 'on_error'],
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
                                'additionalProperties': False,
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
                                        '$ref': '#/definitions/set'
                                    },
                                    'memory_set': {
                                        '$ref': '#/definitions/set'
                                    }
                                }
                            }, {
                                'additionalProperties': False,
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
                                'additionalProperties': False,
                                'properties': {
                                    'type': {'enum': ['event']},
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
                                'additionalProperties': False,
                                'properties': {
                                    'type': {'enum': ['sticker']},
                                    'params': {
                                        'type': 'array',
                                        'items': {'type': 'string'}
                                    }
                                }
                            }]
                        },
                        'end_node_id': {'type': 'string'},
                        'ack_message': {'$ref': '#/definitions/ack_message'}
                    }
                }
            },
            'on_error': {
                'type': 'object',
                'required': ['end_node_id'],
                'additionalProperties': False,
                'properties': {
                    'end_node_id': {'type': 'string'},
                    'ack_message': {'$ref': '#/definitions/ack_message'},
                    'collect_as': {'$ref': '#/definitions/collect_as'},
                    'settings_set': {'$ref': '#/definitions/set'},
                    'memory_set': {'$ref': '#/definitions/set'}
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
            'set': {
                'oneOf': [
                    {'$ref': '#/definitions/dict_set'},
                    {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/dict_set'}
                    }
                ]
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


def process_actions(rule, variables):
    collect_as = rule.get('collect_as')
    memory_set = rule.get('memory_set')
    settings_set = rule.get('settings_set')

    if collect_as:
        if not isinstance(collect_as, list):
            collect_as = [collect_as]

        for item in collect_as:
            CollectedData.Add(
                item['key'],
                Render(item.get('value', '{{text}}'), variables))

    if memory_set:
        if not isinstance(memory_set, list):
            memory_set = [memory_set]

        for item in memory_set:
            value = item.get('value', '{{text}}')
            if isinstance(value, unicode) or isinstance(value, str):
                value = Render(value, variables)
            Memory.Set(item['key'], value)

    if settings_set:
        if not isinstance(settings_set, list):
            settings_set = [settings_set]

        for item in settings_set:
            value = item.get('value', '{{text}}')
            if isinstance(value, unicode) or isinstance(value, str):
                value = Render(value, variables)
            Settings.Set(item['key'], value)


def run(config, user_input, as_root):
    """Run module."""

    for link in config['links']:
        r_type = link['rule']['type']

        def ret(link, variables):
            end_node_id = link.get('end_node_id', None)
            if end_node_id:
                end_node_id = Render(end_node_id, variables)
            ack_msg = link.get('ack_message', None)
            return RouteResult(end_node_id, ack_msg, variables)

        if r_type == 'regexp' and user_input.text:
            for param in link['rule']['params']:
                m = re.search(unicode(param), user_input.text)
                if m:
                    new_vars = {
                        'text': user_input.text,
                        'matches': [user_input.text] + list(m.groups())
                    }
                    process_actions(link['rule'], new_vars)
                    return ret(link, new_vars)
        elif r_type == 'location' and user_input.location:
            collect_as = link['rule'].get('collect_as')
            memory_set = link['rule'].get('memory_set')
            settings_set = link['rule'].get('settings_set')
            if collect_as:
                CollectedData.Add(collect_as['key'], user_input.location)
            if memory_set:
                Memory.Set(memory_set['key'], user_input.location)
            if settings_set:
                Settings.Set(settings_set['key'], user_input.location)
            return ret(link, {'location': user_input.location})
        elif r_type == 'event' and user_input.event:
            for param in link['rule']['params']:
                if re.search(param, user_input.event.key):
                    process_actions(link['rule'], user_input.event)
                    return ret(link, {'event': user_input.event})
        elif r_type == 'sticker' and user_input.sticker:
            for param in link['rule']['params']:
                if re.search(param, user_input.sticker):
                    return ret(link, {'sticker': user_input.sticker})

    if as_root:
        return RouteResult(errored=True)

    on_error = config['on_error']
    variables = {'text': user_input.text}
    process_actions(on_error, variables)

    return RouteResult(Render(on_error['end_node_id'], variables),
                       on_error.get('ack_message'),
                       variables, errored=True)


def get_linkages(config):
    links = []
    for link in config['links']:
        if 'end_node_id' in link:
            links.append(link['end_node_id'])
    return links
