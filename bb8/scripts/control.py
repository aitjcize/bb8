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
import time

import colorlog
import jsonschema

from bb8 import SRC_ROOT as BB8_SRC_ROOT
from bb8 import config, util
from bb8.backend import modules

BB8_DATA_ROOT = '/var/lib/bb8'
BB8_NETWORK = 'bb8_network'
BB8_CLIENT_PACKAGE_NAME = 'bb8-client-9999.tar.gz'
BB8_CREDENTIALS_DIR = '/etc/bb8/'
BB8_CELERY_PID_FILE = '/var/lib/bb8/celery.pid'
BB8_CELERY_SHUTDOWN_WAIT_SECS = 10


logger = logging.getLogger('bb8ctl')


def setup_logger():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s:%(name)s:%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def scoped_name(name):
    """Return name if we are in deploy mode, else the scoped name for a given
    bb8 object name."""
    return (name if config.DEPLOY else
            '%s.%s' % (os.getenv('BB8_SCOPE', 'nobody'), name))


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
    return get_output('git log -n 1 --pretty=format:%%h %s' % path)


def create_dir_if_not_exists(path, sudo=False):
    """Create an directory if it does not exists."""
    if not os.path.exists(path):
        if sudo:
            run('sudo mkdir -p %s' % path)
        else:
            os.makedirs(path)


def docker_get_instance(name):
    """Get docker instance with name.

    Returns: A tuple (instance_name, running).
    """
    result = get_output(
        'docker ps -a --format "{{.Names}},{{.Status}}" | grep "%s"; true' %
        name).strip()
    if not result:
        return '', False

    name, status_text = result.split(',')
    running = True if 'Up' in status_text else False
    return name, running


def hostname_env_switch():
    hostname = os.getenv('BB8_HOSTNAME', None)
    return ' -e BB8_HOSTNAME={0} '.format(hostname) if hostname else ''


def database_env_switch():
    if config.DEPLOY:
        return ''
    database = os.getenv('DATABASE', None)
    if database is None:
        raise RuntimeError('dev database not specified')
    return ' -e DATABASE=%s ' % database


def redis_env_switch():
    if config.DEPLOY:
        return ''
    redis = os.getenv('REDIS_URI', None)
    if redis is None:
        raise RuntimeError('dev redis not specified')
    return ' -e REDIS_URI=%s ' % redis


class App(object):
    """App class representing an BB8 third-party app."""

    BB8_APP_PREFIX = scoped_name('bb8.app')
    SCHEMA = util.get_schema('app')

    VOLUME_PRIVILEGE_WHITELIST = ['system', 'content', 'drama']

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

    def start(self, force=False, bind=False):
        print('=' * 20, 'Starting %s' % self._app_name, '=' * 20)
        self.start_container(force, bind)

    def stop(self):
        instance, unused_running = docker_get_instance(self._image_name)
        if instance:
            run('docker rm -f %s' % instance, True)

    def shell(self, command=None):
        instance, running = docker_get_instance(self._image_name)
        if not instance or not running:
            logger.error('App `%s\' not running', self._image_name)
            return
        s = subprocess.Popen('docker exec -it %s %s' %
                             (instance,
                              'bash' + (" -c '%s'" % command
                                        if command else '')),
                             shell=True)
        s.wait()

    def start_container(self, force=False, bind=False):
        # Compile service proto before calculating app version hash, so the
        # hash includes the compiled serivce_pb2.py
        self.compile_and_install_service_proto()

        app_version_hash = get_dir_hash(self._app_dir)
        container_name = '%s.%s' % (self._image_name, app_version_hash)
        instance, running = docker_get_instance(self._image_name)

        if running:
            m = re.match(r'^%s\.(.*?)$' % self._image_name, instance)
            if m:
                version_hash = m.group(1)
                if version_hash == app_version_hash:
                    logger.warn('%s: no change since last deploy.',
                                self._app_name)

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
                    logger.error('%s: invalid volume `%s\' detected, abort.',
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
            ' -e BB8_SCOPE={0}'.format(os.getenv('BB8_SCOPE', 'nobody')) +
            ' -e BB8_DEPLOY={0}'.format(str(config.DEPLOY).lower()) +
            ' -e BB8_HTTP_PORT={0}'.format(config.HTTP_PORT) +
            (' -p {0}:9999'.format(os.getenv('APP_RPC_PORT', 9999))
             if bind else ' ') +
            database_env_switch() +
            hostname_env_switch() +
            ' '.join(volumes) +
            ' -d %s' % self._image_name)

    def logs(self):
        instance, unused_running = docker_get_instance(self._image_name)
        if instance:
            run('docker logs %s' % instance)


