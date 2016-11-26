# -*- coding: utf-8 -*-
"""
    __init__ for APIs
    ~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from flask import jsonify

# Register request handlers
from bb8 import app, logger

# pylint: disable=W0611
from bb8.api import (request, webhooks, accounts, bots, broadcasts, platforms,
                     threads, third_party, misc)
from bb8.api.error import AppError


def on_app_error(e):
    logger.error(str(e))
    return jsonify(message=e.message, error_code=e.error_code), e.status_code

app.errorhandler(AppError)(on_app_error)
