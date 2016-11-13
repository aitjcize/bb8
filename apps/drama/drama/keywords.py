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
    # Drama Q
    country_list = {
        'kr': 'http://www.dramaq.biz/',
        'tw': 'http://www.dramaq.biz/tw/',
        'cn': 'http://www.dramaq.biz/cn/',
        'jp': 'http://www.dramaq.biz/jp/',
    }

    def popular_dramaq(country):
        try:
            url = country_list[country]
            with contextlib.closing(urllib.urlopen(url)) as page:
                response = lxml.html.fromstring(page.read())
        except Exception:
            logging.warning('Cannot fetch country: ' + country)
            return []

        hrefs = response.xpath('//td/a[1]/@href').extract()
        links = [unicode(urlparse.urljoin(url, href)) for href in hrefs]
        return links

    # Vmus
    def popular_vmus():
        try:
            url = 'http://vmus.co/?s=%E9%80%A3%E8%BC%89%E4%B8%AD'
            with contextlib.closing(urllib.urlopen(url)) as page:
                response = lxml.html.fromstring(page.read())
        except Exception:
            logging.warning('Cannot fetch popular drama for vmus')
            return []

        return response.xpath('//html/body/div[@id="wrapper"]/div[@id="wrap"]'
                              '/section[@id="content"]/article'
                              '/h2/a/@href').extract()

    result = {country: popular_dramaq(country) for country in country_list}
    result['us'] = popular_vmus()

    return result
