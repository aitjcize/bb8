# -*- coding: utf-8 -*-
"""
    Misc Utilities
    ~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import logging

from scrapy import logformatter


class ContentLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            'level': logging.WARNING,
            'msg': logformatter.DROPPEDMSG,
            'args': {
                'exception': exception,
                'item': item['link'],
            }
        }
