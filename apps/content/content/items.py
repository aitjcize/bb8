# -*- coding: utf-8 -*-
"""
    Scrapy items
    ~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import scrapy


class EntryItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    link_hash = scrapy.Field()
    publish_time = scrapy.Field()
    source = scrapy.Field()
    original_source = scrapy.Field()
    images = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()
    created_at = scrapy.Field()
