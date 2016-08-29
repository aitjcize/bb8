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
    LOG_FILE = 'message.log'
    API_SERVICER_LOG_FILE = 'api_servicer.log'

    # Server
    HOSTNAME = 'bot.azhuang.me'
    PORT = int(os.getenv('HTTP_PORT', 7000))

    # App API
    APP_API_SERVICE_PORT = 62629

    # Webhooks
    BOT_WEBHOOOK_ROOT = '/bot'

    # Facebook
    FACEBOOK_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + "/facebook"
    FACEBOOK_WEBHOOK_VALIDATION_TOKEN = "meow_meow_meow"

    # Line
    LINE_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + "/line"

    # Option
    COMMIT_ON_APP_TEARDOWN = True
    STORE_CONVERSATION = False

    # Misc
    YOUBIKE_BOT_GA_ID = 'UA-79887532-2'

    # Third-Party apps address mapping
    APPS_ADDR_MAP = {
        'system':   ('localhost', 30000),
        'youbike':  ('localhost', 30001),
        'content':  ('localhost', 30002)
    }


class DevelopmentConfig(Config):
    DEBUG = True

    # Database
    DATABASE = os.getenv(
        'DATABASE',
        'mysql+pymysql://bb8:bb8test@127.0.0.1:3307/bb8?charset=utf8mb4')


class TestingConfig(DevelopmentConfig):
    TESTING = True


class DeployConfig(DevelopmentConfig):
    DEBUG = False
    DEPLOY = True

    BB8_ROOT = '/var/lib/bb8'

    # Log
    LOG_DIR = BB8_ROOT + '/app_log'

    # Server
    HOSTNAME = 'bot.compose.ai'
    PORT = 5000

    # Third-Party apps address mapping
    APPS_ADDR_MAP = {
        'system':   ('172.17.0.1', 30000),
        'youbike':  ('172.17.0.1', 30001),
        'content':  ('172.17.0.1', 30002)
    }
