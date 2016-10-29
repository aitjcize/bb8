# -*- coding: utf-8 -*-
"""
    Configuration file for bb8
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Please specify all global configuration in this file.

    Copyright 2016 bb8 Authors
"""

import os


def scoped_name(name):
    """Return the scoped name for a given bb8 object name."""
    return '%s.%s' % (os.getenv('BB8_SCOPE', 'nobody'), name)


class Config(object):
    DEBUG = True
    TESTING = False
    DEPLOY = False

    BB8_ROOT = '/tmp/bb8.%s' % os.getenv('BB8_SCOPE', 'nobody')
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
    HOSTNAME = os.getenv('BB8_HOSTNAME', 'dev.compose.ai')
    HTTP_PORT = int(os.getenv('HTTP_PORT', 7000))

    # Ports
    APP_API_SERVICE_PORT = 62629
    APP_GRPC_SERVICE_PORT = int(os.getenv('APP_RPC_PORT', 9999))

    # Webhooks
    BOT_WEBHOOOK_ROOT = '/bot'

    # Options
    COMMIT_ON_APP_TEARDOWN = True
    STORE_CONVERSATION = False

    # Third-Party apps hostname map
    if os.getenv('BB8_IN_DOCKER', False) == 'true':
        APP_HOSTNAME_MAP = {
            'system':   scoped_name('bb8.app.system'),
            'youbike':  scoped_name('bb8.app.youbike'),
            'content':  scoped_name('bb8.app.content'),
            'drama':    scoped_name('bb8.app.drama'),
        }
    else:
        APP_HOSTNAME_MAP = {
            'system':   'localhost',
            'youbike':  'localhost',
            'content':  'localhost',
            'drama':    'localhost',
        }

    # Messaging provider config
    # Facebook
    FACEBOOK_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + '/facebook'
    FACEBOOK_WEBHOOK_VALIDATION_TOKEN = 'meow_meow_meow'

    # Line
    LINE_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + '/line/<provider_ident>'

    GCP_PROJECT = 'dotted-lexicon-133523'

    class CeleryConfig(object):
        BROKER_URL = os.getenv('REDIS_URI', 'redis://localhost:6379/0')
        CELERY_IMPORTS = ('bb8.backend.messaging', 'bb8.backend.broadcast',
                          'bb8.backend.webhooks_tasks')
        CELERY_SEND_EVENTS = False
        CELERY_ACCEPT_CONTENT = ['pickle']


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
    HOSTNAME = os.getenv('BB8_HOSTNAME', 'bot.compose.ai')

    # Third-Party apps hostname map
    APP_HOSTNAME_MAP = {
        'system':   'bb8.app.system',
        'youbike':  'bb8.app.youbike',
        'content':  'bb8.app.content',
        'drama':    'bb8.app.drama',
    }

    class CeleryConfig(DevelopmentConfig.CeleryConfig):
        BROKER_URL = 'redis://bb8.service.redis:6379/0'
