# -*- coding: utf-8 -*-
"""
    Misc Util
    ~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64

from bb8 import config


def image_convert_url(url, max_size_tuple):
    return ('https://%s:%d/util/image_convert?size=%dx%d&url=%s' %
            ((config.HOSTNAME, config.PORT) + max_size_tuple +
             (base64.b64encode(url),)))
