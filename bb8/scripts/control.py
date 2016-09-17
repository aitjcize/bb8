#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    BB8 Deployment Script
    ~~~~~~~~~~~~~~~~~~~~~

    Main script for BB8 deployment.

    Copyright 2016 bb8 Authors
"""

from __future__ import print_function

import argparse
import glob
import json
import logging
import os
import re
import subprocess
import sys

import colorlog
import jsonschema

from bb8 import config


BB8_SRC_ROOT = os.path.normpath(os.path.join(
    os.path.abspath(os.path.dirname(os.path.realpath(__file__))),
    '..', '..'))
BB8_DATA_ROOT = '/var/lib/bb8'
BB8_NETWORK = 'bb8_network'
BB8_CLIENT_PACKAGE_NAME = 'bb8-client-9999.tar.gz'


logger = logging.getLogger('bb8ctl')


def setup_logger():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s:%(name)s:%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def get_manifest_schema():
    """Return the schema of app manifest."""
    with open(os.path.join(BB8_SRC_ROOT, 'apps', 'schema.app.json')) as f:
        return json.load(f)


def run(command, allow_error=False):
    """Simple wrapper for executing shell command."""
    try:
        subprocess.check_call(command, shell=True)
    except Exception:
        if not allow_error:
            raise


def get_output(command):
    """Simple wrapper for getting shell command output."""
    return subprocess.check_output(command, shell=True)


def get_dir_hash(path):
    """Generate a hash representing a given directory."""
    dir_hash = get_output(
        'cd %s; find . -type f -exec sha1sum {} \\; | sha1sum' % path)
    return dir_hash[:6]


def create_dir_if_not_exists(path, sudo=False):
    """Create an directory if it does not exists."""
    if not os.path.exists(path):
        if sudo:
            run('sudo mkdir -p %s' % path)
        else:
            os.makedirs(path)


def docker_get_instance(name):
    return get_output(
        'docker ps -a --format "{{.Names}}" | grep "%s"; true' %
        name).strip()


def database_env_switch():
    if config.DEPLOY:
        return ''
    database = os.getenv('DATABASE', None)
    if database is None:
        logger.error('dev database not specified')
    database = database.replace('127.0.0.1', '172.17.0.1')
    return ' -e DATABASE=%s ' % database


class App(object):
    """App class representing an BB8 third-party app."""

    BB8_APP_PREFIX = 'bb8.app'
    SCHEMA = get_manifest_schema()

    VOLUME_PRIVILEGE_WHITELIST = ['system', 'content']

    def __init__(self, app_dir):
        self._app_dir = app_dir
        with open(os.path.join(app_dir, 'manifest.json'), 'r') as f:
            self._info = json.load(f)

        try:
            jsonschema.validate(self._info, self.SCHEMA)
        except jsonschema.exceptions.ValidationError:
            raise RuntimeError('Validation failed for app `%s\'' %
                               os.path.basename(app_dir))

        self._app_name = self._info['name']
        self._image_name = '%s.%s' % (self.BB8_APP_PREFIX,
                                      self._app_name)

    def start(self, force=False, bind=False):
        print('=' * 20, 'Starting %s' % self._app_name, '=' * 20)
        self.start_container(force, bind)

    def get_cpu_shares(self):
        cpu = self._info['resource']['cpu']
        if cpu == 'low':
            return 128
        elif cpu == 'medium':
            return 256
        else:
            return 512

    def get_memory_limit(self):
        return '%dm' % self._info['resource']['memory']

    def hack_remove_unecessary_imports(self, filename):
        """The gRPC module compiled by the protoc compiler contains unnecessary
        imports. Which cause ImportError if we rename the module. Remove those
        imports to work around the problem.
        """
        with open(filename, 'r') as f:
            data = f.read()

        data = re.sub(r'import service_pb2', '', data)
        data = re.sub(r'service_pb2\.', '', data)

        with open(filename, 'w') as f:
            f.write(data)

    def compile_and_install_service_proto(self):
        """Compile and install service gRPC module."""
        # Compile protobuf python module
        run('docker run -it --rm -v %s:/defs aitjcize/protoc-python' %
            (self._app_dir))
        # Copy to app dir
        run('cp %(path)s/pb-python/service_pb2.py %(path)s' %
            {'path': self._app_dir})

        # Hack: remove unecessary imports
        self.hack_remove_unecessary_imports(
            '%s/service_pb2.py' % self._app_dir)

        # Copy to bb8.pb_modules
        run('cp %(path)s/service_pb2.py %(dest)s/%(name)s_service_pb2.py' %
            {'path': self._app_dir,
             'dest': os.path.join(BB8_SRC_ROOT, 'bb8', 'pb_modules'),
             'name': self._app_name})
        # Remove pb-python dir
        run('sudo rm -rf %s/pb-python' % self._app_dir)

    def stop(self):
        instance = docker_get_instance(self._image_name)
        if instance:
            run('docker rm -f %s' % instance, True)

    def start_container(self, force=False, bind=False):
        # Compile service proto before calculating app version hash, so the
        # hash includes the compiled serivce_pb2.py
        self.compile_and_install_service_proto()

        app_version_hash = get_dir_hash(self._app_dir)
        container_name = '%s.%s' % (self._image_name, app_version_hash)
        instance = docker_get_instance(self._image_name)

        m = re.match(r'^%s\.(.*?)$' % self._image_name, instance)
        if m:
            running_version_hash = m.group(1)
            if running_version_hash == app_version_hash:
                logger.warn('%s: no change since last deploy.', self._app_name)

                if force:
                    logger.warn('%s: force deploy requested, continuing '
                                'deployment ...', self._app_name)
                else:
                    logger.warn('%s: skip deployment.', self._app_name)
                    return

        app_state_dir = os.path.join(BB8_DATA_ROOT, 'apps', self._app_name)
        volumes = []

        if 'volumes' in self._info['resource']:
            for target, path in self._info['resource']['volumes']:
                # Prevent mapping path outside of app dir except for the
                # BB8 system app.
                if ((target.startswith('/') or target.startswith('.')) and
                        self._app_name not in self.VOLUME_PRIVILEGE_WHITELIST):
                    logger.info('%s: invalid volume `%s\' detected, abort.',
                                self._app_name, target)
                    return

                volumes.append('-v %s:%s' %
                               (os.path.join(self._app_dir, target), path))

        if 'states' in self._info['resource']:
            for name, path in self._info['resource']['states']:
                state_dir = os.path.join(app_state_dir, name)
                create_dir_if_not_exists(state_dir, sudo=True)
                volumes.append('-v %s:%s' % (state_dir, path))

        run('cp %s %s' %
            (os.path.join(BB8_SRC_ROOT, 'dist', BB8_CLIENT_PACKAGE_NAME),
             self._app_dir))

        run('docker build -t %s %s' % (self._image_name, self._app_dir))

        run('rm %s' % os.path.join(self._app_dir, BB8_CLIENT_PACKAGE_NAME))

        if instance:
            run('docker rm -f %s' % instance, True)

        run('docker run'
            ' --name={0}'.format(container_name) +
            ' --net={0}'.format(BB8_NETWORK) +
            ' --net-alias={0}'.format(self._image_name) +
            ' --cpu-shares={0}'.format(self.get_cpu_shares()) +
            ' -m {0}'.format(self.get_memory_limit()) +
            ' -e BB8_DEPLOY={0}'.format(str(config.DEPLOY).lower()) +
            (' -p 9999:9999' if bind else ' ') +
            database_env_switch() +
            ' '.join(volumes) +
            ' -d %s' % self._image_name)

    def logs(self):
        instance = docker_get_instance(self._image_name)
        if instance:
            run('docker logs %s' % instance)


class BB8(object):
    BB8_IMAGE_NAME = 'bb8'
    BB8_CONTAINER_NAME = 'bb8.main'
    BB8_SERVICE_PREFIX = 'bb8.service'
    BB8_INDOCKER_PORT = 5000
    CLOUD_SQL_DIR = '/cloudsql'

    def __init__(self):
        self._app_dirs = self.get_app_dirs()

    def start_services(self):
        redis_service = '%s.redis' % self.BB8_SERVICE_PREFIX
        instance = docker_get_instance(redis_service)
        if not instance:
            run('docker run ' +
                '--net=%s ' % BB8_NETWORK +
                '--net-alias=%s ' % redis_service +
                '--name %s -d redis' % redis_service)

    @classmethod
    def get_app_dirs(cls):
        apps_dir = os.path.join(BB8_SRC_ROOT, 'apps')
        return [os.path.join(apps_dir, app_dir)
                for app_dir in os.listdir(apps_dir)
                if os.path.isdir(os.path.join(apps_dir, app_dir))]

    def copy_extra_source(self):
        """Copy extra source required by client module."""
        LIST = ['base_message.py', 'database_utils.py', 'query_filters.py']
        for filename in LIST:
            run('ln -f %s %s' %
                (os.path.join(BB8_SRC_ROOT, 'bb8', 'backend', filename),
                 os.path.join(BB8_SRC_ROOT, 'bb8_client')))

    def compile_and_install_proto(self):
        """Compile and install gRPC module."""
        proto_dir = os.path.join(BB8_SRC_ROOT, 'bb8', 'proto')

        # Compile protobuf python module
        run('docker run -it --rm -v %s:/defs aitjcize/protoc-python' %
            proto_dir)

        # Copy to bb8.pb_modules
        for proto in glob.glob('%s/*.proto' % proto_dir):
            name = os.path.basename(proto).rstrip('.proto')
            run('cp %(path)s/%(name)s_pb2.py %(dest)s' %
                {'path': os.path.join(proto_dir, 'pb-python'),
                 'name': name,
                 'dest': os.path.join(BB8_SRC_ROOT, 'bb8', 'pb_modules')})

        # Copy app_service to bb8_client package
        run('cp %s/pb-python/app_service_pb2.py %s' %
            (proto_dir,
             os.path.join(BB8_SRC_ROOT, 'bb8_client')))

        # Remove pb-python dir
        run('sudo rm -rf %s/pb-python' % proto_dir)

    def build_client_package(self):
        run('cd %s; python setup.py sdist' % BB8_SRC_ROOT)
        run('rm -rf %s' % os.path.join(BB8_SRC_ROOT, 'bb8_client.egg-info'))

    def prepare_resource(self):
        self.copy_extra_source()
        self.build_client_package()
        self.compile_and_install_proto()

    def compile_resource(self):
        self.prepare_resource()

        for app_dir in self._app_dirs:
            app = App(app_dir)
            app.compile_and_install_service_proto()

    def setup_network(self):
        run('docker network create %s' % BB8_NETWORK, True)

    def start(self, force=False):
        self.prepare_resource()
        self.setup_network()
        self.start_services()

        for app_dir in self._app_dirs:
            app = App(app_dir)
            app.start(force)

        print('=' * 20, 'Starting BB8 main container', '=' * 20)
        self.start_container(force)

    def get_git_version_hash(self):
        commit_hash = get_output('cd %s; git rev-parse HEAD' %
                                 BB8_SRC_ROOT)
        return commit_hash[:6]

    def stop(self):
        instance = docker_get_instance(self.BB8_CONTAINER_NAME)
        if instance:
            run('docker rm -f %s' % instance, True)

        for app_dir in self._app_dirs:
            app = App(app_dir)
            app.stop()

    def start_container(self, force=False):
        create_dir_if_not_exists(os.path.join(BB8_DATA_ROOT, 'log'), sudo=True)

        version_hash = self.get_git_version_hash()
        instance = docker_get_instance(self.BB8_CONTAINER_NAME)
        new_container_name = '%s.%s' % (self.BB8_CONTAINER_NAME, version_hash)

        m = re.match(r'^%s\.(.*?)$' % self.BB8_CONTAINER_NAME, instance)
        if m:
            running_version_hash = m.group(1)
            if running_version_hash == version_hash:
                logger.warn('BB8: no change since last deploy.')

                if force:
                    logger.warn('BB8: force deploy requested, '
                                'continuing deployment ...')
                else:
                    logger.warn('BB8: skip deployment.')
                    sys.exit(1)

        run('sudo umount %s/log >/dev/null 2>&1' % BB8_DATA_ROOT, True)
        run('docker build -t %s %s' % (self.BB8_IMAGE_NAME, BB8_SRC_ROOT))

        if instance:
            run('docker rm -f %s' % instance, True)

        run('docker run'
            ' --name={0} '.format(new_container_name) +
            ' --net={0}'.format(BB8_NETWORK) +
            ' --net-alias={0}'.format(self.BB8_CONTAINER_NAME) +
            ' -p {0}:{1}'.format(config.HTTP_PORT, self.BB8_INDOCKER_PORT) +
            ' -p {0}:{0}'.format(config.APP_API_SERVICE_PORT) +
            ' -v {0}:{0}'.format(self.CLOUD_SQL_DIR) +
            ' -e HTTP_PORT={0}'.format(config.HTTP_PORT) +
            database_env_switch() +
            ' -d {0}'.format(self.BB8_IMAGE_NAME))

        run('sudo mount --bind '
            '$(docker inspect -f \'{{index (index .Mounts 1) "Source"}}\' %s) '
            '%s' %
            (new_container_name, os.path.join(BB8_DATA_ROOT, 'log')), True)

    def logs(self):
        instance = docker_get_instance(self.BB8_CONTAINER_NAME)
        if instance:
            run('docker logs %s' % instance)

    def status(self):
        run('docker ps -a --format '
            '"table {{.Image}}\t{{.Names}}\t{{.Ports}}\t{{.Status}}" | '
            'egrep "(IMAGE|bb8\\.)"')


def main():
    root_parser = argparse.ArgumentParser(description='BB8 control script')
    subparsers = root_parser.add_subparsers(help='sub-command')

    # start sub-command
    start_parser = subparsers.add_parser('start', help='start bb8')
    start_parser.set_defaults(which='start')
    start_parser.add_argument('-f', '--force', dest='force',
                              action='store_true', default=False,
                              help='Deploy even if version hash has not '
                              'changed')
    start_parser.add_argument('-a', '--app', dest='app', default=None,
                              help='operate on specific app')
    start_parser.add_argument('-b', '--bind', dest='bind',
                              action='store_true', default=False,
                              help='Bind app service port to localhost')

    # stop sub-command
    stop_parser = subparsers.add_parser('stop', help='stop bb8')
    stop_parser.set_defaults(which='stop')
    stop_parser.add_argument('-a', '--app', dest='app', default=None,
                             help='operate on specific app')

    # logs sub-command
    logs_parser = subparsers.add_parser('logs', help='show bb8 logs')
    logs_parser.set_defaults(which='logs')
    logs_parser.add_argument('-a', '--app', dest='app', default=None,
                             help='operate on specific app')

    # status sub-command
    status_parser = subparsers.add_parser('status', help='show bb8 status')
    status_parser.set_defaults(which='status')

    # status sub-command
    compile_resource_parser = subparsers.add_parser(
        'compile-resource', help='compile bb8 resource')
    compile_resource_parser.set_defaults(which='compile-resource')

    args = root_parser.parse_args()

    bb8 = BB8()
    app = None
    if hasattr(args, 'app') and args.app:
        app_dir = os.path.join(BB8_SRC_ROOT, 'apps', args.app)
        if not os.path.exists(app_dir):
            logger.error('No app named `%s\', abort.', args.app)
            sys.exit(1)
        app = App(app_dir)

    if args.which == 'start':
        if app:
            app.start(args.force, args.bind)
        else:
            if args.bind:
                logger.warn('bind option only works with single app, ignored')
            bb8.start(args.force)
    elif args.which == 'stop':
        if app:
            app.stop()
        else:
            bb8.stop()
    elif args.which == 'logs':
        if app:
            app.logs()
        else:
            bb8.logs()
    elif args.which == 'status':
        bb8.status()
    elif args.which == 'compile-resource':
        bb8.compile_resource()
    else:
        raise RuntimeError('invalid sub-command')


if __name__ == '__main__':
    setup_logger()
    try:
        main()
    except Exception as e:
        logger.exception('error: %s', e)
