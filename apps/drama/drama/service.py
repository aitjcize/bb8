# -*- coding: utf-8 -*-
"""
    DramaInfo Service
    ~~~~~~~~~~~~~~~~~~~
    Recommend the drama to the user, and allow
    the user to subscribe to a given drama

    Copyright 2016 bb8 Authors
"""


import logging
import time

import grpc
from concurrent import futures
from sqlalchemy import desc

import service_pb2  # pylint: disable=E0401

from drama import config
from drama.database import (DatabaseManager, DatabaseSession, Drama,
                            Episode, DramaCountryEnum, User)


_SECS_IN_A_DAY = 86400


def to_proto_drama(drama, user):
    return service_pb2.Drama(
        id=drama.id,
        link=drama.link,
        name=drama.name,
        description=drama.description,
        image_url=drama.image or config.DEFAULT_DRAMA_IMAGE,
        country=drama.country.value,
        subscribed=drama in user.subscribed_dramas
    )


def to_proto_episode(episode):
    return service_pb2.Episode(
        link=episode.link,
        drama_id=episode.drama.id,
        drama_name=episode.drama.name,
        image_url=episode.drama.image or config.DEFAULT_DRAMA_IMAGE,
        description=episode.drama.description,
        serial_number=episode.serial_number,
    )


class DramaInfo(object):
    @classmethod
    def Subscribe(cls, user_id, drama_id):
        with DatabaseSession():
            user = User.get_or_create(id=user_id)
            drama = Drama.get_by(id=drama_id, single=True)
            user.subscribed_dramas.append(drama)
            DatabaseManager.commit()

    @classmethod
    def Unsubscribe(cls, user_id, drama_id):
        with DatabaseSession():
            user = User.get_or_create(id=user_id)
            drama = Drama.get_by(id=drama_id, single=True)
            try:
                user.subscribed_dramas.remove(drama)
            except Exception:
                pass
            DatabaseManager.commit()

    @classmethod
    def Search(cls, user_id, term, count=10):
        with DatabaseSession():
            user = User.get_or_create(id=user_id)
            dramas = Drama.query().filter(
                Drama.name.like(unicode('%' + term + '%'))
            ).order_by(
                # pylint: disable=C0121
                Drama.order == None,  # noqa
                'order', desc('updated_at'),
            ).limit(count)
            return [to_proto_drama(drama, user) for drama in dramas]

    @classmethod
    def Trending(cls, user_id, country, count=10):
        with DatabaseSession():
            user = User.get_or_create(id=user_id)
            dramas = Drama.query().filter(
                Drama.country == DramaCountryEnum(country)
            ).order_by(
                # pylint: disable=C0121
                Drama.order == None,  # noqa
                'order', desc('updated_at'),
            ).limit(count)
            return [to_proto_drama(drama, user) for drama in dramas]

    @classmethod
    def GetHistory(cls, drama_id, from_episode, backward, count=5):
        with DatabaseSession():
            order_by = (desc('serial_number')
                        if backward else 'serial_number')
            episodes = (
                Episode.query().filter(
                    Episode.drama_id == drama_id,
                    Episode.serial_number < from_episode if backward
                    else Episode.serial_number >= from_episode,
                ).order_by(order_by).limit(count))
            return [to_proto_episode(episode) for episode in episodes]


class DramaInfoServicer(service_pb2.DramaInfoServicer):
    def __init__(self):
        super(DramaInfoServicer, self).__init__()

    def Search(self, request, unused_context):
        return service_pb2.Dramas(
            dramas=DramaInfo.Search(
                request.user_id, request.term, request.count))

    def Trending(self, request, unused_context):
        return service_pb2.Dramas(
            dramas=DramaInfo.Trending(
                request.user_id, request.country, request.count))

    def Subscribe(self, request, unused_context):
        DramaInfo.Subscribe(request.user_id, request.drama_id)
        return service_pb2.Empty()

    def Unsubscribe(self, request, unused_context):
        DramaInfo.Unsubscribe(request.user_id, request.drama_id)
        return service_pb2.Empty()

    def GetHistory(self, request, unused_context):
        return service_pb2.Episodes(
            episodes=DramaInfo.GetHistory(
                request.drama_id, request.from_episode, request.backward))


def start_grpc_server(port):
    """Start gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=config.N_THREADS))
    service_pb2.add_DramaInfoServicer_to_server(
        DramaInfoServicer(), server)
    server.add_insecure_port('[::]:%d' % port)
    server.start()
    logging.info('gRPC server started.')

    while True:
        time.sleep(_SECS_IN_A_DAY)
