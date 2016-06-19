# -*- coding: utf-8 -*-
"""
    Configuration file for bb8
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Please specify all global configuration in this file.

    Copyright 2016 bb8 Authors
"""

import os


class Config(object):
    DEBUG = True
    TESTING = False
    DEPLOY = False

    BB8_ROOT = '/tmp/bb8'
    LOCK_DIR = BB8_ROOT + '/lock'
    RECORDS_PER_PAGE = 50

    # Secrets
    # FIXME: Replace these secrets in production
    JWT_SECRET = 'JWT_SECRET_REPLACE_ME'
    # Secret key for Flask session
    SECRET_KEY = 'SECRET_KEY_REPLACE_ME'

    # Log
    LOG_DIR = BB8_ROOT + '/log'
    LOG_FILE = LOG_DIR + '/message.log'

    # Server
    HOSTNAME = 'bot.azhuang.me'
    PORT = 7000

    # Webhooks
    BOT_WEBHOOOK_ROOT = '/bot'

    # Facebook
    FACEBOOK_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + "/facebook"
    FACEBOOK_WEBHOOK_VALIDATION_TOKEN = "meow_meow_meow"

    LINE_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + "/line"


class DevelopmentConfig(Config):
    DEBUG = True

    # Database
    DATABASE = os.getenv('DATABASE', 'sqlite:////tmp/bb8.db')


class TestingConfig(DevelopmentConfig):
    TESTING = True


class DeployConfig(DevelopmentConfig):
    DEBUG = False
    DEPLOY = True

    # Server
    PORT = 5000
