#!/bin/bash

pushd $(dirname $0) > /dev/null

ROLE_ROOT=0

. ersh.sh model.user set_role_by_username $1 $ROLE_ROOT
