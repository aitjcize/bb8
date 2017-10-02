# -*- coding: utf-8 -*-
"""
    Message Definition
    ~~~~~~~~~~~~~~~~~~

    Extend and patch base_message.Message to support extra feature such as
    InputTransformation and query rendering.

    Copyright 2016 bb8 Authors
"""

import json
import random
import re
import sys

from datetime import datetime

import jsonschema

from flask import g
from sqlalchemy import desc, func

from bb8 import config, logger
from bb8.backend import base_message, template, messaging
from bb8.backend.speech import speech_to_text
from bb8.backend.database import CollectedDatum, PlatformTypeEnum
from bb8.backend.util import image_convert_url


VARIABLE_RE = re.compile('^{{(.*?)}}$')


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
        self.image = None
        self.event = None
        self.audio = None
        self.jump_node_id = None
        self.raw_message = None
        self.ref = None

    def valid(self):
        return (self.text or
                self.sticker or
                self.location or
                self.image or
                self.event or
                self.audio)

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

        u.jump_node_id = payload.get('node_id', 'RootRouter')
        return u

    @classmethod
    def FromFacebookMessage(cls, data):
        u = UserInput()
        message = data.get('message')
        if message:
            quick_reply = message.get('quick_reply')
            if quick_reply:
                return cls.FromPayload(quick_reply['payload'])

            u.text = message.get('text')
            u.parse_facebook_sticker(message)
            u.parse_facebook_attachments(message.get('attachments'))
            u.parse_to_raw_message(message)
            return u

        postback = data.get('postback')
        if postback:
            u = cls.FromPayload(postback['payload'])
            referral = postback.get('referral')
            if referral:
                u.parse_m_me_referral(referral)
            return u

        referral = data.get('referral')
        if referral:
            u.parse_m_me_referral(referral)

        return u

    def RunInputTransformation(self):
        """Perform input transformation if there is one."""
        try:
            if (self.text and g.user and g.user.session and
                    g.user.session.input_transformation):
                ret = InputTransformation.transform(
                    self.text, g.user.session.input_transformation)
                return ret if ret else self
        except Exception as e:
            # We shouldn't block user if input transformation fail (possibly
            # due to invalid regular expression). Log the failure for
            # analysis.
            logger.exception(e)

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
                self.location = att['payload']
            elif att['type'] == 'image':
                self.image = att['payload']
            elif att['type'] == 'audio':
                self.audio = att['payload']

    def parse_to_raw_message(self, message):
        for uneeded_key in ['mid', 'seq']:
            del message[uneeded_key]

        attachments = message.get('attachments')
        if attachments:
            message['attachment'] = attachments[0]
            del message['attachments']

        self.raw_message = message

    def parse_m_me_referral(self, referral):
        self.ref = 'http://m.me/%s' % referral['ref']

    def ParseAudioAsText(self, user):
        if self.audio and self.text is None:
            data = messaging.download_audio_as_data(user, self.audio)
            self.text = speech_to_text(data, user.locale or 'zh_TW') or ''

    @classmethod
    def FromLineMessage(cls, entry):
        u = UserInput()
        if entry.get('type') == 'follow':
            u.text = 'hi'
            return u

        message = entry.get('message')
        if message:
            if message['type'] == 'text':
                u.text = message['text']
            elif message['type'] == 'location':
                u.location = {
                    'title': message['title'],
                    'coordinates': {
                        'lat': message['latitude'],
                        'long': message['longitude']
                    }
                }
            elif message['type'] == 'sticker':
                u.sticker = '%s.%s' % (message['packageId'],
                                       message['stickerId'])
            elif message['type'] == 'audio':
                u.audio = message['id']
            return u

        postback = entry.get('postback')
        if postback:
            return cls.FromPayload(postback['data'])

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

    if ';' in names:
        options = names.split(';')
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
        self.fallback_value = None
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

    # Inject some environment specific variables
    variables['env'] = {
        'host': config.HOSTNAME,
        'port': config.HTTP_PORT,
        'http_root': 'https://%s:%d' % (config.HOSTNAME, config.HTTP_PORT)
    }

    # Inject some useful modules
    variables['randint'] = random.randint
    variables['now'] = datetime.today()

    # Inject data query object
    variables['data'] = DataQuery

    return template.Render(tmpl, variables)


def TextPayload(text, send_to_next_node=True):
    """Create a text payload representation given text.

    Args:
        text: text to send
        send_to_next_node: whether or not to jump to next node of current node
            before parsing the payload.
    """
    ret = base_message.TextPayload(text)
    ret['node_id'] = g.node.next_node_id if send_to_next_node else None
    return ret


def LocationPayload(coordinate, send_to_next_node=True):
    """Create a location payload representation given coordinate.

    Args:
        coordinate: the tuple containing long and lat
        send_to_next_node: whether or not to jump to next node of current node
            before parsing the payload.
    """
    ret = base_message.LocationPayload(coordinate)
    ret['node_id'] = g.node.next_node_id if send_to_next_node else None
    return ret


