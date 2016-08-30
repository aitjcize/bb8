# -*- coding: utf-8 -*-
"""
    bb8 Client API init
    ~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from config import DevelopmentConfig, DeployConfig

config = DevelopmentConfig()  # pylint: disable=R0204

if os.getenv('BB8_DEPLOY', '') == 'true':
    config = DeployConfig()  # pylint: disable=R0204
