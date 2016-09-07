# -*- coding: utf-8 -*-
"""
    ContentInfo Service
    ~~~~~~~~~~~~~~~~~~~

    Recommend the content according to trending or personal
    recommendation, and provide the search and read now functionality

    Copyright 2016 bb8 Authors
"""

import hashlib
import json
import logging
import re
import time

import grpc

from backports.functools_lru_cache import lru_cache
from concurrent import futures
from gcloud import datastore
from sqlalchemy import desc

import service_pb2  # pylint: disable=E0401
from content import config
from content.database import DatabaseSession, Entry, Keyword


_SECS_IN_A_DAY = 86400

gclient = datastore.Client()


def to_proto_entry(obj):
    return service_pb2.Entry(
        title=obj.title,
        description='',
        link=obj.link,
        source=obj.source,
        image_url=obj.image_url)


def to_proto_keyword(obj):
    return service_pb2.Keyword(name=obj.name)


def normalize_source(query):
    if isinstance(query, str):
        query = unicode(query)
    mapping = {
        u'yahoo': u'yahoo_rss',
        u'雅虎': u'yahoo_rss',
        u'storm': u'storm',
        u'風傳媒': u'storm',
        u'newslens': u'thenewslens',
        u'關鍵評論': u'thenewslens',
    }
    return mapping.get(query, None)


class ContentInfo(object):
    @classmethod
    def Search(cls, unused_user_id, term, count):
        with DatabaseSession():
            entries = Entry.search(term, count)
            return [to_proto_entry(ent) for ent in entries]

    @classmethod
    def Recommend(cls, unused_user_id, count):
        with DatabaseSession():
            entries = Entry.get_by(order_by=[desc('created_at')], limit=count)
            return [to_proto_entry(ent) for ent in entries]

    @classmethod
    def Trending(cls, unused_user_id, source_name=None, count=5):
        with DatabaseSession():
            source_name = normalize_source(source_name)
            if not source_name:
                entries = Entry.get_by(
                    order_by=[desc('created_at')],
                    limit=count)
            else:
                entries = Entry.get_by(
                    source=source_name,
                    order_by=[desc('created_at')],
                    limit=count)
            return [to_proto_entry(ent) for ent in entries]

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

    @classmethod
    def GetKeywords(cls, limit=5):
        with DatabaseSession():
            kws = Keyword.get_by(order_by=[desc('created_at')], limit=limit)
            return [to_proto_keyword(kw) for kw in kws]

    @classmethod
    def GetRelatedKeywords(cls, name, limit=5):
        with DatabaseSession():
            kw = Keyword.get_by(name=name, single=True)
            if kw:
                kws = Keyword.get_by(parent_id=kw.id,
                                     order_by=['created_at'], limit=limit)
                return [to_proto_keyword(kw) for kw in kws]
            return []


class ContentInfoServicer(service_pb2.ContentInfoServicer):
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

    def GetKeywords(self, request, unused_context):
        return service_pb2.KeywordsContent(
            keywords=ContentInfo.GetKeywords(request.limit))

    def GetRelatedKeywords(self, request, unused_context):
        return service_pb2.KeywordsContent(
            keywords=ContentInfo.GetRelatedKeywords(request.name,
                                                    request.limit))


def start_grpc_server(port):
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=config.N_THREADS))
    service_pb2.add_ContentInfoServicer_to_server(
        ContentInfoServicer(), server)
    server.add_insecure_port('[::]:%d' % port)
    server.start()
    logging.info('gRPC server started.')

    while True:
        time.sleep(_SECS_IN_A_DAY)
