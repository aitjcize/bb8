#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API
    ~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

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
        self.ack_message = unicode(ack_message)


def Config(key):
    """Return a config value given."""
    return CONFIG.get(key, None)


def TextPayload(text, env):
    """Create a text payload representation given text."""
    return {'node_id': env['node_id'], 'message': {'text': text}}


def LocationPayload(coordinate, env):
    """Create a location payload representation given coordinate."""
    return {
        'node_id': env['node_id'],
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
