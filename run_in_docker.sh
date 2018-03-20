#!/bin/bash

pushd $(dirname $0) > /dev/null

DOCKER_IMAGE=mfmfmf/env
VOLUME_DIR=/data/er
VOLUME_MONGODB_DIR=/data/mongodb
DIR=`pwd`

mkdir -p ./data/mongodb
chmod 777 ./data # FIXME(twd2): right permissions
chmod 777 ./data/mongodb # FIXME(twd2): right permissions

if [ ! "$1" ]; then
  docker run -it \
    -v $DIR:$VOLUME_DIR \
    -v $DIR/data/mongodb:$VOLUME_MONGODB_DIR \
    --network=host $DOCKER_IMAGE \
    bash
else
  docker run -it \
    -v $DIR:$VOLUME_DIR \
    -v $DIR/data/mongodb:$VOLUME_MONGODB_DIR \
    --network=host $DOCKER_IMAGE \
    bash $VOLUME_DIR/$@
fi
