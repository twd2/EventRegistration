#!/bin/bash

pushd $(dirname $0) > /dev/null

. prepare.sh

npm run build

. shutdown.sh
