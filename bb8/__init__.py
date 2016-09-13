# -*- coding: utf-8 -*-
"""
    bb8 module init
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from flask import Flask, jsonify

from bb8 import configuration
from bb8.logging_utils import Logger
from bb8.error import AppError

config = None

if os.getenv('CIRCLE_CI', '') == 'true':
    config = configuration.TestingConfig()  # pylint: disable=R0204
elif os.getenv('BB8_DEPLOY', '') == 'true':
    config = configuration.DeployConfig()  # pylint: disable=R0204
else:
    config = configuration.DevelopmentConfig()  # pylint: disable=R0204

app = Flask(__name__)
app.config.from_object(config)

logger = Logger(os.path.join(config.LOG_DIR, config.LOG_FILE))


def on_app_error(e):
    logger.error(str(e))
    return jsonify(message=e.message, error_code=e.error_code), e.status_code

app.errorhandler(AppError)(on_app_error)
