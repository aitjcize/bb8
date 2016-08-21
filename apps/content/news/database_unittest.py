#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Database ORM definition unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import unittest

from news.database import Reset, GetSession, Entry, Tag


class SchemaUnittest(unittest.TestCase):
    def setUp(self):
        self.dbm = GetSession()

    def test_schema(self):
        """Test database schema and make sure all the tables can be created
        without problems."""
        Reset()
        self.dbm.commit()

    def test_schema_sanity(self):
        """Populate data into all tables and make sure there are no error."""
        Reset()

        entry = Entry(title=u'mock-title',
                      link=u'mock-link',
                      publish_time=datetime.datetime.utcnow(),
                      source=u'mock-source',
                      original_source=u'mock-original-source',
                      image_url=u'mock-image-src',
                      author=u'mock-author').add()

        self.dbm.commit()

        tag1 = Tag(name=u'product').add()
        tag2 = Tag(name=u'article').add()

        entry.tags.append(tag1)
        entry.tags.append(tag2)

        self.dbm.commit()

        entry2 = Entry.get_by(link=u'mock-link', single=True)
        self.assertNotEquals(entry2, None)
        self.assertEquals(entry2.image_url, u'mock-image-src')
        self.assertEquals(len(entry2.tags), 2)
        self.assertEquals(entry2.tags[0].name, 'product')


if __name__ == '__main__':
    unittest.main()
