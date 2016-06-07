# -*- coding: utf-8 -*-
"""
    bb8 module init
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import os

from flask import Flask

from bb8 import config as Config
from bb8.logger import Logger

config = None

if not os.getenv('CIRCLE_CI', '') == 'true':
    config = Config.TestingConfig()
else:
    config = Config.DevelopmentConfig()  # pylint: disable=R0204

app = Flask(__name__)
app.config.from_object(config)

logger = Logger(config)
