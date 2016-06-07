# -*- coding: utf-8 -*-
"""
    Search for Youbike Info
    ~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend.module_api import Message, Resolve


def run(content_config, unused_env, variables):
    """
    content_config schema:
    {
       "location": "location variables",
    }
    """
    location = Resolve(content_config['location'], variables)
    return [Message(str(location))]
