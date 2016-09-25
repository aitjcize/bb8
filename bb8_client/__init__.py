# -*- coding: utf-8 -*-
"""
    bb8 Client API init
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from config import DevelopmentConfig, DeployConfig, TestingConfig

config = None

if os.getenv('BB8_TEST', '') == 'true':
    config = TestingConfig()  # pylint: disable=R0204
elif os.getenv('BB8_DEPLOY', '') == 'true':
    config = DeployConfig()  # pylint: disable=R0204
else:
    config = DevelopmentConfig()  # pylint: disable=R0204
