# Copyright 2016 bb8 Authors

LINT_FILES=$(shell find bb8 -name '*.py' -type f | sort)
UNITTESTS=$(shell find bb8 -name '*_unittest.py' | sort)

LINT_OPTIONS=--rcfile=bin/pylintrc \
	     --msg-template='{path}:{line}: {msg_id}: {msg}'

DB_URI='mysql+pymysql://bb8:bb8test@127.0.0.1:3307/bb8?charset=utf8mb4'

all: test lint validate-bots

setup-database:
	@sudo docker rm -f bb8_mysql 2>/dev/null || true
	sudo docker run --name bb8_mysql -p 3307:3306 \
	    -e MYSQL_ROOT_PASSWORD=root \
	    -e MYSQL_USER=bb8 \
	    -e MYSQL_PASSWORD=bb8test \
	    -e MYSQL_DATABASE=bb8 \
	    -d mysql:latest
	@echo 'Waiting 20 sec for MySQL to initialize ...'; sleep 20

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
	   COVERAGE_FILE=.coverage_$$COVER coverage run $$test; \
	 done
	@coverage combine .coverage_*
	@coverage html --include=bb8/*

lint:
	@pep8 $(LINT_FILES)
	@pylint $(LINT_OPTIONS) $(LINT_FILES)

validate-bots:
	make -C bots

deploy:
	sudo docker build -t bb8 .
	sudo docker rm -f bb8
	sudo docker run --name bb8 -p 5000:5000 -p 2222:22 -d bb8
