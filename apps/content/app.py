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
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from sqlalchemy.exc import IntegrityError

import content_service
import service_pb2  # pylint: disable=E0401
from news import config, spider_configs, keywords
from news.database import Session, Initialize, Keyword
from news.spiders import RSSSpider, WebsiteSpider


SECS_IN_A_DAY = 86400


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


def grpc_server(port):
    server = service_pb2.beta_create_ContentInfo_server(
        content_service.ContentInfoServicer())
    server.add_insecure_port('[::]:%d' % port)
    server.start()

    while True:
        time.sleep(SECS_IN_A_DAY)


def main(args):
    Initialize()

    grpcp = multiprocessing.Process(target=grpc_server, args=(args.port,))
    grpcp.start()

    configure_logging({'LOG_LEVEL': 'WARNING', 'LOG_ENABLED': True})
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
