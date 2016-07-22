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
import json
import os
import re
import subprocess
import sys

import jsonschema

from bb8 import config


BB8_SRC_ROOT = os.path.normpath(os.path.join(
    os.path.abspath(os.path.dirname(os.path.realpath(__file__))),
    '..', '..'))
BB8_DATA_ROOT = '/var/lib/bb8'


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


class App(object):
    """App class representing an BB8 third-party app."""

    BB8_APP_PREFIX = 'bb8.app'
    SCHEMA = get_manifest_schema()

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
                                      self._app_name.lower())

    def run(self, force=False):
        self.start_container(force)

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
        run('docker run -it --rm -v %s:/defs namely/protoc-python' %
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
             'name': self._app_name.lower()})
        # Remove pb-python dir
        run('sudo rm -rf %s/pb-python' % self._app_dir)

    def stop(self):
        instance = docker_get_instance(self._image_name)
        if instance:
            run('docker rm -f %s' % instance, True)

    def start_container(self, force=False):
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
                print('%s: no change since last deploy.' % self._app_name)

                if force:
                    print('%s: force deploy requested, continuing deployment '
                          '...' % self._app_name)
                else:
                    print('%s: skip deployment.' % self._app_name)
                    return

        apps_state_dir = os.path.join(BB8_DATA_ROOT, 'apps')
        volumes = []

        if 'volumes' in self._info['resource']:
            for target, path in self._info['resource']['volumes']:
                # Prevent mapping path outside of app dir except for the
                # BB8 system app.
                if (self._app_name != 'System' and
                        (target.startswith('/') or target.startswith('.'))):
                    print('%s: invalid volume `%s\' detected, abort.' %
                          (self._app_name, target))
                    return

                volumes.append('-v %s:%s' %
                               (os.path.join(self._app_dir, target), path))

        if 'states' in self._info['resource']:
            for name, path in self._info['resource']['states']:
                app_state_dir = os.path.join(apps_state_dir, name)
                create_dir_if_not_exists(app_state_dir, sudo=True)
                volumes.append('-v %s:%s' % (app_state_dir, path))

        addr = config.APPS_ADDR_MAP.get(self._app_name, None)
        if not addr:
            print('Fatal: no port mapping for app `%s\'' % self._app_name)
            sys.exit(1)

        run('docker build -t %s %s' % (self._image_name, self._app_dir))

        if instance:
            run('docker rm -f %s' % instance, True)

        run('docker run --name %s ' % container_name +
            '--cpu-shares %d ' % self.get_cpu_shares() +
            '-m %s ' % self.get_memory_limit() +
            '-p %d:%d ' % (addr[1], self._info['service_port']) +
            ' '.join(volumes) +
            ' -d %s' % self._image_name)


class BB8(object):
    BB8_IMAGE_NAME = 'bb8'
    BB8_CONTAINER_NAME = 'bb8.main'
    CLOUD_SQL_DIR = '/cloudsql'

    def __init__(self):
        self._app_dirs = self.get_app_dirs()

    @classmethod
    def get_app_dirs(cls):
        apps_dir = os.path.join(BB8_SRC_ROOT, 'apps')
        return [os.path.join(apps_dir, app_dir)
                for app_dir in os.listdir(apps_dir)
                if os.path.isdir(os.path.join(apps_dir, app_dir))]

    def run(self, force=False):
        for app_dir in self._app_dirs:
            app = App(app_dir)
            app.run(force)

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
                print('BB8: no change since last deploy.')

                if force:
                    print('BB8: force deploy requested, continuing deployment '
                          '...')
                else:
                    print('BB8: skip deployment.')
                    sys.exit(1)

        run('sudo umount %s/log >/dev/null 2>&1' % BB8_DATA_ROOT, True)
        run('docker build -t %s %s' % (self.BB8_IMAGE_NAME, BB8_SRC_ROOT))

        if instance:
            run('docker rm -f %s' % instance, True)

        run('docker run --name %(name)s '
            '-p 5000:5000 '
            '-v %(cloud_sql_dir)s:%(cloud_sql_dir)s '
            '-d %(image_name)s' % {
                'name': new_container_name,
                'cloud_sql_dir': self.CLOUD_SQL_DIR,
                'image_name': self.BB8_IMAGE_NAME
            })

        run('sudo mount --bind '
            '$(docker inspect -f \'{{index (index .Mounts 1) "Source"}}\' %s) '
            '%s' %
            (new_container_name, os.path.join(BB8_DATA_ROOT, 'log')), True)


def main():
    parser = argparse.ArgumentParser(description='BB8 deploy script')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        default=False, help='Deploy even if version hash '
                        'has not changed')
    parser.add_argument('-a', '--app', dest='app', default=None,
                        help='Deploy an app')
    parser.add_argument('--stop', dest='stop', action='store_true',
                        default=None, help='Stop all containers')

    args = parser.parse_args()

    if args.app:
        app_dir = os.path.join(BB8_SRC_ROOT, 'apps', args.app)
        if not os.path.exists(app_dir):
            print('No app named `%s\', abort.' % args.app)
            sys.exit(1)
        app = App(app_dir)
        if args.stop:
            app.stop()
        else:
            app.run(args.force)
        sys.exit(0)

    bb8 = BB8()
    if args.stop:
        bb8.stop()
    else:
        bb8.run(args.force)


if __name__ == '__main__':
    main()
