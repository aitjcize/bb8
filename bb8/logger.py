# -*- coding: utf-8 -*-
"""
    Provides logging utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import sys
import logging

from logging.handlers import RotatingFileHandler
from os import makedirs


class Logger(object):
    def __init__(self, config):
        try:
            makedirs(config.LOG_DIR)
        except Exception:
            pass
        self.logger = self.create_logger(config.LOG_FILE, 'bb8')

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
