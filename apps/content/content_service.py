# -*- coding: utf-8 -*-
"""
    ContentInfo Service
    ~~~~~~~~~~~~~~~~~~~

    Recommend the content according to trending or personal
    recommendation, and provide the search and read now functionality

    Copyright 2016 bb8 Authors
"""

import re

from gcloud import datastore
from sqlalchemy import desc

from news.database import Entry
import service_pb2  # pylint: disable=E0401

gclient = datastore.Client()


def to_proto_entry(obj):
    return service_pb2.Entry(
        id=obj.id,
        title=obj.title,
        description='',
        link=obj.link,
        source=obj.source,
        image_url=obj.image_url)


class ContentInfo(object):
    @classmethod
    def Search(cls, query, count):
        entries = Entry.search(query, count)
        return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    def Recommend(cls, unused_user_id, count):
        entries = Entry.query().order_by(desc('created_at')).limit(count)
        return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    def Trending(cls, count):
        entries = Entry.query().order_by(desc('created_at')).limit(count)
        return [to_proto_entry(ent) for ent in entries.all()]

    @classmethod
    def GetContent(cls, entry_id, char_offset, limit):
        entry_key = gclient.key('entries', entry_id)
        entry = gclient.get(entry_key)

        content = entry['content'][char_offset:char_offset+limit]
        if len(content) < limit:
            return content
        index = len(content) - re.search(r'[^a-zA-Z]', content[::-1]).start(0)
        return content[:index], char_offset+index


class ContentInfoServicer(service_pb2.BetaContentInfoServicer):
    def __init__(self):
        super(ContentInfoServicer, self).__init__()

    def PersonalRecommend(self, request, unused_context):
        return service_pb2.EntriesList(
            entries=ContentInfo.Recommend(
                request.user_id, request.count
            ),
        )

    def Trending(self, request, unused_context):
        return service_pb2.EntriesList(
            entries=ContentInfo.Trending(request.count),
        )

    def Search(self, request, unused_context):
        return service_pb2.EntriesList(
            entries=ContentInfo.Search(request.query, request.count),
        )

    def GetContent(self, request, unused_context):
        content, char_offset = ContentInfo.GetContent(
            request.entry_id, request.char_offset, request.limit)
        return service_pb2.EntryContent(
            content=content, char_offset=char_offset
        )
