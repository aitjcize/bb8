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

import jsonschema

from flask import g
from sqlalchemy import desc, func

from bb8 import logger
from bb8.backend import base_message
from bb8.backend.database import ColletedDatum
from bb8.backend.metadata import InputTransformation
from bb8.backend.query_filters import FILTERS
from bb8.backend.util import image_convert_url


VARIABLE_RE = re.compile('^{{(.*?)}}$')
HAS_VARIABLE_RE = base_message.HAS_VARIABLE_RE


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


def parse_query(expr):
    """Parse query expression."""
    parts = expr.split('|')
    query = parts[0]
    filters = parts[1:]

    m = re.match(r'^q(all)?\.([^.]*)$', query)
    if not m:
        return expr

    key = m.group(2)
    q = ColletedDatum.query(ColletedDatum.value, ColletedDatum.created_at)
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
            m = re.match(r'get\((\d+)\)', f)
            if m:
                result = q.offset(int(m.group(1))).limit(1).first()
                result = result.value if result else None
                break
            m = re.match(r'lru\((\d+)\)', f)
            if m:
                result = ColletedDatum.query(
                    ColletedDatum.value,
                    func.max(ColletedDatum.created_at).label('latest')
                ).filter_by(
                    key=key,
                    user_id=g.user.id
                ).group_by(
                    ColletedDatum.value
                ).order_by(
                    desc('latest')
                ).offset(int(m.group(1))).limit(1).first()
                result = result.value if result else None
                break
            if f == 'last':
                result = q.order_by(ColletedDatum.created_at.desc()).first()
                result = result.value if result else None
                break
            elif f == 'count':
                result = q.count()
                break
            elif f == 'uniq':
                q = q.distinct(ColletedDatum.value)
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
        return None

    if result is None:
        if filters:
            m = re.match(r'fallback\(\'(.*)\'\)', filters[0])
            if m:
                return m.group(1)
        return None

    # Parse transform filter
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
            ret = parse_query(expr)
        else:
            ret = base_message.parse_variable(expr, variables)
        return ret if ret is not None else m.group(0)
    return HAS_VARIABLE_RE.sub(replace, base_message.to_unicode(template))


# Monkey Patch!
# Patch base_message's render message so it supports query expression
base_message.Render = Render


class Message(base_message.Message):
    """Wraps base_message.Message to provide extra function."""

    NotificationType = base_message.Message.NotificationType
    ButtonType = base_message.Message.ButtonType

    class _Button(base_message.Message.Button):
        @classmethod
        def FromDict(cls, data, variables=None):
            """Construct Button object given a button dictionary."""
            jsonschema.validate(data, cls.schema())

            payload = data.get('payload')
            if payload and isinstance(payload, dict):
                payload['node_id'] = g.node.id
                payload = json.dumps(payload)

            return cls(Message.ButtonType(data['type']),
                       data['title'], data.get('url'), payload,
                       data.get('acceptable_inputs'), variables)

        def register_mapping(self, key):
            if self.type == Message.ButtonType.POSTBACK:
                acceptable_inputs = self.acceptable_inputs[:]
                acceptable_inputs.extend(['^%s$' % key, self.title])
                InputTransformation.add_mapping(acceptable_inputs,
                                                self.payload)

    # Patch Message.Button
    base_message.Message.Button = _Button

    class _Bubble(base_message.Message.Bubble):
        def register_mapping(self, key):
            for idx, button in enumerate(self.buttons):
                button.register_mapping(key + r'-' + str(idx + 1))

    # Patch Message.Bubble
    base_message.Message.Bubble = _Bubble

    class _QuickReply(base_message.Message.QuickReply):
        def register_mapping(self):
            if self.acceptable_inputs:
                acceptable_inputs = self.acceptable_inputs[:]
                acceptable_inputs.append(self.title)
                InputTransformation.add_mapping(acceptable_inputs,
                                                self.payload)

    # Patch Message.QuickReply
    base_message.Message.QuickReply = _QuickReply

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
            for card_i, bubble in enumerate(self.bubbles):
                msg_text = bubble.title + '\n'
                if bubble.subtitle:
                    msg_text += bubble.subtitle + '\n'

                for i, but in enumerate(bubble.buttons):
                    if but.type == Message.ButtonType.WEB_URL:
                        msg_text += u'%d-%d. %s <%s>\n' % (card_i + 1, i + 1,
                                                           but.title, but.url)
                    else:
                        msg_text += u'%d-%d. %s\n' % (card_i + 1, i + 1,
                                                      but.title)

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

    def add_button(self, button):
        super(Message, self).add_button(button)
        button.register_mapping(str(len(self.buttons)))

    def add_bubble(self, bubble):
        super(Message, self).add_bubble(bubble)
        bubble.register_mapping(str(len(self.bubbles)))

    def add_quick_reply(self, reply):
        super(Message, self).add_quick_reply(reply)
        reply.register_mapping()
