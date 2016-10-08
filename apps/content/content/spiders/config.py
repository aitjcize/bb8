# -*- coding: utf-8 -*-
"""
    Content service Scrapy spider configuraton
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
                       '/div[@class="bd"]',
            'description': '',
            'images': ('//div[@class="yom-mod yom-art-content "]'
                       '//img', '@src', '@alt'),
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
                       '/article//p',
            'description': '',
            'images': [
                ('//div[contains(@class, "mainPic")]'
                 '//img[re:test(@src, "^http")]', '@src', '@alt'),
                ('//div[contains(@class, "article-wrapper")]'
                 '/article//img[re:test(@src, "^http")]', '@src', '@alt'),
                ('//div[contains(@class, "image")]'
                 '//img[re:test(@src, "^http")]', '@src', '@alt')
            ],
            'author': '',
            'publish_time': '',
            'original_source': '',
        },
    },
    'thenewslens': {
        'name': 'thenewslens',
        'allowed_domains': ['thenewslens.com'],
        'start_urls': (
            'http://www.thenewslens.com/',
        ),
        'custom_settings': {
            'DEPTH_LIMIT': 2
        },
        'rules': (
            Rule(LinkExtractor(allow=(r'category\/.*'),
                               unique=True),
                 follow=True),
            Rule(LinkExtractor(allow=(r'article\/\d+'),
                               unique=True),
                 callback='parse_item',
                 follow=False),
        ),
        'extractor': {
            'title': '//title/text()',
            'content': '(//div[@class="article-content"])[1]',
            'description': '//meta[@name="description"]/@content',
            'images': [
                # The news lens stores meaningless message in alt,
                # so don't extract it
                ('//img[contains(@class, "front-img")]', '@src-lg', ''),
                ('//figure[contains(@class, "article-img-container")]//img',
                 '@src-lg', '')
            ],
            'author': '',
            'publish_time': '',
            'original_source': '',
        },
    }
}
