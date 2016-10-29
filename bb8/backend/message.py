# -*- coding: utf-8 -*-
"""
    Message Definition
    ~~~~~~~~~~~~~~~~~~

    Extend and patch base_message.Message to support extra feature such as
    InputTransformation and query rendering.

    Copyright 2016 bb8 Authors
"""

import json
import re
import sys

import jsonschema

from flask import g
from sqlalchemy import desc, func

from bb8 import logger
from bb8.backend import base_message, template
from bb8.backend.database import CollectedDatum, PlatformTypeEnum
from bb8.backend.metadata import InputTransformation
from bb8.backend.util import image_convert_url


VARIABLE_RE = re.compile('^{{(.*?)}}$')


def IsVariable(text):
    """Test if given text is a variable."""
    if not isinstance(text, str) and not isinstance(text, unicode):
        return False
    return VARIABLE_RE.search(text) is not None


def Resolve(obj, variables):
    """Resolve text into variable value."""
    if not IsVariable(obj) or variables is None:
        return obj

    m = VARIABLE_RE.match(str(obj))
    if not m:
        return obj

    names = m.group(1)

    if ',' in names:
        options = names.split(',')
    else:
        options = [names]

    for option in options:
        if '#' in option:
            try:
                parts = option.split('#')
                if parts[0] in variables:
                    return variables[parts[0]][int(parts[1])]
            except Exception as e:
                logger.exception(e)
                continue
        else:
            if option in variables:
                return variables[option]
    return obj


class DataQuery(object):
    def __init__(self, key):
        self.key = key
        self.fallback_value = ''
        self.query = CollectedDatum.query(
            CollectedDatum.value, CollectedDatum.created_at).filter_by(
                key=key, user_id=g.user.id)

    @property
    def one(self):
        result = self.query.limit(1).first()
        return result[0] if result else self.fallback_value

    @property
    def first(self):
        return self.one

    @property
    def count(self):
        return self.query.count()

    @property
    def last(self):
        result = self.query.order_by(CollectedDatum.created_at.desc()).limit(
            1).first()
        return result[0] if result else self.fallback_value

    def get(self, index):
        result = self.query.offset(index).limit(1).first()
        return result[0] if result else self.fallback_value

    def lru(self, index):
        result = CollectedDatum.query(
            CollectedDatum.value,
            func.max(CollectedDatum.created_at).label('latest')
        ).filter_by(
            key=self.key,
            user_id=g.user.id
        ).group_by(
            CollectedDatum.value
        ).order_by(
            desc('latest')
        ).offset(index).limit(1).first()
        return result[0] if result else self.fallback_value

    def fallback(self, fallback):
        self.fallback_value = fallback
        return self

    def order_by(self, field):
        if field.startswith('-'):
            self.query = self.query.order_by(desc(field[1:]))
        else:
            self.query = self.query.order_by(field)
        return self

    def uniq(self):
        self.query = self.query.distinct(CollectedDatum.value)
        return self


def Render(tmpl, variables):
    """Render template with variables."""

    # Inject user settings and memory access
    if hasattr(g, 'user'):
        variables['settings'] = g.user.settings
        variables['memory'] = g.user.memory

    # Inject data query object
    variables['data'] = DataQuery

    return template.Render(tmpl, variables)


def TextPayload(text, send_to_current_node=True):
    """Create a text payload representation given text.

    Args:
        text: text to send
        send_to_current_node: whether or not to jump to current node before
            parsing the payload.
    """
    ret = base_message.TextPayload(text)
    ret['node_id'] = g.node.stable_id if send_to_current_node else None
    return ret


def LocationPayload(coordinate, send_to_current_node=True):
    """Create a location payload representation given coordinate.

    Args:
        coordinate: the tuple containing long and lat
        send_to_current_node: whether or not to jump to current node before
            parsing the payload.
    """
    ret = base_message.LocationPayload(coordinate)
    ret['node_id'] = g.node.stable_id if send_to_current_node else None
    return ret


