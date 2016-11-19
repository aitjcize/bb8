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

from bb8.backend.module_api import (Message, Render, SupportedPlatform,
                                    ModuleTypeEnum, PureContentModule)


_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)


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


@PureContentModule
def run(config, unused_user_input, unused_env, variables):
    msgs = []  # The output messages.

    url = Render(config['url'], variables)
    method = config.get('method', 'post')
    params = config.get('params', [])
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
