# -*- coding: utf-8 -*-
"""
    Messaging API
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import re

import enum
import jsonschema

from bb8.backend.database import User, PlatformTypeEnum
from bb8.backend.messaging_provider import facebook, line
from bb8.backend.util import image_convert_url


variable_re = re.compile("^{{(.*?)}}$")
has_variable_re = re.compile("{{(.*?)}}")


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
        def __init__(self, b_type, title=None, url=None, payload=None,
                     variables=None):
            if b_type not in Message.ButtonType:
                raise RuntimeError('Invalid Button type')

            self.type = b_type
            self.title = Render(title, variables) if variables else title
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
        def FromDict(cls, data, variables=None):
            jsonschema.validate(data, cls.schema())
            b_type = Message.ButtonType(data['type'])

            b = cls(b_type)
            b.title = data['title']
            if variables:
                b.title = Render(b.title, variables)

            b.url = data.get('url')
            try:
                b.payload = json.loads(data.get('payload'))
                if variables:
                    b.payload = Render(b.payload, variables)
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
                     buttons=None, variables=None):
            self.title = Render(title, variables) if variables else title
            self.item_url = item_url
            self.image_url = image_url
            self.subtitle = (Render(subtitle, variables)
                             if variables else subtitle)
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
        def FromDict(cls, data, variables=None):
            jsonschema.validate(data, cls.schema())
            title = data.get('title')

            b = cls(title)
            b.item_url = data.get('item_url')
            b.image_url = data.get('image_url')
            b.subtitle = data.get('subtitle')
            b.buttons = [Message.Button.FromDict(x, variables)
                         for x in data.get('buttons', [])]
            if variables:
                b.title = Render(b.title, variables)
                b.subtitle = Render(b.subtitle, variables)
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
                 notification_type=NotificationType.REGULAR, variables=None):
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
        self.text = Render(text, variables) if variables else text
        self.image_url = image_url
        self.buttons_text = None
        self.bubbles = []
        self.buttons = []
        self.variables = variables or {}

    def __str__(self):
        return json.dumps(self.as_dict())

    def __eq__(self, other):
        return (
            self.notification_type == other.notification_type and
            self.text == other.text and
            self.image_url == other.image_url and
            self.buttons_text == other.buttons_text and
            len(self.buttons) == len(other.buttons) and
            all([a == b for a, b in zip(self.buttons, other.buttons)]) and
            len(self.bubbles) == len(other.bubbles) and
            all([a == b for a, b in zip(self.bubbles, other.bubbles)])
        )

    @classmethod
    def FromDict(cls, data, variables=None):
        jsonschema.validate(data, cls.schema())
        m = Message()
        m.text = data.get('text')

        attachment = data.get('attachment')
        if attachment:
            if attachment['type'] == 'image':
                m.image_url = attachment['payload'].get('url')
            elif attachment['type'] == 'template':
                ttype = attachment['payload']['template_type']
                if ttype == 'button':
                    m.buttons_text = attachment['payload']['text']
                    buttons = attachment['payload']['buttons']
                    m.buttons = [Message.Button.FromDict(x, variables)
                                 for x in buttons]
                    if variables:
                        m.buttons_text = Render(m.buttons_text, variables)
                elif ttype == 'generic':
                    elements = attachment['payload']['elements']
                    m.bubbles = [Message.Bubble.FromDict(x, variables)
                                 for x in elements]
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
                                'payload': {'oneOf': [{
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
                                }, {
                                    'type': 'object',
                                    'required': ['template_type', 'text',
                                                 'buttons'],
                                    'additionalProperties': False,
                                    'properties': {
                                        'template_type': {
                                            'enum': ['button']
                                        },
                                        'text': {'type': 'string'},
                                        'buttons': {
                                            'type': 'array',
                                            'items': {
                                                '$ref': '#/definitions/button'
                                            }
                                        }
                                    }
                                }]}
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
        elif self.buttons_text:
            data['attachment'] = {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': self.buttons_text,
                    'buttons': [x.as_dict() for x in self.buttons]
                }
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
        elif self.buttons:
            msg_text = self.buttons_text + '\n'
            for i, but in enumerate(self.buttons):
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
        elif self.bubbles:
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

    def set_buttons_text(self, text):
        self.buttons_text = text

    def add_button(self, bubble):
        if len(self.bubbles) == 5:
            raise RuntimeError('maxium allowed buttons reached')

        if not isinstance(bubble, Message.Button):
            raise RuntimeError('object is not a Message.Bubble object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')

        if self.bubbles:
            raise RuntimeError('can not specify bubble and button at the '
                               'same time')

        self.buttons.append(bubble)

    def add_bubble(self, bubble):
        if len(self.bubbles) == 7:
            raise RuntimeError('maxium allowed bubbles reached')

        if not isinstance(bubble, Message.Bubble):
            raise RuntimeError('object is not a Message.Bubble object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')
        if self.buttons:
            raise RuntimeError('can not specify button and bubble at the '
                               'same time')

        self.bubbles.append(bubble)


def IsVariable(text):
    """Test if given text is a variable."""
    if not isinstance(text, str) and not isinstance(text, unicode):
        return False
    return variable_re.search(text) is not None


def Render(template, variables):
    """Render template with variables."""
    def replace(m):
        try:
            keys = m.group(1).split('.')
            var = variables
            for key in keys:
                var = var[key]
        except KeyError:
            return m.group(0)
        return var
    return has_variable_re.sub(replace, template)


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


def get_user_profile(platform, user_ident):
    provider = get_messaging_provider(platform.type_enum)
    return provider.get_user_profile(platform, user_ident)


def broadcast_message(bot, messages):
    for user in User.get_by(bot_id=bot.id):
        send_message(user, messages)
