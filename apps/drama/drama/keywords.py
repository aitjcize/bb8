# -*- coding: utf-8 -*-
"""
    Utilities for collecting trending keywords
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import contextlib
import logging
import urllib
import urlparse

import lxml.html


def extract_popular_dramas():
    """Extracts popular dramas from dramaq.biz, the order on their
        front page impliest the popularity order
    """
    country_list = {
        'kr': 'http://www.dramaq.biz/',
        'tw': 'http://www.dramaq.biz/tw/',
        'cn': 'http://www.dramaq.biz/cn/',
        'jp': 'http://www.dramaq.biz/jp/',
    }

    def popular_drama(country):
        try:
            url = country_list[country]
            with contextlib.closing(urllib.urlopen(url)) as page:
                response = lxml.html.fromstring(page.read())
        except Exception:
            logging.warning('Cannot fetch country: ' + country)
            return []

        hrefs = response.xpath('//td/a[1]/@href')
        links = [unicode(urlparse.urljoin(url, href)) for href in hrefs]
        return links

    return {country: popular_drama(country) for country in country_list}
