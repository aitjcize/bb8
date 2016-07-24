#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API
    ~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import importlib
from datetime import datetime, timedelta

from flask import g

from bb8 import config
# pylint: disable=W0611
from bb8.backend.database import PlatformTypeEnum, SupportedPlatform
# pylint: disable=W0611
from bb8.backend.messaging import Message, Render, Resolve, IsVariable


CONFIG = {
    'HTTP_ROOT': 'https://%s:%d/' % (config.HOSTNAME, config.PORT)
}


class LinkageItem(object):
    def __init__(self, action_ident, end_node_id, ack_message):
        """Constructor.

        If end_node_id is None, then it means we want to go back to the self
        node.
        """
        self.action_ident = action_ident
        self.end_node_id = end_node_id
        self.ack_message = ack_message


def Config(key):
    """Return a config value given."""
    return CONFIG.get(key, None)


def TextPayload(text, send_to_current_node=True):
    """Create a text payload representation given text.

    Args:
        text: text to send
        send_to_current_node: whether or not to jump to current node before
            parsing the payload.
    """
    return {
        'node_id': g.node.id if send_to_current_node else None,
        'message': {'text': text}
    }


def LocationPayload(coordinate, send_to_current_node=True):
    """Create a location payload representation given coordinate.

    Args:
        text: text to send
        send_to_current_node: whether or not to jump to current node before
            parsing the payload.
    """
    return {
        'node_id': g.node.id if send_to_current_node else None,
        'message': {
            'attachments': [{
                'type': 'location',
                'payload': {
                    'coordinates': {
                        'lat': coordinate[0],
                        'long': coordinate[1]
                    }
                }
            }]
        }
    }


def EventPayload(key, value, send_to_current_node=True):
    """Create a event payload representing module events

    Args:
        text: text to send
        send_to_current_node: whether or not to jump to current node before
            parsing the payload.
    """
    return {
        'node_id': g.node.id if send_to_current_node else None,
        'event': {
            'key': key,
            'value': value
        }
    }


def GetUserTime():
    """Get current time according to user's timezone."""
    return datetime.utcnow() + timedelta(hours=g.user.timezone)


def GetgRPCService(name):
    addr = config.APPS_ADDR_MAP.get(name, None)
    if addr is None:
        raise RuntimeError('unknown service `%s\'' % name)

    try:
        module = importlib.import_module(
            'bb8.pb_modules.%s_service_pb2' % name.lower())
    except Exception:
        raise RuntimeError('no gRPC module available for `%s\'' % name)

    return module, addr
