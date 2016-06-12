# -*- coding: utf-8 -*-
"""
    bb8 application error
    ~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""


class AppError(Exception):
    """ Custom application error """

    def __init__(self, status_code, error_code, message):
        super(AppError, self).__init__(status_code, error_code, message)
        if status_code >= 600 or status_code < 200:
            status_code = 500
        self.status_code = status_code
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return "status_code: %d, error_code: %d, message: %s" % \
                (self.status_code, self.error_code, self.message)
