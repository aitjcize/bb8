# Copyright 2016 bb8 Authors

LINT_FILES = $(shell find bb8 bb8_client apps -name '*.py' -type f | egrep -v '(_pb2|alembic|node_modules)' | sort)
UNITTESTS = $(shell find bb8 bb8_client apps -name '*_unittest.py' | sort)

LINT_OPTIONS = --rcfile=bin/pylintrc \
	       --msg-template='{path}:{line}: {msg_id}: {msg}' \
	       --generated-members='service_pb2.*'

CLOUD_SQL_DIR = "/cloudsql"

all: test lint validate-bots

setup-database:
	@if ! docker ps | grep bb8_mysql.$(USER); then \
	   docker run --name bb8_mysql.$(USER) -p $(MYSQL_PORT):3306 \
	       -v $(CURDIR)/conf/mysql:/etc/mysql/conf.d \
	       -e MYSQL_ROOT_PASSWORD=root \
	       -e MYSQL_USER=bb8 \
	       -e MYSQL_PASSWORD=bb8test \
	       -e MYSQL_DATABASE=bb8 \
	       -d mysql:latest; \
	   echo 'Waiting 20 sec for MySQL to initialize ...'; \
	   sleep 20; \
	 fi;

remove-database:
	@docker rm -f bb8_mysql.$(USER)

setup-redis:
	@if ! docker ps | grep bb8_redis.$(USER); then \
	   docker run --name bb8_redis.$(USER) -p $(REDIS_PORT):6379 \
	       -d redis; \
	   echo 'Waiting 10 sec for Redis to initialize ...'; \
	   sleep 10; \
	 fi

remove-redis:
	@docker rm -f bb8_redis.$(USER)

start-celery:
	@celery -A bb8.celery worker --loglevel=info --concurrency 4

frontend-test:
	@manage reset_for_dev
	@cd bb8/frontend && \
	 npm run test && \
	 npm run build
	@manage reset

test: setup-database setup-redis frontend-test
	@export BB8_TEST=true; \
	 for test in $(UNITTESTS); do \
	   if echo $$test | grep '^apps'; then \
	     export PYTHONPATH=$(CURDIR):$(CURDIR)/$$(echo $$test | \
	       sed 's+\(apps/[^/]*/\).*+\1+'); \
	   else \
	     export PYTHONPATH=$(CURDIR); \
	   fi; \
	   echo Running $$test ...; \
	   $$test || exit 1; \
	 done
	@manage reset_for_dev

coverage: setup-database setup-redis frontend-test
	@export BB8_TEST=true; \
	 for test in $(UNITTESTS); do \
	   if echo $$test | grep '^apps'; then \
	     export PYTHONPATH=$(CURDIR):$(CURDIR)/$$(echo $$test | \
	       sed 's+\(apps/[^/]*/\).*+\1+'); \
	   else \
	     export PYTHONPATH=$(CURDIR); \
	   fi; \
	   COVER=$$(echo $$test | tr '/' '_'); \
	   echo Running $$test ...; \
	   COVERAGE_FILE=.coverage_$$COVER coverage run $$test || exit 1; \
	 done
	@COVERAGE_FILE=.coverage_manage_reset coverage \
	   run bin/manage reset_for_dev
	@coverage combine .coverage_*
	@coverage html --include=bb8/*

lint:
	@cd bb8/frontend && npm run lint:css
	@pep8 $(LINT_FILES)
	@pylint $(LINT_OPTIONS) $(LINT_FILES)

compile-resource:
	@bb8ctl compile-resource

# Compile resource without copying credentials. This is used in CI
# environment, which is not run on compose.ai dev server.
compile-resource-no-cred:
	@bb8ctl compile-resource --no-copy-credential

validate-bots:
	make -C bots

cloud-sql:
	sudo $(CURDIR)/bin/cloud_sql_proxy -dir=$(CLOUD_SQL_DIR) &

cleanup-docker:
	@docker rm $(docker ps --all --quiet --filter status=exited --no-trunc)
	@docker volume rm $(docker volume ls --quiet --filter dangling=true)
	@docker rmi $(docker images --quiet --filter="dangling=true" --no-trunc)


clean:
	find bb8 bb8_client apps -name '*_pb2.py' -exec rm -f {} \;

test-deploy:
	@BB8_DEPLOY=false bb8ctl start

deploy:
	@BB8_DEPLOY=true HTTP_PORT=5000 bb8ctl start
