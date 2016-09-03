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
from drama.database import (DatabaseSession, Drama,
                            DramaCountryEnum, User)

from drama import config

_SECS_IN_A_DAY = 86400


def to_proto_drama(drama):
    return service_pb2.Drama(
        id=drama.id,
        link=drama.link,
        name=drama.name,
        description=drama.name,
        image_url=drama.image,
        country=drama.country.value,
    )


def to_proto_episode(episode):
    return service_pb2.Episode(
        link=episode.link,
        drama_id=episode.drama.id,
        drama_name=episode.drama.name,
        serial_number=episode.serial_number,
    )


class DramaInfo(object):
    @classmethod
    def Subscribe(cls, user_id, drama_id):
        with DatabaseSession():
            user = User.get_or_create(id=user_id)
            drama = Drama.get_by(id=drama_id, single=True)
            user.subscribed_dramas.append(drama)
            User.commit()

    @classmethod
    def Search(cls, unused_user_id, term, count=10):
        with DatabaseSession():
            dramas = Drama.query().filter(
                Drama.name.like(unicode('%' + term + '%'))).limit(count)
            return [to_proto_drama(drama) for drama in dramas]

    @classmethod
    def Trending(cls, unused_user_id, country, count=5):
        with DatabaseSession():
            dramas = Drama.get_by(
                country=DramaCountryEnum(country),
                order_by=[desc('order'), desc('created_at')],
                limit=count)
            return [to_proto_drama(drama) for drama in dramas]


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
