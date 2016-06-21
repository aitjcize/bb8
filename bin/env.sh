#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
GITROOT=$(dirname $SCRIPT_DIR)

if [ -e $GITROOT/.env ]; then
  source $GITROOT/.env/bin/activate
fi

export PATH=$PWD/$SCRIPT_DIR:$PATH
export PYTHONPATH=$PWD/$GITROOT

export DATABASE=mysql+pymysql://bb8:bb8test@127.0.0.1:3307/bb8?charset=utf8mb4
