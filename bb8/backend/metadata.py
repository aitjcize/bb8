# -*- coding: utf-8 -*-
"""
    Metadata classes
    ~~~~~~~~~~~~~~~~

    Metadata classes such as class for storing session object.

    Copyright 2016 bb8 Authors
"""

import json

from sqlalchemy.ext.mutable import Mutable


class SessionRecord(Mutable):
    def __init__(self, node_id):
        self._node_id = node_id
        self._message_sent = False

    def __repr__(self):
        return '<SessionRecord(%d, %s)>' % (self._node_id, self._message_sent)

    @property
    def node_id(self):
        return self._node_id

    @property
    def message_sent(self):
        return self._message_sent

    @message_sent.setter
    def message_sent(self, value):
        self._message_sent = value
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, cls):
            if isinstance(value, int):
                return SessionRecord(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __getstate__(self):
        return self._node_id, self._message_sent

    def __setstate__(self, state):
        self._node_id, self._message_sent = state


class UserInput(object):
    def __init__(self, data):
        self.jump_node_id = None
        self.text = data
        try:
            obj = json.loads(data)
            self.jump_node_id = obj['node_id']
            self.text = obj['payload']
        except Exception:
            self.is_text = False

    def jump(self):
        return self.jump_node_id is not None
