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

    # Number of threads that serve the requests. This should be the same
    # as processes * threads in uwsgi.ini
    N_THREADS = 32

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

    # Ports
    APP_API_SERVICE_PORT = 62629
    APP_GRPC_SERVICE_PORT = 9999

    # Webhooks
    BOT_WEBHOOOK_ROOT = '/bot'

    # Facebook
    FACEBOOK_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + '/facebook'
    FACEBOOK_WEBHOOK_VALIDATION_TOKEN = 'meow_meow_meow'

    # Line
    LINE_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + '/line'

    # Option
    COMMIT_ON_APP_TEARDOWN = True
    STORE_CONVERSATION = False

    # Misc
    YOUBIKE_BOT_GA_ID = 'UA-79887532-2'

    # Third-Party apps hostname map
    APP_HOSTNAME_MAP = {
        'system':   'localhost',
        'youbike':  'localhost',
        'content':  'localhost',
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

    # Third-Party apps hostname map
    APP_HOSTNAME_MAP = {
        'system':   'bb8.app.system',
        'youbike':  'bb8.app.youbike',
        'content':  'bb8.app.content',
    }
