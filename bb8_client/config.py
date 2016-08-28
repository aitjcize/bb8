# -*- coding: utf-8 -*-
"""
    bb8 Client API config
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""


class Config(object):
    HOST = 'localhost'
    PORT = 62629


class DevelopmentConfig(Config):
    pass


class DeployConfig(Config):
    HOST = '172.17.0.1'
