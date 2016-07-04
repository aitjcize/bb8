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

from flask import g
from sqlalchemy import desc

from bb8 import logger
from bb8.backend.query_filters import FILTERS
from bb8.backend.database import ColletedDatum, User, PlatformTypeEnum
from bb8.backend.messaging_provider import facebook, line
from bb8.backend.metadata import InputTransformation
from bb8.backend.util import image_convert_url


variable_re = re.compile("^{{(.*?)}}$")
has_variable_re = re.compile("{{(.*?)}}")


def to_unicode(text):
    if text is None:
        return None

    if not isinstance(text, unicode):
        return unicode(text, 'utf8')
    return text


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
                     acceptable_inputs=None, variables=None):
            if b_type not in Message.ButtonType:
                raise RuntimeError('Invalid Button type')

            self.type = b_type
            self.title = Render(to_unicode(title), variables or {})
            self.url = url
            self.payload = None
            self.acceptable_inputs = acceptable_inputs or []

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

        def register_mapping(self, key):
            if self.type == Message.ButtonType.POSTBACK:
                self.acceptable_inputs.extend(['^%s$' % key, self.title])
                InputTransformation.add_mapping(self.acceptable_inputs,
                                                self.payload)

        @classmethod
        def FromDict(cls, data, variables=None, set_node_id=True):
            """Construct Button object given a button dictionary."""
            variables = variables or {}
            jsonschema.validate(data, cls.schema())
            b_type = Message.ButtonType(data['type'])

            b = cls(b_type)
            b.title = Render(to_unicode(data['title']), variables)

            b.url = data.get('url')
            payload = data.get('payload')
            if payload:
                if isinstance(payload, dict):
                    payload['node_id'] = g.node.id if set_node_id else None
                    b.payload = json.dumps(payload)
                else:
                    b.payload = Render(to_unicode(payload), variables)

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
                        'payload': {'type': ['string', 'object']}
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
            variables = variables or {}
            self.title = Render(to_unicode(title), variables)
            self.item_url = item_url
            self.image_url = image_url
            self.subtitle = Render(to_unicode(subtitle), variables)
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

        def register_mapping(self, key):
            for idx, button in enumerate(self.buttons):
                button.register_mapping(key + r'-' + str(idx + 1))

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct Bubble object given a bubble dictionary."""
            variables = variables or {}
            jsonschema.validate(data, cls.schema())
            title = data.get('title')

            b = cls(Render(to_unicode(title), variables))
            b.item_url = data.get('item_url')
            b.image_url = data.get('image_url')
            b.subtitle = Render(to_unicode(data.get('subtitle')), variables)
            b.buttons = [Message.Button.FromDict(x, variables)
                         for x in data.get('buttons', [])]
            return b

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
        self.text = Render(to_unicode(text), variables or {})
        self.image_url = image_url
        self.buttons_text = None
        self.bubbles = []
        self.buttons = []

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
        """Construct Message object given a message dictionary."""
        variables = variables or {}
        jsonschema.validate(data, cls.schema())

        m = cls()
        m.text = Render(to_unicode(data.get('text')), variables)

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
                        m.buttons_text = Render(to_unicode(m.buttons_text),
                                                variables)
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
                    msg_text += u'%d. %s <%s>\n' % (i + 1, but.title,
                                                    but.url)
                else:
                    msg_text += u'%d. %s\n' % (i + 1, but.title)

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
                        msg_text += u'%d. %s <%s>\n' % (i + 1, but.title,
                                                        but.url)
                    else:
                        msg_text += u'%d. %s\n' % (i + 1, but.title)

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

    def set_buttons_text(self, text, variables=None):
        self.buttons_text = Render(to_unicode(text), variables or {})

    def add_button(self, button):
        if len(self.buttons) == 3:
            raise RuntimeError('maxium allowed buttons reached')

        if not isinstance(button, Message.Button):
            raise RuntimeError('object is not a Message.Bubble object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')

        if self.bubbles:
            raise RuntimeError('can not specify bubble and button at the '
                               'same time')

        self.buttons.append(button)
        button.register_mapping(str(len(self.buttons)))

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
        bubble.register_mapping(str(len(self.bubbles)))


def IsVariable(text):
    """Test if given text is a variable."""
    if not isinstance(text, str) and not isinstance(text, unicode):
        return False
    return variable_re.search(text) is not None


def parseQuery(expr):
    """Parse query expression."""
    parts = expr.split('|')
    query = parts[0]
    filters = parts[1:]

    m = re.match(r'^q(all)?\.([^.]*)$', query)
    if not m:
        return expr

    key = m.group(2)
    q = ColletedDatum.query()
    q = q.filter_by(key=key)

    if m.group(1) is None:  # q.
        q = q.filter_by(user_id=g.user.id)

    # Parse query filter
    result = None
    try:
        for f in filters[:]:
            filters = filters[1:]
            if f == 'one' or f == 'first':
                result = q.first()
                result = result.value if result else None
                break
            if f == 'last':
                result = q.order_by(desc('created_at')).first()
                result = result.value if result else None
                break
            elif f == 'count':
                result = q.count()
                break
            else:
                m = re.match(r'order_by\(\'(.*)\'\)', f)
                if m:
                    field = m.group(1)
                    if field.startswith('-'):
                        q = q.order_by(desc(field[1:]))
                    else:
                        q = q.order_by(field)
    except Exception as e:
        logger.exception(e)
        return expr

    if result is None:
        return expr

    # Parse transform filter
    for f in filters:
        if f in FILTERS:
            result = FILTERS[f](result)

    if not isinstance(result, str) and not isinstance(result, unicode):
        result = str(result)

    return result


def parseVariable(expr, variables):
    """Parse variable expression."""
    parts = expr.split('|')
    keys_expr = parts[0]
    filters = parts[1:]

    keys = keys_expr.split('.')
    var = variables
    try:
        for key in keys:
            if '#' in key:
                parts = key.split('#')
                var = var[parts[0]][int(parts[1])]
            else:
                var = var[key]
    except Exception as e:
        logger.exception(e)
        return expr

    # Parse transform filter
    result = var
    for f in filters:
        if f in FILTERS:
            result = FILTERS[f](result)

    if not isinstance(result, str) and not isinstance(result, unicode):
        result = str(result)

    return result


def Render(template, variables):
    """Render template with variables."""
    if template is None:
        return None

    def replace(m):
        expr = m.group(1)
        if re.match(r'^q(all)?\.', expr):  # Query expression
            return parseQuery(expr)
        return parseVariable(expr, variables)
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
