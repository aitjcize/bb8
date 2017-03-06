# -*- coding: utf-8 -*-
"""
    Utilities for collecting trending keywords
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import contextlib
import logging
import urllib2
import urlparse

import lxml.html


FAKE_USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/54.0.2840.98 Safari/537.36')


def extract_popular_dramas():
    """Extracts popular dramas from drama01.com, the order on their
        front page impliest the popularity order
    """
    # Drama Q
    country_list = {
        'kr': 'http://www.drama01.com/',
        'tw': 'http://www.drama01.com/tw/',
        'cn': 'http://www.drama01.com/cn/',
        'jp': 'http://www.drama01.com/jp/',
    }

    def popular_dramaq(country):
        try:
            url = country_list[country]
            with contextlib.closing(urllib2.urlopen(url)) as page:
                response = lxml.html.fromstring(page.read())
        except Exception:
            logging.warning('Cannot fetch country: ' + country)
            return []

        hrefs = response.xpath('//td/a[1]/@href')
        links = [unicode(urlparse.urljoin(url, href)) for href in hrefs]
        return links

    # Vmus
    def popular_vmus():
        try:
            url = 'http://vmus.co/?s=%E9%80%A3%E8%BC%89%E4%B8%AD'
            # CloudFlare blocks us if our user agent is python urllib
            r = urllib2.Request(url, headers={'User-Agent': FAKE_USER_AGENT})
            with contextlib.closing(urllib2.urlopen(r)) as page:
                response = lxml.html.fromstring(page.read())
        except Exception:
            logging.warning('Cannot fetch popular drama for vmus')
            return []

        return response.xpath('//h2/a/@href')

    result = {country: popular_dramaq(country) for country in country_list}
    result['us'] = popular_vmus()

    return result
