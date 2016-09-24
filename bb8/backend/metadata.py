# -*- coding: utf-8 -*-
"""
    Metadata classes
    ~~~~~~~~~~~~~~~~

    Metadata classes such as class for storing session object.

    Copyright 2016 bb8 Authors
"""

import json
import re

from flask import g
from sqlalchemy.ext.mutable import Mutable


class SessionRecord(Mutable):
    def __init__(self, node_id):
        self._node_id = node_id
        self._message_sent = False
        self._input_transformation = []

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

    @property
    def input_transformation(self):
        return self._input_transformation

    @input_transformation.setter
    def input_transformation(self, value):
        self._input_transformation = value
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
        return self._node_id, self._message_sent, self._input_transformation

    def __setstate__(self, state):
        try:
            (self._node_id,
             self._message_sent,
             self._input_transformation) = state
        except ValueError:
            # Temporarily workaround: We added input_transformation on
            # 2016/07/02. Need to handle the case where the previous user
            # session does not have input_transformation
            self._node_id, self._message_sent = state
            self._input_transformation = []


class ParseResult(object):
    """A result object parser modules needs to return.
    """
    def __init__(self, action_ident=None, ack_message=None, variables=None,
                 collected_datum=None, skip_content_module=True):
        """Constructor.

        Args:
            action_ident: action identifier.
            ack_message: ack message that we want to reply immediately.
            variables: parsed action variable.
            collected_datum: data that the parser wants to collect.
            skip_content_module: skip running content module if the current
                node is executed immediately.
        """
        self.action_ident = action_ident
        self.ack_message = ack_message
        self.variables = variables or {}
        self.collected_datum = collected_datum or {}
        self.skip_content_module = skip_content_module

    def collect(self, key, value):
        self.collected_datum[key] = value

    @property
    def matched(self):
        return self.action_ident is not None or self.ack_message is not None


class PostbackEvent(object):
    """Event class representing a postback event."""
    def __init__(self, event):
        self.key = event['key']
        self.value = event['value']


class UserInput(object):
    def __init__(self):
        self.text = None
        self.sticker = None
        self.location = None
        self.jump_node_id = None
        self.event = None
        self.raw_message = None

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
    def Event(cls, key, value):
        u = UserInput()
        u.event = PostbackEvent({'key': key, 'value': value})
        return u

    @classmethod
    def FromPayload(cls, payload):
        u = UserInput()
        try:
            payload = json.loads(payload)
        except Exception:
            u.text = payload  # assume text when failed
            return u

        message = payload.get('message', None)
        if message:
            u.text = message.get('text')
            u.parse_facebook_attachments(message.get('attachments'))

        event = payload.get('event', None)
        if event:
            u.event = PostbackEvent(event)

        node_id = payload.get('node_id', None)
        if node_id:
            u.jump_node_id = int(node_id)
        return u

    @classmethod
    def FromFacebookMessage(cls, messaging):
        u = UserInput()
        message = messaging.get('message')
        if message:
            u.text = message.get('text')
            u.parse_facebook_sticker(message)
            u.parse_facebook_attachments(message.get('attachments'))
            u.parse_to_raw_message(message)
            return u

        postback = messaging.get('postback')
        if postback:
            return cls.FromPayload(postback['payload'])

        return None

    def RunInputTransformation(self):
        """Perform input transformation if there is one."""
        try:
            if self.text and g.user and g.user.session.input_transformation:
                ret = InputTransformation.transform(
                    self.text, g.user.session.input_transformation)
                return ret if ret else self
        except AttributeError:
            pass

        return self

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

    def parse_to_raw_message(self, message):
        for uneeded_key in ['mid', 'seq']:
            del message[uneeded_key]

        attachments = message.get('attachments')
        if attachments:
            message['attachment'] = attachments[0]
            del message['attachments']

        self.raw_message = message

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

    def disable_jump(self):
        """Remove the jump node ID so the input does not indicate jumping."""
        self.jump_node_id = None


class InputTransformation(object):
    @classmethod
    def get(cls):
        try:
            _ = g.input_transformation
        except AttributeError:
            g.input_transformation = []

        return g.input_transformation

    @classmethod
    def clear(cls):
        g.input_transformation = []

    @classmethod
    def add_mapping(cls, rules, payload):
        cls.get().append((rules, payload))

    @classmethod
    def transform(cls, text, transformations):
        for rules, payload in transformations:
            for rule in rules:
                if re.search(rule, text):
                    return UserInput.FromPayload(payload)

        return None
