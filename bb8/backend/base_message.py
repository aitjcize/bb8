# -*- coding: utf-8 -*-
"""
    Base Message Definition
    ~~~~~~~~~~~~~~~~~~~~~~~

    We deliberately separte the Message defintion, so base_message.Message
    can be used in app_api without extra dependencies that we don't want.

    This module should never be used directly in bb8 main framework!

    Copyright 2016 bb8 Authors
"""

import json
import re
import sys

import enum
import jsonschema

# Use relative import here so base_message can be used in app_api
from template_filters import FILTERS


HAS_VARIABLE_RE = re.compile('{{(.*?)}}')


def parse_variable(expr, variables):
    """Parse variable expression."""
    parts = expr.split('|')
    keys_expr = parts[0]
    filters = parts[1:]

    keys_exprs = keys_expr.split(',')

    for keys_expr in keys_exprs:
        keys = keys_expr.split('.')
        var = variables
        try:
            for key in keys:
                if '#' in key:
                    parts = key.split('#')
                    var = var[parts[0]][int(parts[1])]
                else:
                    var = var[key]
        except Exception:
            # One of the keys_expr does not exist in variables, try next one.
            pass
        else:
            break
    else:
        return None

    # Parse transform filter
    result = var
    for f in filters:
        if f in FILTERS:
            result = FILTERS[f](result)

    if not isinstance(result, str) and not isinstance(result, unicode):
        result = str(result)

    return result


def to_unicode(text):
    if text is None:
        return None

    if not isinstance(text, unicode):
        return unicode(text, 'utf8')
    return text


def Render(template, variables):
    """Render template with variables."""
    if template is None:
        return None

    def replace(m):
        expr = m.group(1)
        ret = parse_variable(expr, variables)
        return ret if ret else m.group(0)
    return HAS_VARIABLE_RE.sub(replace, to_unicode(template))


def TextPayload(text):
    """Create a text payload representation given text.

    Args:
        text: text to send
    """
    return {
        'message': {'text': text}
    }


