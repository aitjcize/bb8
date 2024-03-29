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
import sys

import enum
import jsonschema

# Use relative import here so base_message can be used in app_api
from template import Render


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

    # These are the union of upper limits of all platforms. Individual platform
    # limits are defined in __limits__ attribute in each class of message.py
    MAX_BUTTONS = 3  # Facebook limit
    MAX_BUBBLES = 10  # Facebook limit
    MAX_LIST_ITEMS = 4  # Facebook limit

    class NotificationType(enum.Enum):
        REGULAR = 'REGULAR'
        SILENT_PUSH = 'SLIENT_PUSH'
        NO_PUSH = 'NO_PUSH'

    class ButtonType(enum.Enum):
        WEB_URL = 'web_url'
        POSTBACK = 'postback'
        ELEMENT_SHARE = 'element_share'

    class WebviewHeightRatioEnum(enum.Enum):
        COMPACT = 'compact'
        TALL = 'tall'
        FULL = 'full'

    class ListTopElementStyle(enum.Enum):
        LARGE = 'large'
        COMPACT = 'compact'

    class QuickReplyType(enum.Enum):
        TEXT = 'text'
        LOCATION = 'location'

    class Button(object):
        def __init__(self, b_type, title=None, url=None, payload=None,
                     webview_height_ratio=None, acceptable_inputs=None,
                     variables=None):
            if b_type not in Message.ButtonType:
                raise RuntimeError('Invalid Button type')

            if (webview_height_ratio and
                    webview_height_ratio not in
                    Message.WebviewHeightRatioEnum):
                raise RuntimeError('Invalid Webview height ratio')

            variables = variables or {}
            self.type = b_type
            self.title = Render(title, variables)
            self.url = Render(url, variables)
            self.payload = None
            self.webview_height_ratio = webview_height_ratio
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

        def action_equals(self, other):
            """Used for comparing 'actions' (button without a title)."""
            return (
                self.type == other.type and
                self.url == other.url
            )

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct Button object given a button dictionary."""
            jsonschema.validate(data, cls.schema())

            payload = data.get('payload')
            if payload and isinstance(payload, dict):
                payload = json.dumps(payload)

            webview_height_ratio = data.get('webview_height_ratio')
            if webview_height_ratio:
                webview_height_ratio = (
                    Message.WebviewHeightRatioEnum(webview_height_ratio))

            return cls(Message.ButtonType(data['type']),
                       data.get('title'), data.get('url'), payload,
                       webview_height_ratio,
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
                        },
                        'webview_height_ratio': {
                            'enum': ['compact', 'tall', 'full']
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
                    if self.webview_height_ratio:
                        data['webview_height_ratio'] = (
                            self.webview_height_ratio.value)
                else:
                    data['payload'] = self.payload
            return data

    class Bubble(object):
        MAX_BUTTONS = 3

        def __init__(self, title, item_url=None, image_url=None, subtitle=None,
                     buttons=None, variables=None):
            variables = variables or {}
            self.title = Render(title, variables)
            self.item_url = Render(item_url, variables)
            self.image_url = Render(image_url, variables)
            self.subtitle = Render(subtitle, variables)
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

    class DefaultAction(object):
        def __init__(self, url, variables=None):
            variables = variables or {}
            self.url = Render(url, variables)

        def __str__(self):
            return json.dumps(self.as_dict())

        def __eq__(self, other):
            return (
                self.url == other.url
            )

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct DefaultAction object given a dictionary."""
            jsonschema.validate(data, cls.schema())
            return cls(data['url'], variables)

        @classmethod
        def schema(cls):
            return {
                'type': 'object',
                'required': ['type', 'url'],
                'properties': {
                    'type': {'enum': ['web_url']},
                    'url': {'type': 'string'},
                }
            }

        def as_dict(self):
            return {
                'type': 'web_url',
                'url': self.url
            }

    class ListItem(object):
        def __init__(self, title, subtitle=None, image_url=None,
                     default_action=None, button=None, variables=None):
            variables = variables or {}
            self.title = Render(title, variables)
            self.subtitle = Render(subtitle, variables)
            self.image_url = Render(image_url, variables)
            self.default_action = default_action
            self.button = button

        def __str__(self):
            return json.dumps(self.as_dict())

        def __eq__(self, other):
            return (
                self.title == other.title and
                self.subtitle == other.subtitle and
                self.image_url == other.image_url and
                self.default_action == other.default_action and
                self.button == other.button
            )

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct ListItem object given a dictionary."""
            jsonschema.validate(data, cls.schema())

            default_action = None
            default_action_dict = data.get('default_action')
            if default_action_dict:
                default_action = Message.DefaultAction.FromDict(
                    default_action_dict, variables)

            button = None
            buttons_dict = data.get('buttons')
            if buttons_dict:
                button = Message.Button.FromDict(buttons_dict[0], variables)

            return cls(data['title'], data.get('subtitle'),
                       data.get('image_url'), default_action, button,
                       variables)

        @classmethod
        def schema(cls):
            return {
                'type': 'object',
                'required': ['title'],
                'additionalProperties': False,
                'properties': {
                    'title': {'type': 'string'},
                    'subtitle': {'type': 'string'},
                    'image_url': {'type': 'string'},
                    'default_action': {'$ref': '#/definitions/default_action'},
                    'buttons': {
                        'type': 'array',
                        'items': {'$ref': '#/definitions/button'},
                        'maxItems': 1
                    },
                },
                'definitions': {
                    'button': Message.Button.schema(),
                    'default_action': Message.DefaultAction.schema()
                }
            }

        def as_dict(self):
            data = {'title': self.title}

            if self.subtitle:
                data['subtitle'] = self.subtitle

            if self.image_url:
                data['image_url'] = self.image_url

            if self.default_action:
                data['default_action'] = self.default_action.as_dict()

            if self.button:
                data['buttons'] = [self.button.as_dict()]

            return data

        def set_default_action(self, default_action):
            if not isinstance(default_action, Message.DefaultAction):
                raise RuntimeError('object is not a Message.DefaultAction '
                                   'object')

            self.default_action = default_action

        def set_button(self, button):
            if not isinstance(button, Message.Button):
                raise RuntimeError('object is not a Message.Button object')

            self.button = button

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
                    self.payload = payload
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

    class ImageMapAction(object):
        def __init__(self, action_type, text=None, url=None, area=None,
                     variables=None):
            if action_type not in Message.ButtonType:
                raise RuntimeError('Invalid ImageMapAction type')

            variables = variables or {}
            self.type = action_type
            self.text = Render(text, variables)
            self.url = Render(url, variables)
            self.area = area

            if action_type == Message.ButtonType.POSTBACK and not text:
                raise RuntimeError('postback button without text specified')

            if action_type == Message.ButtonType.WEB_URL and not url:
                raise RuntimeError('URL button without URL specified')

            if url and text:
                raise RuntimeError('can not specify text and URL at the '
                                   'same time')

        def __str__(self):
            return json.dumps(self.as_dict())

        def __eq__(self, other):
            return (
                self.type == other.type and
                self.text == other.text and
                self.url == other.url and
                self.area == other.area
            )

        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct QuickReply object given a dictionary."""
            jsonschema.validate(data, cls.schema())

            return cls(Message.ButtonType(data['type']),
                       data.get('text'), data.get('url'), data.get('area'),
                       variables)

        @classmethod
        def schema(cls):
            return {
                'type': 'object',
                'required': ['type', 'area'],
                'properties': {
                    'type': {'enum': ['postback', 'web_url']},
                    'text': {'type': 'string'},
                    'url': {'type': 'string'},
                    'area': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'x': {'type': 'number'},
                            'y': {'type': 'number'},
                            'width': {'type': 'number'},
                            'height': {'type': 'number'}
                        }
                    }
                }
            }

        def as_dict(self):
            if self.type == Message.ButtonType.POSTBACK:
                return {
                    'type': self.type.value,
                    'text': self.text,
                    'area': self.area
                }
            else:
                return {
                    'type': self.type.value,
                    'url': self.url,
                    'area': self.area
                }

    def __init__(self, text=None, image_url=None, buttons_text=None,
                 top_element_style=None, imagemap_url=None,
                 notification_type=NotificationType.REGULAR, variables=None):
        """Constructor.

        Args:
            text: text message to send for a 'Text message'
            image_url: URL of the image for a 'Image message'
            buttons_text: text for a 'Buttons template message'
            top_element_style: top_element_style for a 'List template message'
        """
        if notification_type not in self.NotificationType:
            raise RuntimeError('Invalid notification type')

        if (top_element_style and
                top_element_style not in self.ListTopElementStyle):
            raise RuntimeError('Invalid top_element_style')

        if text and image_url:
            raise RuntimeError('can not specify text and image at the same '
                               'time')

        variables = variables or {}
        self.notification_type = notification_type
        self.text = Render(text, variables)
        self.image_url = Render(image_url, variables)
        self.buttons_text = Render(buttons_text, variables)
        self.top_element_style = top_element_style
        self.bubbles = []
        self.buttons = []
        self.list_items = []
        self.quick_replies = []
        self.imagemap_url = imagemap_url
        self.imagemap_actions = []
        self.register_mapping = False

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
    def FromDict(cls, data, variables=None, register_mapping=False):
        """Construct Message object given a dictionary.

        Args:
            register_mapping: whether or not to register the mapping to input
                transformation list. This is here because we want the derived
                class message.Message to be able to control wether or not to
                register the mapping.
        """
        jsonschema.validate(data, cls.schema())

        variables = variables or {}
        m = cls(data.get('text'), variables=variables)

        # Set register_mapping flag, so the dereived (add_button, add_bubble,
        # ...) methods can decide whether or not to register the mapping.
        m.register_mapping = register_mapping

        attachment = data.get('attachment')
        if attachment:
            if attachment['type'] == 'image':
                m.image_url = Render(attachment['payload'].get('url'),
                                     variables)
            elif attachment['type'] == 'template':
                ttype = attachment['payload']['template_type']
                if ttype == 'button':
                    m.buttons_text = Render(attachment['payload']['text'],
                                            variables)
                    for x in attachment['payload']['buttons']:
                        m.add_button(cls.Button.FromDict(x, variables))
                elif ttype == 'generic':
                    for x in attachment['payload']['elements']:
                        m.add_bubble(cls.Bubble.FromDict(x, variables))
                elif ttype == 'imagemap':
                    m.imagemap_url = Render(
                        attachment['payload'].get('imagemap_url'), variables)
                    for x in attachment['payload']['actions']:
                        m.add_imagemap_action(
                            cls.ImageMapAction.FromDict(x, variables))

        quick_replies = data.get('quick_replies', [])
        for x in quick_replies:
            m.add_quick_reply(cls.QuickReply.FromDict(x, variables))

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
                                }, {
                                    'type': 'object',
                                    'required': ['template_type', 'elements'],
                                    'additionalProperties': True,
                                    'properties': {
                                        'template_type': {
                                            'enum': ['list']
                                        },
                                        'top_element_style': {
                                            'enum': ['large', 'compact'],
                                        },
                                        'elements': {
                                            'type': 'array',
                                            'items': {
                                                '$ref':
                                                    '#/definitions/list_item',
                                            },
                                            'minItems': 2,
                                            'maxItems': 4
                                        },
                                        'buttons': {
                                            'type': 'array',
                                            'items': {
                                                '$ref': '#/definitions/button'
                                            },
                                            'maxItems': 1
                                        }
                                    }
                                }, {
                                    'type': 'object',
                                    'required': ['template_type',
                                                 'imagemap_url', 'actions'],
                                    'additionalProperties': True,
                                    'properties': {
                                        'template_type': {
                                            'enum': ['imagemap']
                                        },
                                        'imagemap_url': {'type': 'string'},
                                        'actions': {
                                            'type': 'array',
                                            'items':
                                            Message.ImageMapAction.schema(),
                                            'minItems': 1,
                                            'maxItems': 50
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
                'list_item': Message.ListItem.schema(),
                'quick_reply': Message.QuickReply.schema()
            }
        }

    def as_dict(self):
        data = {}

        if self.text is not None:
            data['text'] = self.text
        elif self.image_url:
            data['attachment'] = {
                'type': 'image',
                'payload': {'url': self.image_url}
            }
        elif self.buttons_text is not None:
            data['attachment'] = {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': self.buttons_text,
                    'buttons': [x.as_dict() for x in self.buttons]
                }
            }
        elif self.bubbles:
            data['attachment'] = {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': [x.as_dict() for x in self.bubbles]
                }
            }
        elif self.list_items:
            payload = {
                'template_type': 'list',
                'elements': [x.as_dict() for x in self.list_items]
            }

            if self.top_element_style:
                payload['top_element_style'] = self.top_element_style.value

            if self.buttons:
                payload['buttons'] = [self.buttons[0].as_dict()]

            data['attachment'] = {
                'type': 'template',
                'payload': payload
            }
        elif self.imagemap_url:
            data['attachment'] = {
                'type': 'template',
                'payload': {
                    'template_type': 'imagemap',
                    'imagemap_url': self.imagemap_url,
                    'actions': [x.as_dict() for x in self.imagemap_actions]
                }
            }
        else:
            raise RuntimeError('Invalid message type %r' % self)

        if self.quick_replies:
            data['quick_replies'] = [x.as_dict() for x in self.quick_replies]

        return data

    def set_notification_type(self, value):
        if value not in Message.NotificationType:
            raise RuntimeError('Invalid notification type')

        self.notification_type = value

    def add_button(self, button):
        if len(self.buttons) == self.MAX_BUTTONS:
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
        if len(self.bubbles) == self.MAX_BUBBLES:
            raise RuntimeError('maximum allowed bubbles reached')

        if not isinstance(bubble, Message.Bubble):
            raise RuntimeError('object is not a Message.Bubble object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')
        if self.buttons:
            raise RuntimeError('can not specify button and bubble at the '
                               'same time')
        if self.list_items:
            raise RuntimeError('can not specify list item and bubble at the '
                               'same time')

        self.bubbles.append(bubble)

    def add_list_item(self, list_item):
        if len(self.bubbles) == self.MAX_LIST_ITEMS:
            raise RuntimeError('maximum allowed list items reached')

        if not isinstance(list_item, Message.ListItem):
            raise RuntimeError('object is not a Message.ListItem object')

        if self.text:
            raise RuntimeError('can not specify attachment and text at the '
                               'same time')
        if self.bubbles:
            raise RuntimeError('can not specify bubble and list item at the '
                               'same time')
        if len(self.buttons) > 1:
            raise RuntimeError('list message can only have one button')

        self.list_items.append(list_item)

    def add_quick_reply(self, reply):
        if not isinstance(reply, Message.QuickReply):
            raise RuntimeError('object is not a Message.QuickReply object')

        self.quick_replies.append(reply)

    def add_imagemap_action(self, action):
        if not isinstance(action, Message.ImageMapAction):
            raise RuntimeError('object is not a Message.ImageMapAction '
                               'object')

        self.imagemap_actions.append(action)


# To allow pickling inner class, set module attribute alias
setattr(sys.modules[__name__], 'NotificationType', Message.NotificationType)
setattr(sys.modules[__name__], 'ButtonType', Message.ButtonType)
setattr(sys.modules[__name__], 'ListTopElementStyle',
        Message.ListTopElementStyle)
setattr(sys.modules[__name__], 'QuickReplyType', Message.QuickReplyType)
setattr(sys.modules[__name__], 'Button', Message.Button)
setattr(sys.modules[__name__], 'Bubble', Message.Bubble)
setattr(sys.modules[__name__], 'DefaultAction', Message.DefaultAction)
setattr(sys.modules[__name__], 'ListItem', Message.ListItem)
setattr(sys.modules[__name__], 'QuickReply', Message.QuickReply)
