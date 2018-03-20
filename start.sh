#!/bin/bash

pushd $(dirname $0) > /dev/null

. prepare.sh

echo Arguments: $@
python3 -m er.server $@

. shutdown.sh
