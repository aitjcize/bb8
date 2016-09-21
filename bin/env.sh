#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
GITROOT=$(dirname $SCRIPT_DIR)

if [ -e $GITROOT/.env ]; then
  source $GITROOT/.env/bin/activate
fi

export PATH=$PWD/bin:$PWD/$SCRIPT_DIR:$PATH
export PYTHONPATH=$PWD/$GITROOT

# Default configuration for CI
export MYSQL_PORT=3307
export REDIS_PORT=6379

# Per-User port config for users testing on same machine
case $USER in
  deploy)
    export BB8_DEPLOY=true
    export HTTP_PORT=5000
    ;;
  aitjcize)
    export MYSQL_PORT=3307
    export REDIS_PORT=6380
    export HTTP_PORT=7000
    ;;
  kevin)
    export MYSQL_PORT=3308
    export REDIS_PORT=6381
    export HTTP_PORT=7001
    ;;
  ychiaoli18)
    export MYSQL_PORT=3307
    export REDIS_PORT=6380
    export HTTP_PORT=7000
    ;;
esac

export DATABASE="mysql+pymysql://bb8:bb8test@127.0.0.1:$MYSQL_PORT/bb8?charset=utf8mb4"
