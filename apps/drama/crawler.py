#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Scrapy spiders Entry Point
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import argparse
import logging
import time
import multiprocessing

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from drama import keywords
from drama.database import DatabaseManager, Initialize, Drama
from drama.spiders import DramaSpider
from drama.spiders.config import spider_configs


logger = logging.getLogger('drama.crawler')
logger.setLevel(logging.DEBUG)


def crawl():
    try:
        logger.info('Crawler: started')
        process = CrawlerProcess(get_project_settings())
        process.crawl(DramaSpider, **spider_configs['dramaq'])
        process.start()
        process.stop()

        logger.info('Crawler: extracting popular dramas')
        populars = keywords.extract_popular_dramas()
        for links in populars.values():
            for order, link in enumerate(links):
                drama = Drama.get_by(link=link, single=True)
                if drama:
                    drama.order = order
        DatabaseManager.commit()

    except Exception:
        logging.exception('Crawler: exception, skipped')
    else:
        logger.info('Crawler: finished gracefully')


def main(args):
    Initialize()

    while True:
        p = multiprocessing.Process(target=crawl)
        p.start()
        p.join()

        time.sleep(args.interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('--interval', type=int, dest='interval', default=1800,
                        help='The interval in seoncds between crawler run')
    main(parser.parse_args())
