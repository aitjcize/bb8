#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Starts the grpc servicer
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import argparse

from drama import service


def main(args):
    service.start_grpc_server(args.port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawler')
    parser.add_argument('-p', '--port', dest='port', default=9999,
                        help='gRPC service port')
    main(parser.parse_args())
