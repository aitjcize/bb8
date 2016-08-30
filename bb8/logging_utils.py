# -*- coding: utf-8 -*-
"""
    Provides logging utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import logging
from logging.handlers import RotatingFileHandler

import os
import sys


class Logger(object):
    def __init__(self, filename, name='bb8'):
        try:
            os.makedirs(os.path.dirname(filename))
        except Exception:
            pass
        self.logger = self.create_logger(filename, name)

    @classmethod
    def get_logger(cls, name):
        return logging.getLogger(name)

    @classmethod
    def create_logger(cls, filename, name):
        """Return a rotating logger"""
        handler = RotatingFileHandler(filename,
                                      maxBytes=1048576,
                                      backupCount=10,
                                      encoding='UTF-8')
        formatter = logging.Formatter('%(asctime)s %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        return logger

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def warn(self, *args, **kwargs):
        self.logger.warn(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs):
        self.logger.exception(*args, **kwargs)
