# -*- coding: utf-8 -*-
"""
    ContentInfo Service
    ~~~~~~~~~~~~~~~~~~~

    Recommend the content according to trending or personal
    recommendation, and provide the search and read now functionality

    Copyright 2016 bb8 Authors
"""

import contextlib
import hashlib
import json
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
    def Search(cls, unused_user_id, term, count):
        with contextlib.closing(GetSession()) as session:
            entries = session.query(Entry).filter(
                Entry.title.like(unicode('%' + term + '%'))).limit(count)
            return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    def Recommend(cls, unused_user_id, count):
        with contextlib.closing(GetSession()) as session:
            entries = session.query(Entry).order_by(
                desc('created_at')).limit(count)
            return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    def Trending(cls, unused_user_id, source_name=None, count=5):
        with contextlib.closing(GetSession()) as session:
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
        total_length = len(entry['content'])

        content = entry['content'][char_offset:char_offset+limit]
        if len(content) < limit:
            return content, -1, total_length

        try:
            breakpoints = list(re.finditer(ur'[。？！\n][^」]', content))
            index = breakpoints[-1].start(0) + 1
        except Exception:
            # Cannot find suitable break point
            index = len(content) - 1
        return content[:index], char_offset+index, total_length

    @classmethod
    def GetPicture(cls, entry_link, pic_index):
        if pic_index == -1:
            return '', '', -1

        entry = cls.GetEntry(entry_link)

        pictures = json.loads(entry['images'])
        if pic_index >= len(pictures):
            return '', '', -1

        return (pictures[pic_index]['src'],
                pictures[pic_index]['alt'],
                pic_index+1 if pic_index+1 < len(pictures) else -1)


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
                request.user_id, request.query, request.count))

    def GetContent(self, request, unused_context):
        content, char_offset, total_length = ContentInfo.GetContent(
            request.entry_link, request.char_offset, request.limit)
        return service_pb2.EntryContent(
            content=content, char_offset=char_offset,
            total_length=total_length)

    def GetPicture(self, request, unused_context):
        src, alt, pic_index = ContentInfo.GetPicture(
            request.entry_link, request.pic_index)
        return service_pb2.PictureContent(
            src=src, alt=alt, pic_index=pic_index)