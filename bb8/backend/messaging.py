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
from bb8.backend.util import image_convert_url


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
        def __init__(self, b_type, title=None, url=None, payload=None):
            if b_type not in Message.ButtonType:
                raise RuntimeError('Invalid Button type')

            self.type = b_type
            self.title = title
            self.url = url
            self.payload = None

            if payload:
                if isinstance(payload, str) or isinstance(payload, unicode):
                    self.payload = str(payload)
                elif isinstance(payload, dict):
                    self.payload = json.dumps(payload)

        def __str__(self):
            return json.dumps(self.as_dict())

        def __eq__(self, other):
            return (
                self.type == other.type and
                self.title == other.title and
                self.url == other.url and
                self.payload == other.payload
            )

        @classmethod
        def FromDict(cls, data):
            jsonschema.validate(data, cls.schema())
            b_type = Message.ButtonType(data['type'])

            b = cls(b_type)
            b.title = data.get('title')
            b.url = data.get('url')
            try:
                b.payload = json.loads(data.get('payload'))
            except (TypeError, ValueError):  # Not a json object
                b.payload = data.get('payload')

            return b

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
                'type': self.type.value,
                'title': self.title,
            }
            if self.type == Message.ButtonType.WEB_URL:
                data['url'] = self.url
            else:
                data['payload'] = self.payload
            return data

    class Bubble(object):
        def __init__(self, title, item_url=None, image_url=None, subtitle=None,
                     buttons=None):
            self.title = title
            self.item_url = item_url
            self.image_url = image_url
            self.subtitle = subtitle
            self.buttons = buttons or []

        def __str__(self):
            return json.dumps(self.as_dict())

        def __eq__(self, other):
            return (
                self.title == other.title and
                self.item_url == other.item_url and
                self.image_url == other.image_url and
                self.subtitle == other.subtitle and
                len(self.buttons) == len(other.buttons) and
                all([a == b for a, b in zip(self.buttons, other.buttons)])
            )

        @classmethod
        def FromDict(cls, data):
            jsonschema.validate(data, cls.schema())
            title = data.get('title')

            b = cls(title)
            b.item_url = data.get('item_url')
            b.image_url = data.get('image_url')
            b.subtitle = data.get('subtitle')
            b.buttons = [Message.Button.FromDict(x)
                         for x in data.get('buttons', [])]
            return b

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

            self.buttons.append(button)

        def as_dict(self):
            data = {'title': self.title}

            if self.item_url:
                data['item_url'] = self.item_url

            if self.image_url:
                data['image_url'] = self.image_url

            if self.subtitle:
                data['subtitle'] = self.subtitle

            if self.buttons:
                data['buttons'] = [x.as_dict() for x in self.buttons]

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

        self.notification_type = notification_type
        self.text = text
        self.image_url = image_url
        self.bubbles = []

    def __str__(self):
        return json.dumps(self.as_dict())

    def __eq__(self, other):
        return (
            self.notification_type == other.notification_type and
            self.text == other.text and
            self.image_url == other.image_url and
            len(self.bubbles) == len(other.bubbles) and
            all([a == b for a, b in zip(self.bubbles, other.bubbles)])
        )

    @classmethod
    def FromDict(cls, data):
        jsonschema.validate(data, cls.schema())
        m = Message()
        m.text = data.get('text')

        attachment = data.get('attachment')
        if attachment:
            if attachment['type'] == 'image':
                m.image_url = attachment['payload'].get('url')
            elif attachment['type'] == 'template':
                elements = attachment['payload'].get('elements', [])
                m.bubbles = [Message.Bubble.FromDict(x) for x in elements]

        return m

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
        data = {}

        if self.text:
            data['text'] = self.text
        elif self.image_url:
            data['attachment'] = {
                'type': 'image',
                'payload': {'url': self.image_url}
            }
        else:
            data['attachment'] = {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': [x.as_dict() for x in self.bubbles]
                }
            }
        return data

    def as_facebook_message(self):
        """Return message as Facebook message dictionary."""
        return self.as_dict()

    def as_line_message(self):
        """Return message as Line message dictionary."""
        msgs = []

        if self.text:
            msgs.append({'contentType': 1, 'toType': 1, 'text': self.text})
        elif self.image_url:
            msgs.append({
                'contentType': 2,
                'toType': 1,
                'originalContentUrl':
                    image_convert_url(self.image_url, (1024, 1024)),
                'previewImageUrl':
                    image_convert_url(self.image_url, (240, 240))
            })
        else:
            for bubble in self.bubbles:
                msg_text = bubble.title + '\n'
                if bubble.subtitle:
                    msg_text += bubble.subtitle + '\n'

                msg_text += '\n'

                for i, but in enumerate(bubble.buttons):
                    if but.type == Message.ButtonType.WEB_URL:
                        msg_text += '%d. %s <%s>\n' % (i + 1, but.title,
                                                       but.url)
                    else:
                        msg_text += '%d. %s\n' % (i + 1, but.title)

                msgs.append({
                    'contentType': 1,
                    'toType': 1,
                    'text': msg_text
                })

                msgs.append({
                    'contentType': 2,
                    'toType': 1,
                    'originalContentUrl':
                        image_convert_url(bubble.image_url, (1024, 1024)),
                    'previewImageUrl':
                        image_convert_url(bubble.image_url, (240, 240))
                })

        return {'messages': msgs}

    def set_notification_type(self, value):
        if value not in Message.NotificationType:
            raise RuntimeError('Invalid notification type')

        self.notification_type = value

    def add_bubble(self, bubble):
        if len(self.bubbles) == 7:
            raise RuntimeError('maxium allowed bubbles reached')

        if not isinstance(bubble, Message.Bubble):
            raise RuntimeError('object is not a Message.Bubble object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')

        self.bubbles.append(bubble)


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
