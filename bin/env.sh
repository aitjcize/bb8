#!/bin/bash

GITROOT=$(git rev-parse --show-toplevel)

if [ -e $GITROOT/.env ]; then
  source $GITROOT/.env/bin/activate
fi

export PATH=$GITROOT/bin:$PATH
export PYTHONPATH=$GITROOT

# Set python path
for p in apps/*/; do
    if [ -d $p ]; then
        export PYTHONPATH=$PYTHONPATH:`pwd`/$p
    fi
done

# Default configuration for CI
export MYSQL_PORT=3307
export REDIS_PORT=6379
export HTTP_PORT=7000
export BB8_HOSTNAME=dev.compose.ai

# Per-User port config for users testing on same machine
case $USER in
  deploy)
    export BB8_DEPLOY=true
    export HTTP_PORT=5000
    export BB8_HOSTNAME=bot.compose.ai
    ;;
  aitjcize)
    export MYSQL_PORT=3308
    export REDIS_PORT=6380
    export HTTP_PORT=7001
    ;;
  ychiaoli18)
    export MYSQL_PORT=3309
    export REDIS_PORT=6381
    export HTTP_PORT=7002
    ;;
esac

export DATABASE="mysql+pymysql://bb8:bb8test@127.0.0.1:$MYSQL_PORT/bb8?charset=utf8mb4"
