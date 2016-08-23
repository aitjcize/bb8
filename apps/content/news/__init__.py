# -*- coding: utf-8 -*-
"""
    Initialization of news module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import logging
import os

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
                 '/article//img[re:test(@src, "^http")]', '@src', '@alt')
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


class Config(object):
    DATABASE = os.getenv('DATABASE',
                         'mysql+pymysql://bb8:bb8test'
                         '@172.17.0.1:3307/bb8?charset=utf8mb4')
    ENABLE_CRAWLER = True


class DevelopmentConfig(Config):
    ENTRY_ENTITY = 'entries-dev'
    ENABLE_CRAWLER = True


class DeployConfig(Config):
    DATABASE = ('mysql+pymysql://contentdeploy:contentdeploymysql@/content?'
                'unix_socket=/cloudsql/dotted-lexicon-133523:asia-east1:bb8&'
                'charset=utf8mb4')
    ENTRY_ENTITY = 'entries'
    ENABLE_CRAWLER = True


def ConfigureLogger():
    logger_ = logging.getLogger('news')
    logger_.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger_.addHandler(ch)
    return logger_


logger = ConfigureLogger()

if os.getenv('BB8_DEPLOY', '') == 'true':
    logger.info('In deploy mode')
    config = DeployConfig()  # pylint: disable=R0204
else:
    logger.info('In development mode')
    config = DevelopmentConfig()  # pylint: disable=R0204

logger.info('Database URI: %s', config.DATABASE)
