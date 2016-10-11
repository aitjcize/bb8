# -*- coding: utf-8 -*-
"""
    Initialization of drama module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import logging
import os


class Config(object):
    DATABASE = os.getenv('DATABASE', '')
    N_THREADS = 8
    DEFAULT_DRAMA_IMAGE = 'http://i.imgur.com/xa9wSAU.png'


class DevelopmentConfig(Config):
    pass


class DeployConfig(Config):
    DATABASE = ('mysql+pymysql://dramadeploy:dramadeploymysql@/drama?'
                'unix_socket=/cloudsql/dotted-lexicon-133523:asia-east1:bb8&'
                'charset=utf8mb4')


def ConfigureLogger():
    logger_ = logging.getLogger('news')
    logger_.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger_.addHandler(ch)
    return logger_


logger = ConfigureLogger()

if os.getenv('BB8_DEPLOY', '') == 'true':
    logger.info('In deploy mode')
    config = DeployConfig()  # pylint: disable=R0204
else:
    logger.info('In development mode')
    config = DevelopmentConfig()  # pylint: disable=R0204

logger.info('Database URI: %s', config.DATABASE)
