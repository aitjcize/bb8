#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API
    ~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import re

from bb8 import config

# pylint: disable=W0611
from bb8.backend.database import PlatformTypeEnum, SupportedPlatform
from bb8.backend.messaging import Message  # pylint: disable=W0611


variable_re = re.compile("^{{(.*?)}}$")
has_variable_re = re.compile("{{(.*?)}}")

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


def Render(template, variables):
    """Render template with variables."""
    def replace(m):
        return variables.get(m.group(1), m.group(0))
    return has_variable_re.sub(replace, template)


def IsVariable(text):
    """Test if given text is a variable."""
    if not isinstance(text, str) and not isinstance(text, unicode):
        return False
    return variable_re.search(text) is not None


def Resolve(obj, variables):
    """Resolve text into variable value."""
    if not IsVariable(obj) or variables is None:
        return obj

    m = variable_re.match(str(obj))
    if not m:
        return obj

    names = m.group(1)

    if ',' in names:
        options = names.split(',')
    else:
        options = [names]

    for option in options:
        if option in variables:
            return variables[option]

    return obj
