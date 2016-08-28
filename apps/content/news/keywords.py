# -*- coding: utf-8 -*-
"""
    Utilities for collecting trending keywords
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""


import contextlib
import logging
import urllib

import lxml.html

from news.database import Entry


CHINA_TIMES = 'http://www.chinatimes.com/search/keyword/'


def extract_keywords_ct():
    """Extract the keywords from China Times

    Returns:
        keywords: a dictionary with key as the major
            keyword, and the value is a list of correlated
            keywords of the key
    """

    try:
        with contextlib.closing(urllib.urlopen(CHINA_TIMES)) as page:
            response = lxml.html.fromstring(page.read())
    except Exception:
        logging.warning('Cannot open url: ' + CHINA_TIMES)
        return {}

    blocks = response.xpath(
        '(//div[@class="rl_content"]/div[@class="day"])[1]'
        '//li[@class="clear-fix"]')

    keywords = {}
    for block in blocks:
        try:
            kw = block.xpath(
                './/div[@class="k1 clear-fix"]/a/text()')[0]
            related = block.xpath('.//p/a/text()')

            if validate_keyword(kw):
                keywords[kw] = [r for r in related
                                if validate_keyword(r)]
        except Exception:
            logging.warning(
                'Unexpected syntax while parsing ' + CHINA_TIMES)

    return keywords


def validate_keyword(keyword):
    """Validate this keyword by querying our database
        to see if this keyword can related to any content
    """
    entries = Entry.search(keyword, 10)
    return len(entries) > 0
