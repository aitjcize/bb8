# -*- coding: utf-8 -*-
"""
    Commando module
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors

    This module is used to convert the JSON object returned by the remote
    server into the bot message back to user.

    An example of server's response:

    {
      "messages": [
        /*** Pure text message ***/
        {
          "text": "A regular message"
        },

        /*** Bubbles ***/
        {
          "attachment": {
            "type": "template",
            "payload": {
              "template_type": "generic",
              "elements": [
                {
                  "title": "Main Title", "subtitle": "Sub-title",
                  "image_url": "http://xxx.ooo"
                },
                {
                  "title": "Main Title", "subtitle": "Sub-title",
                  "image_url": "http://xxx.ooo"
                }
              ]
            }
          }
        },

        /*** Buttons ***/
        {
          "attachment": {
            "type": "template",
            "payload": {
              "template_type": "button",
              "text": "Main title",
              "buttons": [{
                "type": "postback",
                "title": "Shown to user",
                "payload": "Postback to bot"
              }]
            }
          }
        }
      ],
      "memory": {
        "whatever_key_0": "whatever_value_0",
        "whatever_key_1": "whatever_value_1"
      },
      "memory_copy": {
        "whatever_key_0": "local_variable_name_0",
        "whatever_key_1": "local_variable_name_1"
      },
      "settings": {
        "whatever_key_0": "whatever_value_0",
        "whatever_key_1": "whatever_value_1"
      },
      "settings_copy": {
        "whatever_key_0": "local_variable_name_0",
        "whatever_key_1": "local_variable_name_1"
      }
    }

    This module also supports JSON transform too, which converts the server's
    response to the format that that commando parses (the above format).

    If the url is not specified in the config, this means not to fetch data
    from external website. Instead, the transform must be configured. This is
    useful for the case that output the values in settings and memory.

    'memory' and 'settings' are used to set the variables in memory and
    setting. The setting value is basically a string. If you want to copy a
    dict or array use 'memory_copy' and 'settings_copy'.

    The jinja document: http://jinja.pocoo.org/docs/dev/templates/
"""

import importlib
import json
import logging

import jinja2
import requests

from bb8.backend.module_api import (Message, Render, SupportedPlatform, Memory,
                                    Settings, ModuleTypeEnum, Config,
                                    PureContentModule)


_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)

_MODULE_WHITELIST = ['re', 'urllib', 'base64']


def properties():
    return {
        'id': 'ai.compose.content.core.commando',
        'type': ModuleTypeEnum.Content,
        'name': 'Commando',
        'description': 'Generic Commando module',
        'supported_platform': SupportedPlatform.All,
        'variables': []
    }


def schema():
    return {
        'type': 'object',
        'properties': {
            'url': {'type': 'string'},
            'params': {
                'type': 'array',
                'items': {'$ref': '#/definitions/param'},
            },
            'debug': {'type': 'boolean'},
            'on_error': {'type': 'string'},
            'transform': {
                'type': 'array',
                'items': {'$ref': '#/definitions/transform_item'},
            },
        },
        'definitions': {
            'transform_item': {
                'type': 'object',
                'required': ['type', 'template'],
                'properties': {
                    'type': {'type': 'string'},
                    'template': {
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                },
            },
            'param': {
                'type': 'array',
                'items': {'type': 'string'},
                'minItems': 2,
                'maxItems': 2,
            },
        },
    }


def FetchData(url, params=[], method='post'):  # pylint: disable=W0102
    """Fetch the data from the given URL.

    Args:
        url: str.
        params: array of list. The key/value pairs.
        method: HTTP method.

    Returns:
        object: decoded JSON object from remote.
    """
    # Merge multiple values into a dict of array
    new_params = {}
    for (k, v) in params:
        value = new_params.get(k, [])
        new_params[k] = value + [v]

    headers = {
        'user-agent': 'compose.ai/0.0.1',
    }

    req = getattr(requests, method)
    resp = req(url, params=new_params, headers=headers)

    resp.raise_for_status()
    assert 'application/json' in resp.headers['Content-Type']

    return resp.json()


def Transform(transform, js, unused_debug):
    """Transform the input JSON into output JSON.

    Args:
      transform: list of dict. The dict includes:
                   'type': the transform type.
                   'template': str or list of str. The template.
                               JSON doesn't support multiple lines. The
                               workaround is list of str.
                 The JSON data is transformed in order.
      js: object from JSON.
      debug: bool. True to return debug message.

    Returns:
      An object for JSON.
      debug_msg: array. debug messages back to user.
    """
    debug_msg = []
    for trans in transform:
        if trans['type'] == 'jinja':
            template_json = '\n'.join(trans['template'])

            imports = {}

            if 'imports' in trans:
                for p in trans['imports']:
                    if p not in _MODULE_WHITELIST:
                        _LOG.warn('module `%s\' not in whitelist', p)
                        continue
                    imports[p] = importlib.import_module(p)

            env = jinja2.Environment()
            env.filters['safe_json'] = lambda x: json.dumps(unicode(x))[1:-1]

            tmpl = env.from_string(template_json)
            js_str = tmpl.render(  # pylint: disable=E1101
                transform_input=js,
                memory=Memory.All(),
                settings=Settings.All(),
                env={'HTTP_ROOT': Config('HTTP_ROOT')},
                **imports)

            # TODO: loose restriction on the tailing , in JSON
            js = json.loads(js_str)

    return js, debug_msg


def VarCopy(var_name, local_vars):
    """Resolve the variable name to copy whole dict/array.

    Args:
      var_name: str. may contain '.' and '[number]'.
      local_vars: from locals().

    Returns:
      str, dict, or array
    """
    value = local_vars
    for name in var_name.split('.'):
        value = value[name]
    return value


@PureContentModule
def run(config, unused_user_input, unused_env, variables):
    msgs = []  # The output messages.

    url = Render(config.get('url'), variables)
    method = config.get('method', 'post')
    params = config.get('params', [])
    params = [
        (Render(x[0], variables), Render(x[1], variables))
        for x in params]

    debug = config.get('debug')
    on_error = config.get(
        'on_error',
        u'Ooops! Something wrong while talking to remote server.')

    try:
        if url:
            js = FetchData(url=url, params=params, method=method)
        else:
            js = None  # Loopback. Process data in memory or settings.
        transform_input = js

        transform = config.get('transform')
        if transform:
            js, debug_msg = Transform(transform, js, debug)
            if debug_msg:
                msgs += debug_msg

        if not url and not transform:
            raise ValueError('Neither url or transform is not specified')

        messages = js.get('messages', [])
        for m in messages:
            msg = Message.FromDict(m)
            msgs.append(msg)

        quick_replies = js.get('quick_replies', [])
        for q in quick_replies:
            msgs[-1].add_quick_reply(Message.QuickReply.FromDict(q))

        memory = js.get('memory', {})
        for k, v in memory.iteritems():
            if v is None:
                v = transform_input
            Memory.Set(k, v)

        memory = js.get('memory_copy', {})
        for k, v in memory.iteritems():
            Memory.Set(k, VarCopy(v, locals()))

        settings = js.get('settings', {})
        for k, v in settings.iteritems():
            if v is None:
                v = transform_input
            Settings.Set(k, v)

        settings = js.get('settings_copy', {})
        for k, v in settings.iteritems():
            Settings.Set(k, VarCopy(v, locals()))

    except Exception as e:
        _LOG.exception(e)
        msgs.append(Message(on_error))
        if debug:
            msgs.append(Message('Got an exception in commando: %r' % e))

    return msgs
