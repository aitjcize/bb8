# -*- coding: utf-8 -*-
"""
    bb8 module init
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from flask import Flask, jsonify
from celery import Celery

from bb8 import configuration
from bb8.logging_utils import Logger
from bb8.error import AppError


SRC_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))

config = None

if os.getenv('BB8_TEST', '') == 'true':
    config = configuration.TestingConfig()  # pylint: disable=R0204
elif os.getenv('BB8_DEPLOY', '') == 'true':
    config = configuration.DeployConfig()  # pylint: disable=R0204
else:
    config = configuration.DevelopmentConfig()  # pylint: disable=R0204

app = Flask(__name__)
app.config.from_object(config)

celery = Celery()
celery.config_from_object(config.CeleryConfig)

logger = Logger(os.path.join(config.LOG_DIR, config.LOG_FILE))


def on_app_error(e):
    logger.error(str(e))
    return jsonify(message=e.message, error_code=e.error_code), e.status_code

app.errorhandler(AppError)(on_app_error)
