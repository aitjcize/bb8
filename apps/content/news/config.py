# -*- coding: utf-8 -*-
"""
    Spider configs
    ~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor


spider_configs = {
    'yahoo_rss': {
        'name': 'yahoo_rss',
        'allowed_domains': ['yahoo.com'],
        'start_urls': (
            'http://tw.news.yahoo.com/rss/realtime',
            'http://tw.news.yahoo.com/rss/politics',
            'http://tw.news.yahoo.com/rss/taiwan',
            'http://tw.news.yahoo.com/rss/tech',
            'http://tw.news.yahoo.com/rss/sports',
            'http://tw.news.yahoo.com/rss/edu',
            'http://tw.news.yahoo.com/rss/life',
        ),
        'custom_settings': {
            'DEPTH_LIMIT': 1
        },
        'extractor': {
            'title': '//title/text()',
            'content': '//div[@class="yom-mod yom-art-content "]'
                       '/div[@class="bd"]/*/text()',
            'description': '',
            'images': '//div[@class="yom-mod yom-art-content "]'
                      '/div[@class="bd"]/*//img',
            'author': '',
            'source': 'yahoo_rss',
        },
    },
    'storm': {
        'name': 'storm',
        'allowed_domains': ['storm.mg'],
        'start_urls': (
            'http://www.storm.mg',
        ),
        'custom_settings': {
            'DEPTH_LIMIT': 1
        },
        'rules': (
            Rule(LinkExtractor(allow=(r'category\/\d+'),
                               deny=(r'category\/\d+\/[0-9][0-9]'),
                               unique=True),
                 follow=True),
            Rule(LinkExtractor(allow=(r'article\/\d+'),
                               unique=True),
                 callback='parse_item',
                 follow=False),
        ),
        'extractor': {
            'title': '//title/text()',
            'content': '//div[@class="article-wrapper"]'
                       '/article/*[self::h2 or self::p]//text()',
            'description': '',
            'images': '//div[contains(@class, "article-wrapper")'
                      ' or contains(@class, "mainPic")]'
                      '//img[re:test(@src, "^http")]',
            'author': '',
            'publish_time': '',
            'original_source': '',
        },
    },
}