class BB8(object):
    BB8_IMAGE_NAME = 'bb8'
    BB8_CONTAINER_NAME = scoped_name('bb8.main')
    BB8_SERVICE_PREFIX = scoped_name('bb8.service')
    BB8_INDOCKER_PORT = 5000
    CLOUD_SQL_DIR = '/cloudsql'

    def __init__(self):
        self._app_dirs = self.get_app_dirs()

    def start_services(self):
        redis_service = '%s.redis' % self.BB8_SERVICE_PREFIX
        instance, running = docker_get_instance(redis_service)
        if instance and not running:
            run('docker rm -f %s' % redis_service)
        if not running:
            run('docker run ' +
                '--net=%s ' % BB8_NETWORK +
                '--net-alias=%s ' % redis_service +
                '--name %s -d redis' % redis_service)

        datadog_service = '%s.datadog' % self.BB8_SERVICE_PREFIX
        instance, running = docker_get_instance(datadog_service)
        if instance and not running:
            run('docker rm -f %s' % datadog_service)
        if not running:
            run('docker run ' +
                '--net=%s ' % BB8_NETWORK +
                '--net-alias=%s ' % datadog_service +
                '-v /var/run/docker.sock:/var/run/docker.sock ' +
                '-v /proc/:/host/proc/:ro ' +
                '-v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro ' +
                '-e API_KEY=%s ' % config.DATADOG_API_KEY +
                '--name %s -d ' % datadog_service +
                'datadog/docker-dd-agent:latest-alpine')

    @classmethod
    def get_app_dirs(cls):
        apps_dir = os.path.join(BB8_SRC_ROOT, 'apps')
        return [os.path.join(apps_dir, app_dir)
                for app_dir in os.listdir(apps_dir)
                if os.path.isdir(os.path.join(apps_dir, app_dir))]

    def copy_credentials(self):
        """Copy required credentials."""
        # We shouldn't need credential when testing
        if config.TESTING:
            return

        # Copy SSL-certificate
        run('cp -r %s %s' % (os.path.join(BB8_CREDENTIALS_DIR, 'certs'),
                             BB8_SRC_ROOT))

        # Copy Google-Cloud credential
        target = os.path.join(BB8_SRC_ROOT, 'credential')
        if not os.path.exists(target):
            os.makedirs(target)
        run('cp -r %s %s' %
            (os.path.join(BB8_CREDENTIALS_DIR, 'compose-ai.json'), target))

        for app in ['content']:
            target = os.path.join(BB8_SRC_ROOT, 'apps', app, 'credential')
            if not os.path.exists(target):
                os.makedirs(target)
            run('cp -r %s %s' %
                (os.path.join(BB8_CREDENTIALS_DIR, 'compose-ai.json'), target))

    def copy_extra_source(self):
        """Copy extra source required by client module."""
        LIST = ['base_message.py', 'database_utils.py', 'template.py',
                'template_filters.py']
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

    def compile_static_frontend_resource(self):
        modules.compile_module_infos(
            os.path.join(BB8_SRC_ROOT, 'bb8', 'frontend', 'constants',
                         'ModuleInfos.json'))
        run('cp -r %s %s' %
            (os.path.join(BB8_SRC_ROOT, 'schema'),
             os.path.join(BB8_SRC_ROOT, 'bb8', 'frontend')))

    def compile_python_source(self):
        if not config.DEPLOY:
            return
        for subdir in ['bb8', 'apps']:
            run('python -OO -m compileall %s >/dev/null' %
                os.path.join(BB8_SRC_ROOT, subdir))

    def build_client_package(self):
        run('cd %s; python setup.py sdist' % BB8_SRC_ROOT)
        run('rm -rf %s' % os.path.join(BB8_SRC_ROOT, 'bb8_client.egg-info'))

    def prepare_resource(self, copy_credential=True):
        if copy_credential:
            self.copy_credentials()
        self.copy_extra_source()
        self.build_client_package()
        self.compile_and_install_proto()
        self.compile_static_frontend_resource()
        self.compile_python_source()

    def compile_resource(self, copy_credential=True):
        self.prepare_resource(copy_credential)

        for app_dir in self._app_dirs:
            app = App(app_dir)
            app.compile_and_install_service_proto()

    def install_misc_resource(self):
        RESOURCE_DEF = os.path.join(BB8_SRC_ROOT, 'conf', 'misc-resource.json')

        with open(RESOURCE_DEF, 'r') as f:
            resource_def = json.load(f)

        schema_def = util.get_schema('misc-resource')
        try:
            jsonschema.validate(resource_def, schema_def)
        except jsonschema.exceptions.ValidationError as e:
            raise RuntimeError('Fail to validate misc-resource definition: '
                               '%s' % e)

        # gsutil maybe under /root/google-cloud-sdk/bin/ if installed via pip
        os.environ['PATH'] = os.getenv('PATH') + ':/root/google-cloud-sdk/bin'

        # Copy module-resource
        for module, res_list in resource_def['module-resource'].iteritems():
            logger.info('Installing resource for %s ...', module)
            for resource in res_list:
                run('gsutil cp "%s" "%s"' % (resource['source'],
                                             resource['dest']))

                if resource['source'].endswith('.zip'):
                    run('cd "%s"; unzip "%s"' %
                        (os.path.dirname(resource['dest']),
                         os.path.basename(resource['source'])))

    def setup_network(self):
        run('docker network create %s' % BB8_NETWORK, True)

    def start(self, force=False, main_only=False):
        self.prepare_resource()
        self.setup_network()
        self.start_services()

        if not main_only:
            for app_dir in self._app_dirs:
                app = App(app_dir)
                app.start(force)

        print('=' * 20, 'Starting BB8 main container', '=' * 20)
        self.start_container(force)

    def stop(self):
        instance, unused_running = docker_get_instance(self.BB8_CONTAINER_NAME)
        if instance:
            logging.info('Waiting for celery workers to stop...')
            self.shell('kill -TERM $(cat %s)' % BB8_CELERY_PID_FILE)
            time.sleep(BB8_CELERY_SHUTDOWN_WAIT_SECS)
            run('docker rm -f %s' % instance, True)

    def stop_all(self):
        self.stop()
        for app_dir in self._app_dirs:
            app = App(app_dir)
            app.stop()

    def shell(self, command=None):
        instance, running = docker_get_instance(self.BB8_CONTAINER_NAME)
        if not instance or not running:
            logger.error('Main container `%s\' not running',
                         self.BB8_CONTAINER_NAME)
            return
        s = subprocess.Popen('docker exec -it %s %s' %
                             (instance,
                              'bash' + (" -c '%s'" % command
                                        if command else '')),
                             shell=True)
        s.wait()

    def get_git_version_hash(self):
        commit_hash = get_output('cd %s; git rev-parse HEAD' %
                                 BB8_SRC_ROOT)
        return commit_hash[:6]

    def start_container(self, force=False):
        create_dir_if_not_exists(os.path.join(BB8_DATA_ROOT, 'log'), sudo=True)

        version_hash = self.get_git_version_hash()
        instance, running = docker_get_instance(self.BB8_CONTAINER_NAME)
        new_container_name = '%s.%s' % (self.BB8_CONTAINER_NAME, version_hash)

        if running:
            m = re.match(r'^%s\.(.*?)$' % self.BB8_CONTAINER_NAME, instance)
            if m:
                old_version_hash = m.group(1)
                if version_hash == old_version_hash:
                    logger.warn('BB8: no change since last deploy.')

                    if force:
                        logger.warn('BB8: force deploy requested, '
                                    'continuing deployment ...')
                    else:
                        logger.warn('BB8: skip deployment.')
                        sys.exit(1)

        run('docker build -t %s %s' % (self.BB8_IMAGE_NAME, BB8_SRC_ROOT))

        self.stop()
        run('docker run'
            ' --name={0} '.format(new_container_name) +
            ' --net={0}'.format(BB8_NETWORK) +
            ' --net-alias={0}'.format(self.BB8_CONTAINER_NAME) +
            ' -p {0}:{1}'.format(config.HTTP_PORT, self.BB8_INDOCKER_PORT) +
            ' -v {0}:{0}'.format(self.CLOUD_SQL_DIR) +
            ' -e BB8_SCOPE={0}'.format(os.getenv('BB8_SCOPE', 'nobody')) +
            ' -e BB8_IN_DOCKER=true ' +
            ' -e BB8_DEPLOY={0}'.format(str(config.DEPLOY).lower()) +
            ' -e HTTP_PORT={0}'.format(config.HTTP_PORT) +
            database_env_switch() +
            redis_env_switch() +
            hostname_env_switch() +
            ' -d {0}'.format(self.BB8_IMAGE_NAME))

    def logs(self):
        instance, unused_running = docker_get_instance(self.BB8_CONTAINER_NAME)
        if instance:
            run('docker logs %s' % instance)

    def status(self):
        run('docker ps -a --format '
            '"table {{.Image}}\t{{.Names}}\t{{.Ports}}\t{{.Status}}" | '
            'egrep "(IMAGE|%s\\.)"' % scoped_name('bb8'))


