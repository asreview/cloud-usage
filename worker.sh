#!/bin/bash

if [ "$PWD" != "/app/workdir" ];
then
  echo "ERROR: I don't know where I am"
  exit 1
fi

python /app/worker-receiver.py
