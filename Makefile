# Copyright 2016 bb8 Authors

LINT_FILES = $(shell find bb8 apps -name '*.py' -type f | grep -v '_pb2' | sort)
UNITTESTS = $(shell find bb8 -name '*_unittest.py' | sort)

LINT_OPTIONS = --rcfile=bin/pylintrc \
	       --msg-template='{path}:{line}: {msg_id}: {msg}'

PORT ?= 3307
DOCKER_IP ?= 127.0.0.1

DB_URI = "mysql+pymysql://bb8:bb8test@$(DOCKER_IP):$(PORT)/bb8?charset=utf8mb4"

CLOUD_SQL_DIR = "/cloudsql"

STATE_DIR = $(CURDIR)/states

all: test lint validate-bots

setup-database:
	@if ! docker ps | grep bb8_mysql.$(USER); then \
	   docker run --name bb8_mysql.$(USER) -p $(PORT):3306 \
	       -v $(CURDIR)/conf/mysql:/etc/mysql/conf.d \
	       -e MYSQL_ROOT_PASSWORD=root \
	       -e MYSQL_USER=bb8 \
	       -e MYSQL_PASSWORD=bb8test \
	       -e MYSQL_DATABASE=bb8 \
	       -d mysql:latest; \
	   echo 'Waiting 20 sec for MySQL to initialize ...'; \
	   sleep 20; \
	 fi

remove-database:
	@docker rm -f bb8_mysql.$(USER)

test: setup-database
	@export PYTHONPATH=$$PWD; \
	 export DATABASE=$(DB_URI); \
	 for test in $(UNITTESTS); do \
	   echo Running $$test ...; \
	   $$test || exit 1; \
	 done

coverage: setup-database
	@export PYTHONPATH=$$PWD; \
	 export DATABASE=$(DB_URI); \
	 for test in $(UNITTESTS); do \
	   COVER=$$(echo $$test | tr '/' '_'); \
	   echo Running $$test ...; \
	   COVERAGE_FILE=.coverage_$$COVER coverage run $$test || exit 1; \
	 done
	@coverage combine .coverage_*
	@coverage html --include=bb8/*

lint:
	@pep8 $(LINT_FILES)
	@pylint $(LINT_OPTIONS) $(LINT_FILES)

validate-bots:
	make -C bots

cloud-sql:
	sudo $(CURDIR)/bin/cloud_sql_proxy -dir=$(CLOUD_SQL_DIR) &

cleanup-docker:
	@docker rm -v $(docker ps -a -q -f status=exited) 2>/dev/null || true
	@docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true

clean:
	find bb8 apps -name '*_pb2.py' -exec rm -f {} \;

deploy:
	@bb8ctl start
