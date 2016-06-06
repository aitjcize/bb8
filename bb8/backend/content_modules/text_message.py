# -*- coding: utf-8 -*-
"""
    Send a text message
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.messaging import Message


def run(content_config):
    text = content_config.get('text', None)
    if text:
        return [Message(text)]
    return []