def EventPayload(key, value, send_to_current_node=True):
    """Create a event payload representing module events

    Args:
        key: the event name
        value: the event value
        send_to_current_node: whether or not to jump to current node before
            parsing the payload.
    """
    ret = base_message.EventPayload(key, value)
    ret['node_id'] = g.node.stable_id if send_to_current_node else None
    return ret


# Monkey Patch!
# Patch base_message's render message so it supports query expression
base_message.Render = Render


class Message(base_message.Message):
    """Wraps base_message.Message to provide extra function."""

    limits = {
        PlatformTypeEnum.Facebook: {
            'text': 320,
            'buttons_text': 320,
            'buttons': 3,
            'bubbles': 10,
            'quick_replies': 10
        },
        PlatformTypeEnum.Line: {
            'text': 160,
            'buttons_text': 160,
            'buttons': 3,
            'bubbles': 5,
            'quick_replies': 10
        }
    }

    NotificationType = base_message.Message.NotificationType
    ButtonType = base_message.Message.ButtonType

    class _Button(base_message.Message.Button):
        limits = {
            PlatformTypeEnum.Facebook: {
                'title': 20,
                'url': 500,
                'payload': 1000,
            },
            PlatformTypeEnum.Line: {
                'title': 20,
                'url': 500,
                'payload': 300,
            }
        }

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct Button object given a button dictionary."""
            jsonschema.validate(data, cls.schema())

            payload = data.get('payload')
            if payload and isinstance(payload, dict):
                payload['node_id'] = g.node.stable_id
                payload = json.dumps(payload)

            return cls(Message.ButtonType(data['type']),
                       data.get('title'), data.get('url'), payload,
                       data.get('acceptable_inputs'), variables)

        def apply_limits(self, platform_type):
            limits = self.limits[platform_type]
            if self.title:
                self.title = self.title[:limits['title']]
            if self.url:
                self.url = self.url[:limits['url']]
            if self.payload:
                self.payload = self.payload[:limits['payload']]

        def register_mapping(self, key):
            if self.type == Message.ButtonType.POSTBACK:
                acceptable_inputs = self.acceptable_inputs[:]
                acceptable_inputs.extend(['^%s$' % key, self.title])
                InputTransformation.add_mapping(acceptable_inputs,
                                                self.payload)

    # Patch Message.Button
    base_message.Message.Button = _Button

    class _Bubble(base_message.Message.Bubble):
        limits = {
            PlatformTypeEnum.Facebook: {
                'title': 80,
                'subtitle': 80,
                'buttons': 3,
            },
            PlatformTypeEnum.Line: {
                'title': 40,
                'subtitle': 60,
                'buttons': 3,
            }
        }

        def apply_limits(self, platform_type):
            limits = self.limits[platform_type]
            if self.title:
                self.title = self.title[:limits['title']]
            if self.subtitle:
                self.subtitle = self.subtitle[:limits['subtitle']]

            self.buttons = self.buttons[:limits['buttons']]

            for button in self.buttons:
                button.apply_limits(platform_type)

        def register_mapping(self, key):
            for idx, button in enumerate(self.buttons):
                button.register_mapping(key + r'-' + str(idx + 1))

    # Patch Message.Bubble
    base_message.Message.Bubble = _Bubble

    class _QuickReply(base_message.Message.QuickReply):
        limits = {
            PlatformTypeEnum.Facebook: {
                'title': 20,
                'payload': 1000
            }
        }

        def apply_limits(self, platform_type):
            limits = self.limits[platform_type]
            if self.title:
                self.title = self.title[:limits['title']]
            if self.payload:
                self.payload = self.payload[:limits['payload']]

        def register_mapping(self):
            if self.content_type == Message.QuickReplyType.TEXT:
                acceptable_inputs = self.acceptable_inputs[:]
                acceptable_inputs.append(self.title)
                InputTransformation.add_mapping(acceptable_inputs,
                                                self.payload)

    # Patch Message.QuickReply
    base_message.Message.QuickReply = _QuickReply

    def apply_limits(self, platform_type):
        limits = self.limits[platform_type]
        if self.text:
            self.text = self.text[:limits['text']]
        if self.buttons_text:
            self.buttons_text = self.buttons_text[:limits['buttons_text']]

        self.buttons = self.buttons[:limits['buttons']]
        self.bubbles = self.bubbles[:limits['bubbles']]
        self.quick_replies = self.quick_replies[:limits['quick_replies']]

        for button in self.buttons:
            button.apply_limits(platform_type)

        for bubble in self.bubbles:
            bubble.apply_limits(platform_type)

    def as_facebook_message(self):
        """Return message as Facebook message dictionary."""
        self.apply_limits(PlatformTypeEnum.Facebook)
        return self.as_dict()

    def as_line_message(self):
        """Return message as Line message dictionary."""
        self.apply_limits(PlatformTypeEnum.Line)

        if self.text:
            return {'type': 'text', 'text': self.text}
        elif self.image_url:
            return {
                'type': 'image',
                'originalContentUrl':
                    image_convert_url(self.image_url, (1024, 1024)),
                'previewImageUrl':
                    image_convert_url(self.image_url, (240, 240))
            }
        elif self.buttons:
            buttons = []
            for but in self.buttons:
                if but.type == Message.ButtonType.WEB_URL:
                    buttons.append({
                        'type': 'uri',
                        'label': but.title,
                        'uri': but.url
                    })
                elif but.type == Message.ButtonType.POSTBACK:
                    buttons.append({
                        'type': 'postback',
                        'label': but.title,
                        'data': but.payload
                    })

            return {
                'type': 'template',
                'altText': 'buttons',
                'template': {
                    'type': 'buttons',
                    'text': self.buttons_text,
                    'actions': buttons
                }
            }
        elif self.bubbles:
            columns = []
            max_buttons = max([len(b.buttons)
                               for b in self.bubbles])

            for bubble in self.bubbles:
                buttons = []
                for but in bubble.buttons:
                    if but.type == Message.ButtonType.WEB_URL:
                        buttons.append({
                            'type': 'uri',
                            'label': but.title,
                            'uri': but.url
                        })
                    elif but.type == Message.ButtonType.POSTBACK:
                        buttons.append({
                            'type': 'postback',
                            'label': but.title,
                            'data': but.payload
                        })

                for unused_i in range(max_buttons - len(buttons)):
                    buttons.append({
                        'type': 'postback',
                        'label': ' ',
                        'data': ' '
                    })

                col = {
                    'title': bubble.title,
                    'text': bubble.subtitle if bubble.subtitle else ' ',
                    'actions': buttons
                }

                if bubble.image_url:
                    col['thumbnailImageUrl'] = image_convert_url(
                        bubble.image_url, (1024, 1024))

                columns.append(col)

            return {
                'type': 'template',
                'altText': 'carousel',
                'template': {
                    'type': 'carousel',
                    'columns': columns
                }
            }

        return {}

    @classmethod
    def FromDict(cls, data, variables=None):
        """Construct Message object given a dictionary."""
        m = super(Message, cls).FromDict(data, variables)
        for reply in m.quick_replies:
            reply.register_mapping()
        return m

    def add_button(self, button):
        super(Message, self).add_button(button)
        button.register_mapping(str(len(self.buttons)))

    def add_bubble(self, bubble):
        super(Message, self).add_bubble(bubble)
        bubble.register_mapping(str(len(self.bubbles)))

    def add_quick_reply(self, reply):
        super(Message, self).add_quick_reply(reply)
        reply.register_mapping()


# To allow pickling inner class, set module attribute alias
# pylint: disable=W0212
setattr(sys.modules[__name__], '_Button', Message._Button)
setattr(sys.modules[__name__], '_Bubble', Message._Bubble)
setattr(sys.modules[__name__], '_QuickReply', Message._QuickReply)
