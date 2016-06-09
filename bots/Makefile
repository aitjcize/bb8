# Copyright 2016 bb8 Authors

BOTS_FILES=$(shell find -name '*.bot' -type f | sort)

all: validate

validate:
	@for bot in $(BOTS_FILES); do \
	   echo Validating $$bot ...; \
	   jsonschema -i $$bot schema.bot.json; \
	 done
