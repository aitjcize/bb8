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

    # Number of threads that serve the requests. This should be larger than
    # processes * threads in uwsgi.ini
    N_THREADS = 64

    # Secrets
    JWT_SECRET = 'JWT_SECRET_REPLACE_ME'
    INVITE_MASTER = 'master@compose.ai'

    # Log
    LOG_DIR = BB8_ROOT + '/log'
    LOG_FILE = 'message.log'
    API_SERVICER_LOG_FILE = 'api_servicer.log'

    # Server
    HOSTNAME = os.getenv('BB8_HOSTNAME', 'dev.compose.ai')
    RESOURCE_HOSTNAME = os.getenv('BB8_RESOURCE_HOSTNAME', 'r-dev.compose.ai')
    HTTP_PORT = int(os.getenv('HTTP_PORT', 7000))

    # Ports
    APP_API_SERVICE_PORT = 62629
    APP_GRPC_SERVICE_PORT = int(os.getenv('APP_RPC_PORT', 9999))

    # Webhooks
    BOT_WEBHOOOK_ROOT = '/bot'

    # Options
    COMMIT_ON_APP_TEARDOWN = True
    STORE_CONVERSATION = True

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
    FACEBOOK_APP_ID = '1663575030609051'
    FACEBOOK_APP_SECRET = 'a4dd467d54ffe8eef263bc58f3fcc750'

    # Line
    LINE_WEBHOOK_PATH = BOT_WEBHOOOK_ROOT + '/line/<provider_ident>'

    GCP_PROJECT = 'dotted-lexicon-133523'

    # Datadog
    DATADOG_API_KEY = '5443ec4b9da5f217eef3f035df22a62c'
    DATADOG_APP_KEY = '7003bcefefe66024a1830488ab11b359eade0b92',
    DATADOG_HOST = scoped_name('bb8.service.datadog')
    ENV_TAG = 'dev'

    # Stripe
    STRIPE_API_KEY = 'sk_test_4XMwouS8QrK95TxVSe1dJi3M'
    # Basic Auth: composeai:ad9e0957a41257
    STRIPE_WEBHOOK_CREDENTIAL = 'Y29tcG9zZWFpOmFkOWUwOTU3YTQxMjU3'
    STRIPE_PLANS = [
        {
            'name': 'Basic Plan',
            'id': 'basic-monthly',
            'interval': 'month',
            'currency': 'usd',
            'amount': 7,
            'trial_period_days': 7
        }
    ]

    # Celery
    class CeleryConfig(object):
        broker_url = (os.getenv('REDIS_URI', 'redis://localhost:6379') + '/0')
        imports = (
            'bb8.backend.broadcast',
            'bb8.backend.messaging_tasks',
            'bb8.backend.webhooks_tasks',
        )
        send_events = False
        accept_content = ['pickle']
        task_serializer = 'pickle'

    # Dogpile Cache
    DOGPILE_CACHE_CONFIG = {
        'default': {
            'url': os.getenv('REDIS_URI', 'redis://localhost:6379') + '/1',
            'redis_expiration_time': 60 * 60 * 2,  # 2 hours
            'distributed_lock': True
        }
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

    # Secrets
    JWT_SECRET = '4e1243bd22c66e76c2ba9eddc1f91394e57f9f83'

    # Server
    HOSTNAME = os.getenv('BB8_HOSTNAME', 'bot.compose.ai')
    RESOURCE_HOSTNAME = os.getenv('BB8_RESOURCE_HOSTNAME', 're.compose.ai')

    # Options
    STORE_CONVERSATION = False

    # Third-Party apps hostname map
    APP_HOSTNAME_MAP = {
        'system':   'bb8.app.system',
        'youbike':  'bb8.app.youbike',
        'content':  'bb8.app.content',
        'drama':    'bb8.app.drama',
    }

    # Messaging provider config
    # Facebook
    FACEBOOK_APP_ID = '1797497130479857'
    FACEBOOK_APP_SECRET = '132f7214f7753be8ff8d235af0b7bd20'

    # Datadog
    DATADOG_HOST = 'bb8.service.datadog'
    ENV_TAG = 'prod'

    # Celery
    class CeleryConfig(DevelopmentConfig.CeleryConfig):
        broker_url = os.getenv('REDIS_URI',
                               'redis://bb8.service.redis:6379') + '/0'

    # Dogpile Cache
    DOGPILE_CACHE_CONFIG = {
        'default': {
            'url': (os.getenv('REDIS_URI', 'redis://bb8.service.redis:6379') +
                    '/1'),
            'redis_expiration_time': 60 * 60 * 2,  # 2 hours
            'distributed_lock': True
        }
    }
