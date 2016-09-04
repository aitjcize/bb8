# -*- coding: utf-8 -*-
"""
    Initialization of content module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import logging
import os


class Config(object):
    DATABASE = os.getenv('DATABASE',
                         'mysql+pymysql://bb8:bb8test'
                         '@172.17.0.1:3307/bb8?charset=utf8mb4')
    N_THREADS = 8
    ENABLE_CRAWLER = True


class DevelopmentConfig(Config):
    ENTRY_ENTITY = 'entries-dev'
    ENABLE_CRAWLER = True


class DeployConfig(Config):
    DATABASE = ('mysql+pymysql://contentdeploy:contentdeploymysql@/content?'
                'unix_socket=/cloudsql/dotted-lexicon-133523:asia-east1:bb8&'
                'charset=utf8mb4')
    ENTRY_ENTITY = 'entries'
    ENABLE_CRAWLER = True


def ConfigureLogger():
    logger_ = logging.getLogger('content')
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
