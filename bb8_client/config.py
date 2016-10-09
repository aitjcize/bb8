# -*- coding: utf-8 -*-
"""
    bb8 Client API config
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os


class Config(object):
    HOST = 'bb8.main'
    PORT = 62629


class TestingConfig(Config):
    HOST = 'localhost'


class DevelopmentConfig(Config):
    HOST = '%s.bb8.main' % os.getenv('BB8_SCOPE', 'nobody')


class DeployConfig(Config):
    pass
