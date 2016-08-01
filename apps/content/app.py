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

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import content_service
import service_pb2  # pylint: disable=E0401
from news.config import spider_configs
from news.spiders import RSSSpider, WebsiteSpider


def main(args):
    # Setup logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(message)s', '%Y/%m/%d %H:%M:%S')
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # Start gRPC
    server = service_pb2.beta_create_ContentInfo_server(
        content_service.ContentInfoServicer())
    server.add_insecure_port('[::]:%d' % args.port)
    server.start()

    while True:
        try:
            process = CrawlerProcess(get_project_settings())
            process.crawl(WebsiteSpider, **spider_configs['storm'])
            process.crawl(RSSSpider, **spider_configs['yahoo_rss'])
            process.start()
        except Exception:
            logging.exception('Crawler exception, skipping')
            continue
        time.sleep(args.interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('-p', '--port', dest='port', default=9999,
                        help='gRPC service port')
    parser.add_argument('--interval',
                        type=int,
                        dest='interval',
                        default=3600,
                        help='The interval to fetch youbike data (second)')
    main(parser.parse_args())
