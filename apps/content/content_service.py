# -*- coding: utf-8 -*-
"""
    ContentInfo Service
    ~~~~~~~~~~~~~~~~~~~

    Recommend the content according to trending or personal
    recommendation, and provide the search and read now functionality

    Copyright 2016 bb8 Authors
"""

import hashlib
import re

from backports.functools_lru_cache import lru_cache
from gcloud import datastore
from sqlalchemy import desc

import service_pb2  # pylint: disable=E0401
from news import config
from news.database import Entry, GetSession


gclient = datastore.Client()


def to_proto_entry(obj):
    return service_pb2.Entry(
        title=obj.title,
        description='',
        link=obj.link,
        source=obj.source,
        image_url=obj.image_url)


def normalize_source(query):
    mapping = {
        'yahoo': 'yahoo_rss',
        '雅虎': 'yahoo_rss',
        'storm': 'storm',
        '風傳媒': 'storm',
    }
    return mapping.get(query, None)


class ContentInfo(object):
    @classmethod
    def Search(cls, term, unused_user_id, count):
        session = GetSession()
        entries = session.query(Entry).filter(
            Entry.title.like(unicode('%' + term + '%'))).limit(count)
        return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    def Recommend(cls, unused_user_id, count):
        session = GetSession()
        entries = session.query(Entry).order_by(
            desc('created_at')).limit(count)
        return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    def Trending(cls, unused_user_id, source_name=None, count=5):
        session = GetSession()
        source_name = normalize_source(source_name)
        if source_name is None:
            entries = session.query(Entry).order_by(
                desc('created_at')).limit(count)
        else:
            entries = session.query(Entry).filter(
                Entry.source == source_name,
            ).order_by(desc('created_at')).limit(count)
        return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    @lru_cache(maxsize=512)
    def GetEntry(cls, entry_link):
        link_hash = hashlib.sha1(entry_link).hexdigest()
        entry_key = gclient.key(config.ENTRY_ENTITY, link_hash)
        return gclient.get(entry_key)

    @classmethod
    def GetContent(cls, entry_link, char_offset, limit):
        entry = cls.GetEntry(entry_link)

        content = entry['content'][char_offset:char_offset+limit]
        if len(content) < limit:
            return content, -1

        try:
            breakpoints = [_ for _ in re.finditer(ur'[。？！\n][^」]', content)]
            index = breakpoints[-1].start(0) + 1
        except Exception:
            # Cannot find suitable break point
            index = len(content) - 1
        return content[:index], char_offset+index


class ContentInfoServicer(service_pb2.BetaContentInfoServicer):
    def __init__(self):
        super(ContentInfoServicer, self).__init__()

    def PersonalRecommend(self, request, unused_context):
        return service_pb2.EntriesList(
            entries=ContentInfo.Recommend(
                request.user_id, request.count))

    def Trending(self, request, unused_context):
        return service_pb2.EntriesList(
            entries=ContentInfo.Trending(
                request.user_id, request.source_name, request.count))

    def Search(self, request, unused_context):
        return service_pb2.EntriesList(
            entries=ContentInfo.Search(
                request.query, request.user_id, request.count))

    def GetContent(self, request, unused_context):
        content, char_offset = ContentInfo.GetContent(
            request.entry_link, request.char_offset, request.limit)
        return service_pb2.EntryContent(
            content=content, char_offset=char_offset)
