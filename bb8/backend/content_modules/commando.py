# -*- coding: utf-8 -*-
"""
    Commando module
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors

    This module is used to convert the JSON object returned by the remote
    server into the bot message back to user.

    An example of server's response:

        [
            {
                'text': 'MSG',
            },
            {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': [
                            {'title': 'TITLE', 'subtitle': 'SUBTITLE'}
                        ]
                    }
                }
            },
        ]

    User will get a plain text message and a Bubble message with title and
    subtitle.
"""
import json
import logging

import requests

from bb8.backend.module_api import Message, Render, SupportedPlatform


_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)


def get_module_info():
    return {
        'id': 'ai.compose.content.core.commando',
        'name': 'Commando',
        'description': 'Generic Commando module',
        'supported_platform': SupportedPlatform.All,
        'module_name': 'commando',
        'ui_module_name': 'commando',
    }


def schema():
    return {
        'type': 'object',
        'properties': {
        }
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

    return json.loads(resp.text)


def run(content_config, unused_env, variables):
    msgs = []  # The output messages.

    url = Render(content_config['url'], variables)
    method = content_config.get('method', 'post')
    params = content_config.get('params', [])
    params = [
        (Render(x[0], variables), Render(x[1], variables))
        for x in params]

    try:
        js = FetchData(url=url, params=params, method=method)

        for m in js:
            msg = Message.FromDict(m)
            msgs.append(msg)

    except Exception as e:
        _LOG.exception(e)
        msgs.append(Message(u'我好像壞掉了，快通知管理員。'))

    return msgs
