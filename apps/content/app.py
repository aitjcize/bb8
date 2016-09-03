#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Scrapy spiders and grpc entry point
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from __future__ import print_function

import argparse
import logging
import time
import multiprocessing

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sqlalchemy.exc import IntegrityError

from content import config, spider_configs, keywords, service
from content.database import Session, Initialize, Keyword
from content.spiders import RSSSpider, WebsiteSpider


def crawl():
    try:
        print('Crawler: started')
        process = CrawlerProcess(get_project_settings())
        process.crawl(WebsiteSpider, **spider_configs['storm'])
        process.crawl(WebsiteSpider, **spider_configs['thenewslens'])
        process.crawl(RSSSpider, **spider_configs['yahoo_rss'])
        process.start()
        process.stop()

        print('Crawler: extracting keywords')
        kws = keywords.extract_keywords_ct()
        for kw, related in kws.iteritems():
            try:
                k = Keyword(name=kw).add()
                Session().commit()
            except IntegrityError:
                Session().rollback()

            for r in related:
                try:
                    related_kw = Keyword(name=r).add()
                    k.related_keywords.append(related_kw)
                    Session().commit()
                except IntegrityError:
                    Session().rollback()
    except Exception:
        logging.exception('Crawler: exception, skipped')
    else:
        print('Crawler: finished gracefully')


def main(args):
    Initialize()

    service.start_grpc_server(args.port)

    while True:
        if config.ENABLE_CRAWLER:
            p = multiprocessing.Process(target=crawl)
            p.start()
            p.join()

        time.sleep(args.interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('-p', '--port', dest='port', default=9999,
                        help='gRPC service port')
    parser.add_argument('--interval', type=int, dest='interval', default=1800,
                        help='The interval in seoncds between crawler run')
    main(parser.parse_args())
