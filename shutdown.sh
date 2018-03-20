#!/bin/bash

if pgrep mongod > /dev/null; then
  printf "\n****** Shutting down MongoDB... ******\n"
  pkill -INT mongod
  while pgrep mongod > /dev/null;
  do
    printf "."
    sleep 0.1
  done
  echo
fi
