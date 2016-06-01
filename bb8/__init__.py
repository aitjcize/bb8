# -*- coding: utf-8 -*-
"""
    bb8 module init
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from bb8 import config as Config

config = None

if not os.getenv('CIRCLE_CI', '') == 'true':
    config = Config.TestingConfig()
else:
    config = Config.DevelopmentConfig()  # pylint: disable=R0204
