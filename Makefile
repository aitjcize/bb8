# Copyright 2016 bb8 Authors

LINT_FILES=$(shell find bb8 -name '*.py' -type f | sort)
UNITTESTS=$(shell find bb8 -name '*_unittest.py' | sort)

LINT_OPTIONS=--rcfile=bin/pylintrc \
	     --msg-template='{path}:{line}: {msg_id}: {msg}'

all: test lint

test:
	@export PYTHONPATH=$$PWD; \
	 for test in $(UNITTESTS); do \
	   echo Running $$test ...; $$test; \
	 done

lint:
	@pep8 $(LINT_FILES)
	@pylint $(LINT_OPTIONS) $(LINT_FILES)
