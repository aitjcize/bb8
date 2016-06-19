#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Util unittest
    ~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import base64
import re
import unittest

from urllib2 import urlparse

from bb8.backend.util import image_convert_url


class UtilUnittest(unittest.TestCase):
    def test_image_convert_url(self):
        test_url = 'http://test.com'
        url = image_convert_url(test_url, (1024, 1024))
        p = urlparse.urlparse(url)
        urlp = base64.b64decode(re.search(r'url=(.*?)&?$', p.query).group(1))
        self.assertEquals(urlp, test_url)


if __name__ == '__main__':
    unittest.main()
