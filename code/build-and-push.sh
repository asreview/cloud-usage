#!/bin/bash

YOURUSER=$1

if [ -z "$YOURUSER" ]; then
  echo "ERROR: Missing YOURUSER. Run 'bash build-and-push.sh YOURUSER'"
  exit 1
fi

for f in worker tasker
do
  if ! docker build -t "$YOURUSER/$f" -f $f.Dockerfile .; then
    echo "ERROR building docker image"
    exit 1
  fi
  if ! docker push "$YOURUSER/$f"; then
    echo "ERROR pushing docker image"
    exit 1
  fi
done
