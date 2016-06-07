#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module API
    ~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import re

from messaging import Message  # pylint: disable=W0611


variables_extract = re.compile("{{(.*?)}}")


class LinkageItem(object):
    def __init__(self, action_ident, end_node_id, ack_message):
        """Constructor.

        If end_node_id is None, then it means we want to go back to the self
        node.
        """
        self.action_ident = action_ident
        self.end_node_id = end_node_id
        self.ack_message = ack_message


def Payload(payload, env):
    return {'node_id': env['node_id'], 'payload': payload}


def Resolve(text, variables):
    def replace(m):
        return variables.get(m.group(1), m.group(0))
    return variables_extract.sub(replace, text)
