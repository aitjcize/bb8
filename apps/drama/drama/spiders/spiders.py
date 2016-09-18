# -*- coding: utf-8 -*-
"""
    Spiders
    ~~~~~~~

    Copyright 2016 bb8 Authors
"""

import re
import traceback
import urlparse
from functools import partial

import scrapy
from scrapy.exceptions import DropItem
from scrapy.spiders import CrawlSpider
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from bb8_client.app_api import MessagingService

from drama.database import Drama, Episode, DramaCountryEnum, DatabaseManager

message_service = MessagingService()


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


class DramaSpider(CrawlSpider):
    def parse_drama_meta(self, response):
        referer = response.request.headers.get('Referer', None)

        try:
            country = re.match(r'.*\/([a-zA-Z]{2})\/?$', referer).group(1)
        except Exception:
            country = 'kr'

        base = response.request.__dict__['_url']
        return dict(
            name=extract_xpath(response,
                               '//div[@class="item-page"]/h1/text()'),
            description=extract_content(response,
                                        '(//div[@class="item-page"]//p)[1]'),
            image=urlparse.urljoin(
                base,
                extract_xpath(response, '//div[@id="top"]//img/@src')),
            country=DramaCountryEnum(country),
            order=None,
        )

    def parse_drama(self, response):
        base = response.request.__dict__['_url']

        meta = self.parse_drama_meta(response)
        try:
            drama = Drama(link=unicode(base), **meta).add()
            DatabaseManager.commit()
        except (IntegrityError, InvalidRequestError):
            DatabaseManager.rollback()
            drama = Drama.get_by(name=meta['name'], single=True)
            if not drama:
                raise RuntimeError(u'Should not be here! name=' + meta['name'])

        hrefs = response.xpath('//div[@id="main"]//li/a/@href').extract()
        for idx, link in enumerate(hrefs):
            yield scrapy.Request(
                urlparse.urljoin(base, link),
                partial(self.parse_episode,
                        dict(serial_number=idx, drama=drama)))

    def parse_episode(self, variables, response):
        link = response.request.__dict__['_url']

        try:
            serial_numbers = [
                int(re.match(r'.*\/[a-zA-Z]*(\d*)\.php$', link).group(1))]
        except Exception:
            try:
                nums = re.match(
                    r'.*\/[a-zA-Z]*(\d+-\d+)\.php', link).group(1).split('-')
                assert len(nums) == 2
                serial_numbers = range(*map(int, nums))
            except Exception:
                print 'Not supported link %s' % link
                return

        drama = variables['drama']
        for serial_number in serial_numbers:
            try:
                ep = Episode(link=unicode(link),
                             serial_number=serial_number).add()
                drama.episodes.append(ep)
                DatabaseManager.commit()
            except (InvalidRequestError, IntegrityError):
                DatabaseManager.rollback()

        try:
            DatabaseManager.commit()
        except (InvalidRequestError, IntegrityError):
            DatabaseManager.rollback()
