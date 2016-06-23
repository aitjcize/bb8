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
    def __init__(self):
        self.text = None
        self.sticker = None
        self.location = None
        self.jump_node_id = None

    @classmethod
    def Text(cls, text):
        u = UserInput()
        u.text = text
        return u

    @classmethod
    def Location(cls, coordinates, title='location'):
        u = UserInput()
        u.location = {
            'title': title,
            'coordinates': {
                'lat': coordinates[0],
                'long': coordinates[1]
            }
        }
        return u

    @classmethod
    def FromFacebookMessage(cls, messaging):
        u = UserInput()
        message = messaging.get('message')
        if message:
            u.text = message.get('text')
            u.parse_facebook_sticker(message)
            u.parse_facebook_attachments(message.get('attachments'))
            return u

        postback = messaging.get('postback')
        if postback:
            try:
                payload = json.loads(postback['payload'])
                message = payload['message']
                u.text = message.get('text')
                u.parse_facebook_attachments(message.get('attachments'))
                u.jump_node_id = int(payload['node_id'])
            except ValueError:
                pass
            else:
                return u

        return None

    def parse_facebook_sticker(self, message):
        """Helper function for parsing facebook sticker."""
        if 'sticker_id' in message:
            self.sticker = str(message['sticker_id'])

    def parse_facebook_attachments(self, attachments):
        """Helper function for parsing facebook attachments."""
        if not attachments:
            return

        for att in attachments:
            if att['type'] == 'location':
                self.location = att.get('payload')

    @classmethod
    def FromLineMessage(cls, content):
        u = UserInput()
        if content['contentType'] == 1:  # Text Message
            u.text = content['text']
        elif content['contentType'] == 7:  # Location Message
            loc = content['location']
            u.location = {
                'title': loc['title'],
                'coordinates': {
                    'lat': loc['latitude'],
                    'long': loc['longitude']
                }
            }
        else:
            return None

        return u

    def jump(self):
        return self.jump_node_id is not None
