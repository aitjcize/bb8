# -*- coding: utf-8 -*-
"""
    Drama Service Scrapy spider configuration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor


spider_configs = {
    'dramaq': {
        'name': 'dramaq',
        'allowed_domains': ['www.drama01.com', 'www.showq.biz'],
        'start_urls': (
            'http://www.drama01.com/',
            'http://www.drama01.com/tw/',
            'http://www.drama01.com/cn/',
            'http://www.drama01.com/jp/',
        ),
        'custom_settings': {
            'DEPTH_LIMIT': 1
        },
        'rules': (
            Rule(LinkExtractor(
                deny=(r'.*\.php$'),
                restrict_xpaths='//ul[@class="category-module"]',
            ), callback='parse_drama'),
            Rule(LinkExtractor(
                deny=(r'.*\.php$'),
                restrict_xpaths='//td//a',
            ), callback='parse_drama'),
        ),

    },
    'vmus': {
        'name': 'vmus',
        'allowed_domains': ['vmus.co'],
        'start_urls': (
            'http://vmus.co/',
        ),
        'rules': (
            Rule(LinkExtractor(
                allow=('vmus.co/'),
                deny=(r'[sS]\d+[eE]\d+'),
                ), callback='parse_vmus_drama'),
        ),
    }
}
