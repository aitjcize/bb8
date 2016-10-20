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
        print 'src:1:', srcs
        if not srcs:
            print 'extracting empty src1!!!'
            print 'imgs::', imgs
            print 'imgs.extract::', imgs.extract()
            print 'imgs.extract type::', type(imgs.extract())
            #srcs = imgs.re(r'url\(\'(.*)\'\)')
            srcs = response.xpath(xpath).re(r'url\(\'(.*)\'\)')
        if not alts:
            alts = ['' for tmp in srcs]
        print 'src:2:', srcs
        print 'alts::', alts
        return [dict(src=s, alt=a) for s, a in zip(srcs, alts)]

    if isinstance(rules, tuple):
        return __extract_xpath(response, rules)
    elif isinstance(rules, list):
        return list(itertools.chain.from_iterable(
            [__extract_xpath(response, rule) for rule in rules]))
    raise RuntimeError('Not supported xpaths type')


class RSSSpider(XMLFeedSpider):
    def get_extractor(self, name):
        print 'RSSSpider::get_extractor()'
        return self.extractor[name]  # pylint: disable=E1101

    def parse_page(self, variables, response):
        print 'RSSSpider start----------------------------'
        print 'RSSSpider::parse_page()'
        title = extract_xpath(response, self.get_extractor('title'))
        author = extract_xpath(response, self.get_extractor('author'))

        content = extract_content(response, self.get_extractor('content'))
        imgs = extract_imgs(response, self.get_extractor('images'))
        #print 'RSS::title::', unicode(title)
        print 'RSS::imgs::', imgs
        print 'RSS::source::', unicode(self.name)
        #print 'RSS::original_source::', unicode(variables['original_source'])
        print 'RSS::link::', unicode(response.url)

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
        print 'RSSSpider end----------------------------'
        return item

    def parse_node(self, response, node):
        try:
            print 'parse_node::start'
            link = node.xpath('link/text()').extract()[0]
            print 'parse_node::link::', link
            pub_date = node.xpath('pubDate/text()').extract()[0]
            print 'parse_node::pub_date::', pub_date
            original_source = node.xpath('source/text()').extract()[0]
            #print 'parse_node::original_source::', original_source
            publish_time = parser.parse(pub_date)
            print 'parse_node::publish_time::', publish_time
            yield scrapy.Request(
                link,
                partial(self.parse_page,
                        dict(publish_time=publish_time,
                             original_source=original_source)))
        except IndexError:
            print 'parse_node::fail!!!'
            pass


class WebsiteSpider(CrawlSpider):
    def get_extractor(self, name):
        print 'WebsiteSpider::get_extractor()'
        return self.extractor[name]  # pylint: disable=E1101

    def parse_item(self, response):
        print 'WebsiteSpider::parse_item()'
        title = extract_xpath(response, self.get_extractor('title'))
        author = extract_xpath(response, self.get_extractor('author'))

        content = extract_content(response, self.get_extractor('content'))
        imgs = extract_imgs(response, self.get_extractor('images'))

        original_source = (
            response.xpath(
                self.get_extractor('original_source')
            ).extract()[0]
            if self.get_extractor('original_source') else '')

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
