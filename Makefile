# Copyright 2016 bb8 Authors

LINT_FILES=$(shell find bb8 -name '*.py' -type f | sort)
UNITTESTS=$(shell find bb8 -name '*_unittest.py' | sort)

LINT_OPTIONS=--rcfile=bin/pylintrc \
	     --msg-template='{path}:{line}: {msg_id}: {msg}'

all: test lint validate-bots

test:
	@export PYTHONPATH=$$PWD; \
	 for test in $(UNITTESTS); do \
	   echo Running $$test ...; \
	   $$test || exit 1; \
	 done

coverage:
	@export PYTHONPATH=$$PWD; \
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
	sudo docker run -p 5000:5000 -p 2222:22 -d --name bb8 bb8
