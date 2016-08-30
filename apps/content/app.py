#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Scrapy spiders and grpc entry point
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import argparse
import logging
import time
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

import content_service
import service_pb2  # pylint: disable=E0401
from news import config, spider_configs
from news.database import Initialize
from news.spiders import RSSSpider, WebsiteSpider


def crawl():
    try:
        process = CrawlerProcess(get_project_settings())
        process.crawl(WebsiteSpider, **spider_configs['storm'])
        process.crawl(WebsiteSpider, **spider_configs['thenewslens'])
        process.crawl(RSSSpider, **spider_configs['yahoo_rss'])
        process.start()
        process.stop()
    except Exception:
        logging.exception('Crawler exception, skipping')


def main(args):
    Initialize()

    # Start gRPC
    server = service_pb2.beta_create_ContentInfo_server(
        content_service.ContentInfoServicer())
    server.add_insecure_port('[::]:%d' % args.port)
    server.start()

    configure_logging({'LOG_LEVEL': 'WARNING', 'LOG_ENABLED': True})

    while True:
        if config.ENABLE_CRAWLER:
            p = Process(target=crawl)
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