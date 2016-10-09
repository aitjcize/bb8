#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Database ORM definition unittest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import unittest

from drama.database import DatabaseManager, Drama, DramaCountryEnum, Episode


class SchemaUnittest(unittest.TestCase):
    def setUp(self):
        DatabaseManager.connect()

    def tearDown(self):
        DatabaseManager.disconnect()

    def test_schema(self):
        """Test database schema and make sure all the tables can be created
        without problems."""
        DatabaseManager.reset()
        DatabaseManager.commit()

    def test_schema_sanity(self):
        """Populate data into all tables and make sure there are no error."""
        DatabaseManager.reset()

        drama = Drama(link=u'mock-link',
                      name=u'mock-name',
                      description=u'mock-desc',
                      image=u'mock-image',
                      country=DramaCountryEnum.TAIWAN,
                      order=1).add()

        DatabaseManager.commit()

        drama1 = Drama.get_by(name=u'mock-name', single=True)
        self.assertNotEquals(drama1, None)
        self.assertEquals(drama1.link, 'mock-link')

        episode = Episode(link=u'mock-link-2',
                          drama_id=drama.id,
                          serial_number=10).add()

        drama.episodes.append(episode)
        DatabaseManager.commit()

        episode1 = Episode.get_by(link=u'mock-link-2', single=True)
        self.assertNotEquals(episode1, None)

        self.assertEquals(episode1.drama.id, drama1.id)

        drama2 = Drama.get_by(name=u'mock-name', single=True)
        self.assertEquals(len(drama2.episodes), 1)
        self.assertEquals(drama2.episodes[0].link_hash, episode.link_hash)


if __name__ == '__main__':
    unittest.main()
