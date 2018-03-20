#!/bin/bash

pushd $(dirname $0) > /dev/null

. prepare.sh > /dev/null

python3 -m er.$@

. shutdown.sh > /dev/null