def LocationPayload(coordinate):
    """Create a location payload representation given coordinate.

    Args:
        coordinate: a coordinate representing the location
    """
    return {
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


def EventPayload(key, value):
    """Create a event payload representing module events

    Args:
        key: the event name
        value: the event value
    """
    return {
        'event': {
            'key': key,
            'value': value
        }
    }


class Message(object):
    """The Message class is a representation of messages.

    We use Facebook's message format as our internal/intermediate
    representation.
    """

    MAX_TEXT_LEN = 320

    class NotificationType(enum.Enum):
        REGULAR = 'REGULAR'
        SILENT_PUSH = 'SLIENT_PUSH'
        NO_PUSH = 'NO_PUSH'

    class ButtonType(enum.Enum):
        WEB_URL = 'web_url'
        POSTBACK = 'postback'
        ELEMENT_SHARE = 'element_share'

    class QuickReplyType(enum.Enum):
        TEXT = 'text'
        LOCATION = 'location'

    class Button(object):
        def __init__(self, b_type, title=None, url=None, payload=None,
                     acceptable_inputs=None, variables=None):
            if b_type not in Message.ButtonType:
                raise RuntimeError('Invalid Button type')

            variables = variables or {}
            self.type = b_type
            self.title = Render(title, variables)
            self.url = Render(url, variables)
            self.payload = None
            self.acceptable_inputs = acceptable_inputs or []

            if payload:
                if isinstance(payload, str) or isinstance(payload, unicode):
                    self.payload = Render(payload, variables)
                elif isinstance(payload, dict):
                    self.payload = Render(json.dumps(payload), variables)

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
            """Construct Button object given a button dictionary."""
            jsonschema.validate(data, cls.schema())

            payload = data.get('payload')
            if payload and isinstance(payload, dict):
                payload = json.dumps(payload)

            return cls(Message.ButtonType(data['type']),
                       data.get('title'), data.get('url'), payload,
                       data.get('acceptable_inputs'), variables)

        @classmethod
        def schema(cls):
            return {
                'oneOf': [{
                    'type': 'object',
                    'required': ['type', 'title', 'url'],
                    'properties': {
                        'type': {'enum': ['web_url']},
                        'title': {'type': 'string'},
                        'url': {'type': 'string'},
                        'acceptable_inputs': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                }, {
                    'type': 'object',
                    'required': ['type', 'title', 'payload'],
                    'properties': {
                        'type': {'enum': ['postback']},
                        'title': {'type': 'string'},
                        'payload': {'type': ['string', 'object']},
                        'acceptable_inputs': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        }
                    }
                }, {
                    'type': 'object',
                    'required': ['type'],
                    'properties': {
                        'type': {'enum': ['element_share']},
                    }
                }]
            }

        def as_dict(self):
            if self.type == Message.ButtonType.ELEMENT_SHARE:
                data = {
                    'type': self.type.value
                }
            else:
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
        MAX_TITLE_LEN = 80
        MAX_BUTTONS = 3

        def __init__(self, title, item_url=None, image_url=None, subtitle=None,
                     buttons=None, variables=None):
            variables = variables or {}
            self.title = Render(title, variables)
            self.item_url = Render(item_url, variables)
            self.image_url = Render(image_url, variables)
            self.subtitle = Render(subtitle, variables)
            self.buttons = buttons or []

            # Truncat to limits
            if self.title:
                self.title = self.title[:self.MAX_TITLE_LEN]
            if self.subtitle:
                self.subtitle = self.subtitle[:self.MAX_TITLE_LEN]

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
            """Construct Bubble object given a dictionary."""
            jsonschema.validate(data, cls.schema())

            buttons = [Message.Button.FromDict(x, variables)
                       for x in data.get('buttons', [])]
            return cls(data['title'], data.get('item_url'),
                       data.get('image_url'), data.get('subtitle'),
                       buttons, variables)

        @classmethod
        def schema(cls):
            return {
                'type': 'object',
                'required': ['title'],
                'additionalProperties': False,
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

            if len(self.buttons) == self.MAX_BUTTONS:
                raise RuntimeError('max number of Message.Button reached')

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

    class QuickReply(object):
        def __init__(self, content_type, title=None, payload=None,
                     acceptable_inputs=None, variables=None):
            if content_type not in Message.QuickReplyType:
                raise RuntimeError('Invalid QuickReplyType type')

            if (content_type == Message.QuickReplyType.LOCATION and
                    (title or payload)):
                raise RuntimeError('extra attribute found for LOCATION '
                                   'QuickReply')

            variables = variables or {}
            self.content_type = content_type
            self.title = Render(title, variables)
            if payload:
                if isinstance(payload, str) or isinstance(payload, unicode):
                    self.payload = str(payload)
                elif isinstance(payload, dict):
                    self.payload = json.dumps(payload)
            else:
                self.payload = self.title

            self.acceptable_inputs = acceptable_inputs or []

        def __str__(self):
            return json.dumps(self.as_dict())

        def __eq__(self, other):
            return (
                self.title == other.title and
                self.payload == other.payload
            )

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct QuickReply object given a dictionary."""
            jsonschema.validate(data, cls.schema())

            return cls(Message.QuickReplyType(data['content_type']),
                       data.get('title'), data.get('payload'),
                       data.get('acceptable_inputs'), variables)

        @classmethod
        def schema(cls):
            return {
                'type': 'object',
                'required': ['content_type'],
                'properties': {
                    'content_type': {'enum': ['text', 'location']},
                    'title': {'type': 'string'},
                    'payload': {'type': ['string', 'object']},
                    'acceptable_inputs': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }

        def as_dict(self):
            if self.content_type == Message.QuickReplyType.TEXT:
                return {
                    'content_type': self.content_type.value,
                    'title': self.title,
                    'payload': self.payload
                }
            else:
                return {
                    'content_type': self.content_type.value
                }

    def __init__(self, text=None, image_url=None, buttons_text=None,
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

        variables = variables or {}
        self.notification_type = notification_type
        self.text = Render(text, variables)
        self.image_url = Render(image_url, variables)
        self.buttons_text = Render(buttons_text, variables)
        self.bubbles = []
        self.buttons = []
        self.quick_replies = []

        # Truncat to limits
        if self.text:
            self.text = self.text[:self.MAX_TEXT_LEN]
        if self.buttons_text:
            self.buttons = self.buttons[:self.MAX_TEXT_LEN]

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
        """Construct Message object given a dictionary."""
        jsonschema.validate(data, cls.schema())

        variables = variables or {}
        m = cls(data.get('text'), variables=variables)

        attachment = data.get('attachment')
        if attachment:
            if attachment['type'] == 'image':
                m.image_url = attachment['payload'].get('url')
            elif attachment['type'] == 'template':
                ttype = attachment['payload']['template_type']
                if ttype == 'button':
                    m.buttons_text = attachment['payload']['text']
                    for x in attachment['payload']['buttons']:
                        m.add_button(cls.Button.FromDict(x, variables))
                elif ttype == 'generic':
                    for x in attachment['payload']['elements']:
                        m.add_bubble(cls.Bubble.FromDict(x, variables))

        quick_replies = data.get('quick_replies')
        if quick_replies:
            m.quick_replies = [cls.QuickReply.FromDict(x, variables)
                               for x in quick_replies]
        return m

    @classmethod
    def schema(cls):
        return {
            'oneOf': [{
                'required': ['text'],
                'additionalProperties': False,
                'type': 'object',
                'properties': {
                    'text': {'type': 'string'},
                    'quick_replies': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/quick_reply'}
                    }
                }
            }, {
                'required': ['attachment'],
                'additionalProperties': True,
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
                                    'additionalProperties': True,
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
                                    'additionalProperties': True,
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
                    },
                    'quick_replies': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/quick_reply'}
                    }
                }
            }],
            'definitions': {
                'button': Message.Button.schema(),
                'bubble': Message.Bubble.schema(),
                'quick_reply': Message.QuickReply.schema()
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

        if self.quick_replies:
            data['quick_replies'] = [x.as_dict() for x in self.quick_replies]

        return data

    def set_notification_type(self, value):
        if value not in Message.NotificationType:
            raise RuntimeError('Invalid notification type')

        self.notification_type = value

    def add_button(self, button):
        if len(self.buttons) == 3:
            raise RuntimeError('maxium allowed buttons reached')

        if not isinstance(button, Message.Button):
            raise RuntimeError('object is not a Message.Button object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')

        if self.bubbles:
            raise RuntimeError('can not specify bubble and button at the '
                               'same time')

        self.buttons.append(button)

    def add_bubble(self, bubble):
        if len(self.bubbles) == 10:
            raise RuntimeError('maximum allowed bubbles reached')

        if not isinstance(bubble, Message.Bubble):
            raise RuntimeError('object is not a Message.Bubble object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')
        if self.buttons:
            raise RuntimeError('can not specify button and bubble at the '
                               'same time')

        self.bubbles.append(bubble)

    def add_quick_reply(self, reply):
        if not isinstance(reply, Message.QuickReply):
            raise RuntimeError('object is not a Message.QuickReply object')

        self.quick_replies.append(reply)


# To allow pickling inner class, set module attribute alias
setattr(sys.modules[__name__], 'NotificationType', Message.NotificationType)
setattr(sys.modules[__name__], 'ButtonType', Message.ButtonType)
setattr(sys.modules[__name__], 'QuickReplyType', Message.QuickReplyType)
setattr(sys.modules[__name__], 'Button', Message.Button)
setattr(sys.modules[__name__], 'Bubble', Message.Bubble)
setattr(sys.modules[__name__], 'QuickReply', Message.QuickReply)
