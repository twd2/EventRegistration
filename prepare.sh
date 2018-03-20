#!/bin/bash

if ! mongo < /dev/null > /dev/null 2>&1; then
  printf "\n****** Starting MongoDB... ******\n"
  su -s `which bash` -c 'mongod -f /etc/mongod.conf' mongodb &
  printf "\n****** Waiting for MongoDB... ******\n"
  while ! mongo < /dev/null > /dev/null 2>&1;
  do
    printf "."
    sleep 0.1
  done
  echo
else
  printf "\n****** MongoDB is already running. :) ******\n\n"
fi
