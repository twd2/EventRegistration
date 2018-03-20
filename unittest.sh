#!/bin/bash

pushd $(dirname $0) > /dev/null

. prepare.sh

python3 -m coverage run --omit=/usr/* -m unittest && python3 -m coverage html -d Coverage_Python

. shutdown.sh
