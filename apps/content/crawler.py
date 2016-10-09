#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Scrapy Spider Process
    ~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import argparse
import logging
import multiprocessing
import os
import time

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from content import config, keywords
from content.database import DatabaseSession, Initialize, Keyword
from content.spiders.config import spider_configs
from content.spiders import RSSSpider, WebsiteSpider


logger = logging.getLogger('content.crawler')
logger.setLevel(logging.DEBUG)


def crawl():
    try:
        logger.info('Crawler: started')
        process = CrawlerProcess(get_project_settings())
        process.crawl(WebsiteSpider, **spider_configs['storm'])
        process.crawl(WebsiteSpider, **spider_configs['thenewslens'])
        process.crawl(RSSSpider, **spider_configs['yahoo_rss'])
        process.start()
        process.stop()

        logger.info('Crawler: extracting keywords')
        with DatabaseSession():
            kws = keywords.extract_keywords_ct()
            for kw, related in kws.iteritems():
                k = Keyword(name=kw).commit_unique()
                if k:
                    for r in related:
                        Keyword(parent_id=k.id, name=r).commit_unique()
    except Exception:
        logger.exception('Crawler: exception, skipped')
    else:
        logger.info('Crawler: finished gracefully')


def main(args):
    # cd to script dir
    script_dir = os.path.dirname(__file__)
    if script_dir:
        os.chdir(script_dir)

    Initialize()

    while True:
        if config.ENABLE_CRAWLER:
            p = multiprocessing.Process(target=crawl)
            p.start()
            p.join()

        time.sleep(args.interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('--interval', type=int, dest='interval', default=1800,
                        help='The interval in seoncds between crawler run')
    main(parser.parse_args())
