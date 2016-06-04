#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
GITROOT=$(dirname $SCRIPT_DIR)

if [ -e $GITROOT/.env ]; then
  source $GITROOT/.env/bin/activate
fi

export PATH=$PWD/$SCRIPT_DIR:$PATH
export PYTHONPATH=$PWD/$GITROOT
