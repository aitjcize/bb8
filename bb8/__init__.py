# -*- coding: utf-8 -*-
"""
    bb8 module init
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from flask import Flask, jsonify

from bb8 import config as Config
from bb8.logger import Logger
from bb8.error import AppError

config = None

if not os.getenv('CIRCLE_CI', '') == 'true':
    config = Config.TestingConfig()
else:
    config = Config.DevelopmentConfig()  # pylint: disable=R0204

app = Flask(__name__)
app.config.from_object(config)

logger = Logger(config)


def on_app_error(e):
    logger.error(str(e))
    return jsonify(message=e.message, error_code=e.error_code), e.status_code

app.errorhandler(AppError)(on_app_error)
