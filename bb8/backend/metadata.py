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
    def __init__(self, message=None, postback=None):
        self.text = None
        self.attachments = None
        self.location = None
        self.jump_node_id = None

        if message:
            self.text = message.get('text')
            self.parse_attachments(message.get('attachments'))

        if postback:
            try:
                payload = json.loads(postback['payload'])
                message = payload['message']
                self.text = message.get('text')
                self.parse_attachments(message.get('attachments'))
                self.jump_node_id = int(payload['node_id'])
            except ValueError:
                pass

    @classmethod
    def Text(cls, text):
        return UserInput({'text': text})

    def parse_attachments(self, attachments):
        if not attachments:
            return

        for att in attachments:
            if att['type'] == 'location':
                self.location = att.get('payload')

    def jump(self):
        return self.jump_node_id is not None
