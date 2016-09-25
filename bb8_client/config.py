# -*- coding: utf-8 -*-
"""
    bb8 Client API config
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""


class Config(object):
    HOST = 'bb8.main'
    PORT = 62629


class TestingConfig(Config):
    HOST = 'localhost'


class DevelopmentConfig(Config):
    pass


class DeployConfig(Config):
    pass
