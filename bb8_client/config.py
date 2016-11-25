# -*- coding: utf-8 -*-
"""
    bb8 Client API config
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os


class Config(object):
    HOSTNAME = 'dev.compose.ai'
    RESOURCE_HOSTNAME = 'r-dev.compose.ai'
    HTTP_PORT = os.getenv('BB8_HTTP_PORT', 7000)
    HOST = 'bb8.main'
    PORT = 62629


class TestingConfig(Config):
    HOST = 'localhost'


class DevelopmentConfig(Config):
    HOST = '%s.bb8.main' % os.getenv('BB8_SCOPE', 'nobody')


class DeployConfig(Config):
    HOSTNAME = 'bot.compose.ai'
    RESOURCE_HOSTNAME = 'd.compose.ai'
    HTTP_PORT = 5000
