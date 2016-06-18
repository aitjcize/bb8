# -*- coding: utf-8 -*-
"""
    Messaging API
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json

import enum
import jsonschema

from bb8.backend.database import User, PlatformTypeEnum
from bb8.backend.messaging_provider import facebook, line


class Message(object):
    """The Message class is a representation of messages.

    We use Facebook's message format as our internal/intermediate
    representation.
    """

    class NotificationType(enum.Enum):
        REGULAR = 'REGULAR'
        SILENT_PUSH = 'SLIENT_PUSH'
        NO_PUSH = 'NO_PUSH'

    class ButtonType(enum.Enum):
        WEB_URL = 'web_url'
        POSTBACK = 'postback'

    class Button(object):
        def __init__(self, b_type, title, url=None, payload=None):
            if b_type not in Message.ButtonType:
                raise RuntimeError('Invalid Button type')

            self._type = b_type
            self._title = title
            self._url = url
            self._payload = None

            if payload:
                if isinstance(payload, str) or isinstance(payload, unicode):
                    self._payload = str(payload)
                elif isinstance(payload, dict):
                    self._payload = json.dumps(payload)

        def __str__(self):
            return json.dumps(self.as_dict())

        @classmethod
        def schema(cls):
            return {
                'oneOf': [{
                    'required': ['type', 'title', 'url'],
                    'additionalProperties': False,
                    'type': 'object',
                    'properties': {
                        'type': {'enum': ['web_url']},
                        'title': {'type': 'string'},
                        'url': {'type': 'string'}
                    }
                }, {
                    'required': ['type', 'title', 'payload'],
                    'additionalProperties': False,
                    'type': 'object',
                    'properties': {
                        'type': {'enum': ['postback']},
                        'title': {'type': 'string'},
                        'payload': {'type': 'string'}
                    }
                }]
            }

        def as_dict(self):
            data = {
                'type': self._type.value,
                'title': self._title,
            }
            if self._type == Message.ButtonType.WEB_URL:
                data['url'] = self._url
            else:
                data['payload'] = self._payload
            return data

    class Bubble(object):
        def __init__(self, title, item_url=None, image_url=None, subtitle=None,
                     buttons=None):
            self._title = title
            self._item_url = item_url
            self._image_url = image_url
            self._subtitle = subtitle
            self._buttons = buttons or []

        def __str__(self):
            return json.dumps(self.as_dict())

        @classmethod
        def schema(cls):
            return {
                'required': ['title'],
                'additionalProperties': False,
                'type': 'object',
                'properties': {
                    'buttons': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/button'}
                    },
                    'image_url': {'type': 'string'},
                    'item_url': {'type': 'string'},
                    'subtitle': {'type': 'string'},
                    'title': {'type': 'string'}
                },
                'definitions': {
                    'button': Message.Button.schema()
                }
            }

        def add_button(self, button):
            if not isinstance(button, Message.Button):
                raise RuntimeError('object is not a Message.Button object')

            self._buttons.append(button)

        def as_dict(self):
            data = {
                'title': self._title,
            }

            if self._item_url:
                data['item_url'] = self._item_url

            if self._image_url:
                data['image_url'] = self._image_url

            if self._subtitle:
                data['subtitle'] = self._subtitle

            if self._buttons:
                data['buttons'] = [x.as_dict() for x in self._buttons]

            return data

    def __init__(self, text=None, image_url=None,
                 notification_type=NotificationType.REGULAR):
        """Constructor.

        Args:
            text: text message to send
        """
        if notification_type not in self.NotificationType:
            raise RuntimeError('Invalid notification type')

        if text and image_url:
            raise RuntimeError('can not specify text and image at the same '
                               'time')

        self._constructed = False
        self._notification_type = notification_type
        self._text = text
        self._image_url = image_url
        self._bubbles = []
        self.from_dict = None

        if self._text:
            self._constructed = True

    @classmethod
    def FromDict(cls, data):
        jsonschema.validate(data, cls.schema())
        m = Message()
        m.from_dict = data
        return m

    def __str__(self):
        return json.dumps(self.as_dict())

    @classmethod
    def schema(cls):
        return {
            'oneOf': [{
                'required': ['text'],
                'additionalProperties': False,
                'type': 'object',
                'properties': {
                    'text': {'type': 'string'}
                }
            }, {
                'required': ['attachment'],
                'additionalProperties': False,
                'type': 'object',
                'properties': {
                    'attachment': {
                        'required': ['type', 'payload'],
                        'type': 'object',
                        'oneOf': [{
                            'properties': {
                                'type': {'enum': ['image']},
                                'payload': {
                                    'type': 'object',
                                    'required': ['url'],
                                    'additionalProperties': False,
                                    'properties': {
                                        'url': {'type': 'string'}
                                    }
                                }
                            }
                        }, {
                            'properties': {
                                'type': {'enum': ['template']},
                                'payload': {
                                    'type': 'object',
                                    'required': ['template_type', 'elements'],
                                    'additionalProperties': False,
                                    'properties': {
                                        'template_type': {
                                            'enum': ['generic']
                                        },
                                        'elements': {
                                            'type': 'array',
                                            'items': {
                                                '$ref': '#/definitions/bubble'
                                            }
                                        }
                                    }
                                }
                            }
                        }]
                    }
                }
            }],
            'definitions': {
                'button': Message.Button.schema(),
                'bubble': Message.Bubble.schema()
            }
        }

    def as_dict(self):
        if self.from_dict:
            return self.from_dict

        data = {}

        if self._text:
            data['text'] = self._text
        elif self._image_url:
            data['attachment'] = {
                'type': 'image',
                'payload': {'url': self._image_url}
            }
        else:
            data['attachment'] = {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': [x.as_dict() for x in self._bubbles]
                }
            }
        return data

    def as_facebook_dict(self):
        """Return message as Facebook message dictionary."""
        return self.as_dict()

    def as_line_dict(self):
        """Return message as Line message dictionary."""
        if self._text:
            return {'contentType': 1, 'toType': 1, 'text': self._text}
        return {'contentType': 1, 'toType': 1, 'text': 'stub'}

    @property
    def notification_type(self):
        return self._notification_type

    @notification_type.setter
    def notification_type(self, value):
        if value not in Message.NotificationType:
            raise RuntimeError('Invalid notification type')

        self._notification_type = value

    def add_bubble(self, bubble):
        if len(self._bubbles) == 7:
            raise RuntimeError('maxium allowed bubbles reached')

        if not isinstance(bubble, Message.Bubble):
            raise RuntimeError('object is not a Message.Bubble object')

        if self._text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')

        self._bubbles.append(bubble)


def get_messaging_provider(platform_type):
    if platform_type == PlatformTypeEnum.Facebook:
        return facebook
    elif platform_type == PlatformTypeEnum.Line:
        return line


def send_message(user, messages):
    if isinstance(messages, Message):
        messages = [messages]

    provider = get_messaging_provider(user.platform.type_enum)
    provider.send_message(user, messages)


def broadcast_message(bot, messages):
    for user in User.get_by(bot_id=bot.id):
        send_message(user, messages)