def EventPayload(key, value, send_to_next_node=True):
    """Create a event payload representing module events

    Args:
        key: the event name
        value: the event value
        send_to_next_node: whether or not to jump to next node of current node
            before parsing the payload.
    """
    ret = base_message.EventPayload(key, value)
    ret['node_id'] = g.node.next_node_id if send_to_next_node else None
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
                payload['node_id'] = g.node.next_node_id
                payload = json.dumps(payload)

            webview_height_ratio = data.get('webview_height_ratio')
            if webview_height_ratio:
                webview_height_ratio = (
                    Message.WebviewHeightRatioEnum(webview_height_ratio))

            return cls(Message.ButtonType(data['type']),
                       data.get('title'), data.get('url'), payload,
                       webview_height_ratio,
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
                acceptable_inputs.extend(['^%s$' % key, '^%s$' % self.title])
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

    class _DefaultAction(base_message.Message.DefaultAction):
        limits = {
            PlatformTypeEnum.Facebook: {
                'url': 500,
            },
            PlatformTypeEnum.Line: {
                'url': 500,
            }
        }

        def apply_limits(self, platform_type):
            limits = self.limits[platform_type]
            if self.url:
                self.url = self.url[:limits['url']]

    # Patch Message.DefaultAction
    base_message.Message.DefaultAction = _DefaultAction

    class _ListItem(base_message.Message.ListItem):
        limits = {
            PlatformTypeEnum.Facebook: {
                'title': 80,
                'subtitle': 80,
                'image_url': 500,
            },
            PlatformTypeEnum.Line: {
                'title': 40,
                'subtitle': 60,
                'image_url': 500,
            }
        }

        def apply_limits(self, platform_type):
            limits = self.limits[platform_type]
            if self.title:
                self.title = self.title[:limits['title']]
            if self.subtitle:
                self.subtitle = self.subtitle[:limits['subtitle']]
            if self.image_url:
                self.image_url = self.image_url[:limits['image_url']]

            self.default_action.apply_limits(platform_type)

            for button in self.buttons:
                button.apply_limits(platform_type)

    # Patch Message.ListItem
    base_message.Message.ListItem = _ListItem

    class _QuickReply(base_message.Message.QuickReply):
        limits = {
            PlatformTypeEnum.Facebook: {
                'title': 20,
                'payload': 1000
            }
        }

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct QuickReply object given a quick reply dictionary."""
            jsonschema.validate(data, cls.schema())

            payload = data.get('payload')
            if payload and isinstance(payload, dict):
                payload['node_id'] = g.node.next_node_id
                payload = json.dumps(payload)

            return cls(Message.QuickReplyType(data['content_type']),
                       data.get('title'), payload,
                       data.get('acceptable_inputs'), variables)

        def apply_limits(self, platform_type):
            limits = self.limits[platform_type]
            if self.title:
                self.title = self.title[:limits['title']]
            if self.payload:
                self.payload = self.payload[:limits['payload']]

        def register_mapping(self):
            if self.content_type == Message.QuickReplyType.TEXT:
                acceptable_inputs = self.acceptable_inputs[:]
                acceptable_inputs.append('^%s$' % self.title)
                InputTransformation.add_mapping(acceptable_inputs,
                                                self.payload)

    # Patch Message.QuickReply
    base_message.Message.QuickReply = _QuickReply

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.register_mapping = True

    def apply_limits(self, platform_type):
        limits = self.limits[platform_type]
        if self.text is not None:
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
        """Return message as a list of Line message dictionary."""
        self.apply_limits(PlatformTypeEnum.Line)

        if self.text is not None:
            return [{'type': 'text', 'text': self.text}]
        elif self.image_url:
            return [{
                'type': 'image',
                'originalContentUrl':
                    image_convert_url(self.image_url, (1024, 1024)),
                'previewImageUrl':
                    image_convert_url(self.image_url, (240, 240))
            }]
        elif self.buttons_text is not None:
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

            return [{
                'type': 'template',
                'altText': self.buttons_text,
                'template': {
                    'type': 'buttons',
                    'text': self.buttons_text,
                    'actions': buttons
                }
            }]
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

                if not buttons:
                    buttons.append({
                        'type': 'postback',
                        'label': ' ',
                        'data': ' '
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

            return [{
                'type': 'template',
                'altText': self.bubbles[0].title,
                'template': {
                    'type': 'carousel',
                    'columns': columns
                }
            }]
        elif self.list_items:
            msgs = []
            for list_item in self.list_items:
                buttons = []
                but = list_item.button
                if but:
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

                col = {
                    'title': list_item.title,
                    'text': list_item.subtitle if list_item.subtitle else ' ',
                    'actions': buttons
                }

                if list_item.image_url:
                    col['thumbnailImageUrl'] = image_convert_url(
                        list_item.image_url, (1024, 1024))

                msgs.append({
                    'type': 'template',
                    'altText': self.list_items[0].title,
                    'template': {
                        'type': 'carousel',
                        'columns': [col]
                    }
                })
            return msgs
        else:
            raise RuntimeError('Invalid message type %r' % self)

        return []

    @classmethod
    def FromDict(cls, data, variables=None, register_mapping=True):
        """Construct Message object given a dictionary."""
        m = super(Message, cls).FromDict(data, variables, register_mapping)
        return m

    def add_button(self, button):
        super(Message, self).add_button(button)
        if self.register_mapping:
            button.register_mapping(str(len(self.buttons)))

    def add_bubble(self, bubble):
        super(Message, self).add_bubble(bubble)
        if self.register_mapping:
            bubble.register_mapping(str(len(self.bubbles)))

    def add_quick_reply(self, reply):
        super(Message, self).add_quick_reply(reply)
        if self.register_mapping:
            reply.register_mapping()


# To allow pickling inner class, set module attribute alias
# pylint: disable=W0212
setattr(sys.modules[__name__], '_Button', Message._Button)
setattr(sys.modules[__name__], '_Bubble', Message._Bubble)
setattr(sys.modules[__name__], '_DefaultAction', Message._DefaultAction)
setattr(sys.modules[__name__], '_ListItem', Message._ListItem)
setattr(sys.modules[__name__], '_QuickReply', Message._QuickReply)
