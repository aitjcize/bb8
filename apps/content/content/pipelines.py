# -*- coding: utf-8 -*-
"""
    Scrapy pipelines
    ~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import json
import time
import traceback
from datetime import datetime

import enum
import pytz
from gcloud import datastore
from scrapy.exceptions import DropItem
from sqlalchemy.exc import IntegrityError

from content import config
from content.database import DatabaseManager, DatabaseSession, Entry


gclient = datastore.Client()


class SQLPipeline(object):
    def process_item(self, item, unused_spider):
        item_dict = {k: v for k, v in dict(item).iteritems()
                     if k in Entry.columns()}

        item_dict['image_url'] = unicode(
            item['images'][0]['src'] if len(item['images']) > 0 else u'')
        with DatabaseSession():
            try:
                entry = Entry(**item_dict).add()
                entry.commit()

                item['link_hash'] = entry.link_hash
            except IntegrityError:
                DatabaseManager.rollback()
                raise DropItem('Duplicate entry ignored')
            except Exception:
                DatabaseManager.rollback()
                raise DropItem('Invalid database operation: %s' %
                               traceback.format_exc())
        return item


class DatastorePipeline(object):
    def process_item(self, item, unused_spider):
        def unix_timestamp(dt):
            _EPOCH = datetime(1970, 1, 1, tzinfo=pytz.utc)
            if dt.tzinfo is None:
                return int(time.mktime((dt.year, dt.month, dt.day,
                                        dt.hour, dt.minute, dt.second,
                                        -1, -1, -1)) + dt.microsecond / 1e6)
            return int((dt - _EPOCH).total_seconds())

        def to_json(item):
            rv = dict(item)
            for key in rv:
                # Google DataStore cannot display str well
                if isinstance(rv[key], str):
                    rv[key] = unicode(rv[key])
                elif (isinstance(rv[key], list) or
                      isinstance(rv[key], dict)):
                    rv[key] = unicode(json.dumps(rv[key]))
                elif isinstance(rv[key], datetime):
                    rv[key] = unix_timestamp(rv[key])
                elif isinstance(rv[key], enum.Enum):
                    rv[key] = rv[key].value
            return rv

        data = to_json(item)

        key = gclient.key(config.ENTRY_ENTITY, item['link_hash'])
        entity = datastore.Entity(
            key=key, exclude_from_indexes=['content', 'images'])
        for k, v in data.iteritems():
            entity[k] = v
        gclient.put(entity)
        return item