def main():
    root_parser = argparse.ArgumentParser(description='BB8 control script')
    subparsers = root_parser.add_subparsers(help='sub-command')

    root_parser.add_argument('-a', '--app', dest='app', default=None,
                             help='operate on specific app')
    root_parser.add_argument('-m', '--main', dest='main', action='store_true',
                             default=False, help='operate on specific app')

    # start sub-command
    start_parser = subparsers.add_parser('start', help='start bb8')
    start_parser.set_defaults(which='start')
    start_parser.add_argument('-f', '--force', dest='force',
                              action='store_true', default=False,
                              help='Deploy even if version hash has not '
                              'changed')
    start_parser.add_argument('-b', '--bind', dest='bind',
                              action='store_true', default=False,
                              help='Bind app service port to localhost')

    # stop sub-command
    stop_parser = subparsers.add_parser('stop', help='stop bb8')
    stop_parser.set_defaults(which='stop')

    # logs sub-command
    logs_parser = subparsers.add_parser('logs', help='show bb8 logs')
    logs_parser.set_defaults(which='logs')

    # shell sub-command
    shell_parser = subparsers.add_parser('shell',
                                         help='get a shell into container')
    shell_parser.set_defaults(which='shell')

    # status sub-command
    status_parser = subparsers.add_parser('status', help='show bb8 status')
    status_parser.set_defaults(which='status')

    # compile-resource sub-command
    compile_resource_parser = subparsers.add_parser(
        'compile-resource', help='compile bb8 resource')
    compile_resource_parser.add_argument('--no-copy-credential',
                                         dest='no_copy_credential',
                                         action='store_true',
                                         default=False,
                                         help='Skip copy credential step')
    compile_resource_parser.set_defaults(which='compile-resource')

    # install-misc-resource sub-command
    install_misc_resource_parser = subparsers.add_parser(
        'install-misc-resource', help='install misc resource')
    install_misc_resource_parser.set_defaults(which='install-misc-resource')

    # We want to pass the rest of arguments after shell command directly to the
    # function without parsing it.
    try:
        index = sys.argv.index('shell')
    except ValueError:
        args = root_parser.parse_args()
    else:
        args = root_parser.parse_args(sys.argv[1:index + 1])

    bb8 = BB8()
    app = None
    if hasattr(args, 'app') and args.app:
        app_dir = os.path.join(BB8_SRC_ROOT, 'apps', args.app)
        if not os.path.exists(app_dir):
            logger.error('No app named `%s\', abort.', args.app)
            sys.exit(1)
        app = App(app_dir)

    if args.which == 'start':
        if not app and args.bind:
            logger.warn('bind option only works with single app, ignored')

        if args.main:
            bb8.start(args.force, main_only=True)
        elif app:
            app.start(args.force, args.bind)
        else:
            bb8.start(args.force)
    elif args.which == 'stop':
        if args.main:
            bb8.stop()
        if app:
            app.stop()
        else:
            bb8.stop_all()
    elif args.which == 'logs':
        if app:
            app.logs()
        else:
            bb8.logs()
    elif args.which == 'shell':
        command = ' '.join(sys.argv[sys.argv.index('shell') + 1:])
        if app:
            app.shell(command)
        else:
            bb8.shell(command)
    elif args.which == 'status':
        bb8.status()
    elif args.which == 'compile-resource':
        bb8.compile_resource(not args.no_copy_credential)
    elif args.which == 'install-misc-resource':
        bb8.install_misc_resource()
    else:
        raise RuntimeError('invalid sub-command')


if __name__ == '__main__':
    setup_logger()
    try:
        main()
    except Exception as e:
        logger.exception('error: %s', e)
