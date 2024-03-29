#!/bin/bash

GITROOT=$(git rev-parse --show-toplevel)

if [ -e $GITROOT/.env ]; then
  source $GITROOT/.env/bin/activate
fi

export PATH=$GITROOT/bin:$GITROOT/bb8/frontend/node_modules/.bin:$PATH
export PYTHONPATH=$GITROOT

# Set python path
for p in apps/*/; do
    if [ -d $p ]; then
        export PYTHONPATH=$PYTHONPATH:`pwd`/$p
    fi
done


DOCKER_HOST_IP=`ifconfig docker0 | grep 'inet addr:' | cut -d: -f2 | cut -f1 -d ' '`

# Default configuration for CI
export MYSQL_PORT=3307
export REDIS_HOST=$DOCKER_HOST_IP
export REDIS_PORT=6379
export HTTP_PORT=7000
export BB8_HOSTNAME="dev.compose.ai"
export BB8_RESOURCE_HOSTNAME="r-dev.compose.ai"
export BB8_SCOPE=$USER

# Per-User port config for users testing on same machine
case $USER in
  deploy)
    export BB8_DEPLOY=true
    export HTTP_PORT=5000
    export BB8_HOSTNAME="bot.compose.ai"
    export BB8_RESOURCE_HOSTNAME="r.compose.ai"
    export NODE_ENV='BB8_DEPLOY'
    # export REDIS_HOST=$(docker network inspect bb8_network | awk '/bb8.service.redis/,/},/ { if ($1 == "\"IPv4Address\":") { print substr($2, 2, index($2, "/") - 2) } }')
    # export DATABASE='mysql+pymysql://bb8deploy:bb8deploymysql@/bb8?unix_socket=/cloudsql/dotted-lexicon-133523:asia-east1:bb8&charset=utf8mb4'
    ;;
  aitjcize)
    export MYSQL_PORT=3308
    export REDIS_PORT=6380
    export HTTP_PORT=7001
    export APP_RPC_PORT=9999
    export WEBPACK_PORT=8080
    ;;
  ychiaoli18)
    export MYSQL_PORT=3309
    export REDIS_PORT=6381
    export HTTP_PORT=7002
    export APP_RPC_PORT=10000
    export WEBPACK_PORT=8081
    ;;
  yjlou)
    export MYSQL_PORT=3310
    export REDIS_PORT=6382
    export HTTP_PORT=7003
    export APP_RPC_PORT=10001
    export WEBPACK_PORT=8082
    ;;
  hans)
    export MYSQL_PORT=3311
    export REDIS_PORT=6383
    export HTTP_PORT=7004
    export APP_RPC_PORT=10002
    export WEBPACK_PORT=8083
    ;;
  amytseng)
    export MYSQL_PORT=3312
    export REDIS_PORT=6384
    export HTTP_PORT=7005
    export APP_RPC_PORT=10003
    export WEBPACK_PORT=8084
    ;;
  dev)
    export MYSQL_PORT=3313
    export REDIS_PORT=6385
    export HTTP_PORT=7006
    export APP_RPC_PORT=10004
    export WEBPACK_PORT=8085
    ;;
  lai)
    export MYSQL_PORT=3314
    export REDIS_PORT=6386
    export HTTP_PORT=7006
    export APP_RPC_PORT=10005
    export WEBPACK_PORT=8086
    ;;
  jsgame)
    export MYSQL_PORT=3315
    export REDIS_PORT=6387
    export HTTP_PORT=7007
    export APP_RPC_PORT=10006
    export WEBPACK_PORT=8087
    ;;
esac

export DATABASE="mysql+pymysql://bb8:bb8test@$DOCKER_HOST_IP:$MYSQL_PORT/bb8?charset=utf8mb4"
export REDIS_URI="redis://$REDIS_HOST:$REDIS_PORT"
