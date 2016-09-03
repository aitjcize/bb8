#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Database ORM definition unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import datetime
import unittest

from news.database import Reset, GetSession, Entry, Tag, Keyword


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
        self.assertEquals(entry2.tags[0].name, u'product')

        keyword1 = Keyword(name=u'kw1').add()
        keyword2 = Keyword(name=u'kw2').add()
        keyword3 = Keyword(name=u'kw3').add()

        keyword1.related_keywords.append(keyword2)
        keyword1.related_keywords.append(keyword3)
        self.dbm.commit()

        keyword = Keyword.get_by(name=u'kw1', single=True)
        self.assertEquals(keyword.name, u'kw1')
        self.assertEquals(len(keyword.related_keywords), 2)
        self.assertEquals(
            keyword.related_keywords[0].name, u'kw2')
        self.assertEquals(
            keyword.related_keywords[1].name, u'kw3')


if __name__ == '__main__':
    unittest.main()
