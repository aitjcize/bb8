#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Content App gRPC Servicer
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import argparse

from content import service


def main(args):
    service.start_grpc_server(args.port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gRPC servicer')
    parser.add_argument('-p', '--port', dest='port', default=9999,
                        help='gRPC service port')
    main(parser.parse_args())
