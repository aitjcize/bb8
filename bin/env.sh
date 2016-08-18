#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
GITROOT=$(dirname $SCRIPT_DIR)

if [ -e $GITROOT/.env ]; then
  source $GITROOT/.env/bin/activate
fi

export PATH=$PWD/$SCRIPT_DIR:$PATH
export PYTHONPATH=$PWD/$GITROOT

# Default configuration for CI
export PORT=3307

# Per-User port config for users testing on same machine
case $USER in
  aitjcize)
    export PORT=3307
    export HTTP_PORT=7000
    ;;
  kevin)
    export PORT=3308
    export HTTP_PORT=7001
    ;;
esac

export DATABASE="mysql+pymysql://bb8:bb8test@127.0.0.1:$PORT/bb8?charset=utf8mb4"
