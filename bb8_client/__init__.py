# -*- coding: utf-8 -*-
"""
    bb8 Client API init
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from config import TestingConfig, DevelopmentConfig, DeployConfig

config = None

if os.getenv('CIRCLE_CI', '') == 'true':
    config = TestingConfig()  # pylint: disable=R0204
elif os.getenv('BB8_DEPLOY', '') == 'true':
    config = DeployConfig()  # pylint: disable=R0204
else:
    config = DevelopmentConfig()  # pylint: disable=R0204
