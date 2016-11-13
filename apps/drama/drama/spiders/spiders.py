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

from bb8_client.app_api import (CacheImage, EventPayload, Message,
                                MessagingService, TrackedURL)

from drama import config
from drama.database import Drama, Episode, DramaCountryEnum, DatabaseManager


# Global MessagingService API endpoint
message_service = MessagingService()


def build_new_episode_bubble(message, drama, episode):
    image_url = (CacheImage(drama.image) if drama.image else
                 config.DEFAULT_DRAMA_IMAGE)

    if episode.serial_number > 1000 and episode.serial_number < 20000:
        s_n = episode.serial_number / 1000
        e_n = episode.serial_number % 1000
        title = u'S%02dE%02d ' % (s_n, e_n) + drama.name
    else:
        title = drama.name + u' 第 %d 集' % episode.serial_number

    b = Message.Bubble(title,
                       image_url=image_url,
                       subtitle=drama.description,
                       item_url=episode.link)

    b.add_button(
        Message.Button(Message.ButtonType.WEB_URL,
                       u'帶我去看',
                       url=TrackedURL(episode.link, 'WatchButton/Push')))
    b.add_button(
        Message.Button(Message.ButtonType.POSTBACK,
                       u'我想看前幾集',
                       payload=EventPayload(
                           'GET_HISTORY',
                           {'drama_id': drama.id,
                            'from_episode': episode.serial_number,
                            'backward': True})))
    b.add_button(Message.Button(Message.ButtonType.ELEMENT_SHARE))
    message.add_bubble(b)


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
            name=extract_xpath(
                response, '//div[@class="item-page"]/h1/text()')[:64],
            description=extract_content(
                response, '(//div[@class="item-page"]//p)[1]')[:512],
            image=urlparse.urljoin(
                base,
                extract_xpath(response, '//div[@id="top"]//img/@src')),
            country=DramaCountryEnum(country)
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

            # Update Drama info
            Drama.get_by(name=meta['name'], return_query=True).update(meta)
            DatabaseManager.commit()

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
                # Not supported link
                return

        msg = Message()
        drama = variables['drama']
        bubble_count = 0

        for serial_number in serial_numbers:
            try:
                ep = Episode(link=unicode(link),
                             serial_number=serial_number).add()
                drama.episodes.append(ep)
                DatabaseManager.commit()

                build_new_episode_bubble(msg, drama, ep)
                bubble_count += 1
            except (InvalidRequestError, IntegrityError):
                DatabaseManager.rollback()

        user_ids = [u.id for u in drama.users]
        if bubble_count > 0 and user_ids:
            message_service.Push(
                user_ids,
                [Message(u'您訂閱的戲劇%s'
                         u'有新的一集囉！快來看！' % drama.name), msg])


class VmusDramaSpider(CrawlSpider):
    def parse_vmus_drama_meta(self, response):
        name = extract_xpath(
            response,
            '//div[@id="wrapper"]/div[@id="wrap"]'
            '/section[@id="content"]/article/h2/text()')

        for pattern in [r'\[.*?\]', u'線上看', u'限制級', u'連載中']:
            name = re.sub(pattern, '', name)

        return dict(
            name=name[:64],
            description=extract_content(
                response,
                '//div[@id="wrapper"]/div[@id="wrap"]'
                '/section[@id="content"]/article'
                '/div[@class="entry clearfix"]/p[1]')[:512],
            image='http:' + extract_xpath(
                response,
                '//div[@id="wrapper"]/div[@id="wrap"]/'
                'section[@id="content"]/article/img/@src'),
            country=DramaCountryEnum.UNITED_STATES
        )

    def parse_vmus_drama(self, response):
        base = response.request.__dict__['_url']

        meta = self.parse_vmus_drama_meta(response)
        try:
            drama = Drama(link=unicode(base), **meta).add()
            DatabaseManager.commit()
        except (IntegrityError, InvalidRequestError):
            DatabaseManager.rollback()
            drama = Drama.get_by(name=meta['name'], single=True)
            if not drama:
                raise RuntimeError(u'Should not be here! name=' + meta['name'])

            # Update Drama info
            Drama.get_by(name=meta['name'], return_query=True).update(meta)
            DatabaseManager.commit()

        hrefs = response.xpath('//div[@id="wrapper"]/div[@id="wrap"]'
                               '/section[@id="content"]/article'
                               '/div[@class="entry clearfix"]/'
                               '/@href').extract()
        for link in hrefs:
            yield scrapy.Request(
                urlparse.urljoin(base, link),
                partial(self.parse_episode, dict(drama=drama)))

    def parse_episode(self, variables, response):
        link = response.request.__dict__['_url']

        try:
            title = response.xpath('//h2/text()').extract()[0]
        except Exception:
            return

        m = re.search(r'[sS](\d+)[eE](\d+)', title)
        if m:
            serial_number = 1000 * int(m.groups()[0]) + int(m.groups()[1])
        else:  # not valid episode URL
            return

        msg = Message()
        drama = variables['drama']

        try:
            ep = Episode(link=unicode(link),
                         serial_number=serial_number).add()
            drama.episodes.append(ep)
            DatabaseManager.commit()

            build_new_episode_bubble(msg, drama, ep)
        except (InvalidRequestError, IntegrityError):
            DatabaseManager.rollback()
            return

        user_ids = [u.id for u in drama.users]
        if user_ids:
            patterns = [ur'[簡中英繁/]+字幕', '(?:HD/)?HR-HDTV', '720P',
                        '1080P', '720P/1080P', 'HD']
            drama_name = drama.name
            for pattern in patterns:
                drama_name = re.sub(pattern, '', drama_name)
            message_service.Push(
                user_ids,
                [Message(u'您訂閱的戲劇%s'
                         u'有新的一集囉！快來看！' % drama_name), msg])
