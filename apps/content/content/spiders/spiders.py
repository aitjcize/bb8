# -*- coding: utf-8 -*-
"""
    Spiders
    ~~~~~~~

    Copyright 2016 bb8 Authors
"""

import traceback
import itertools
from datetime import datetime
from functools import partial

from dateutil import parser

import scrapy
from scrapy.exceptions import DropItem
from scrapy.spiders import CrawlSpider, XMLFeedSpider

from content.items import EntryItem


def extract_xpath(response, xpath, default_val=''):
    try:
        return (response.xpath(xpath).extract()[0]
                if xpath else default_val)
    except IndexError:
        raise DropItem('Invalid response: %s' % traceback.format_exc())


def extract_content(response, xpath):
    content = []
    nodes = response.xpath(xpath)
    for node in nodes:
        value = ''.join(
            node.xpath('.//text()[not(parent::script)]').extract()).strip()
        if value != '':
            content.append(value)
    return '\n'.join(content)


def extract_imgs(response, rules):
    def __extract_xpath(response, rule):
        xpath, src_path, alt_path = rule
        imgs = response.xpath(xpath)
        if not len(imgs):
            return []
        srcs = imgs.xpath(src_path).extract()
        alts = imgs.xpath(alt_path).extract() if alt_path else [''] * len(imgs)
        return [dict(src=s, alt=a) for s, a in zip(srcs, alts)]

    if isinstance(rules, tuple):
        return __extract_xpath(response, rules)
    elif isinstance(rules, list):
        return list(itertools.chain.from_iterable(
            [__extract_xpath(response, rule) for rule in rules]))
    raise RuntimeError('Not supported xpaths type')


class RSSSpider(XMLFeedSpider):
    def parse_page(self, variables, response):
        title = extract_xpath(response, self.extractor['title'])
        author = extract_xpath(response, self.extractor['author'])

        content = extract_content(response, self.extractor['content'])
        imgs = extract_imgs(response, self.extractor['images'])

        item = EntryItem()
        item['author'] = unicode(author)
        item['images'] = imgs
        item['source'] = unicode(self.name)
        item['original_source'] = unicode(variables['original_source'])
        item['title'] = unicode(title)
        item['link'] = unicode(response.url)
        item['content'] = unicode(content)
        item['publish_time'] = variables['publish_time']
        item['created_at'] = datetime.now()
        return item

    def parse_node(self, response, node):
        try:
            link = node.xpath('link/text()').extract()[0]
            pub_date = node.xpath('pubDate/text()').extract()[0]
            original_source = node.xpath('source/text()').extract()[0]
            publish_time = parser.parse(pub_date)
            yield scrapy.Request(
                link,
                partial(self.parse_page,
                        dict(publish_time=publish_time,
                             original_source=original_source)))
        except IndexError:
            pass


class WebsiteSpider(CrawlSpider):
    def parse_item(self, response):
        title = extract_xpath(response, self.extractor['title'])
        author = extract_xpath(response, self.extractor['author'])

        content = extract_content(response, self.extractor['content'])
        imgs = extract_imgs(response, self.extractor['images'])

        original_source = (
            response.xpath(
                self.extractor['original_source']
            ).extract()[0]
            if self.extractor['original_source'] else '')

        item = EntryItem()
        item['author'] = unicode(author)
        item['images'] = imgs
        item['source'] = unicode(self.name)
        item['original_source'] = unicode(original_source)
        item['title'] = unicode(title)
        item['link'] = unicode(response.url)
        item['content'] = unicode(content)
        item['publish_time'] = datetime.now()
        item['created_at'] = datetime.now()
        return item
