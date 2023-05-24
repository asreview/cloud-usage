#!/bin/bash

# Just checking that we are in the right place.
if [ "$PWD" != "/app/workdir" ];
then
  echo "ERROR: I don't know where I am"
  exit 1
fi

# Clean workdir. Ensures that we are always starting anew
rm -rf /app/workdir/*

# Copy files from the parent folder for the workdir.
cp ../*.sh ../*.py ./
cp -r ../data ./
cp ../custom_arfi.txt.template ./

# Create a logging function
function log {
  echo "[$0:$(date --iso=ns)] $1"
}

# Run makita
log "Running makita"

SETTINGS=""
# SETTINGS="-m nb -e tfidf"
asreview makita template arfi --template custom_arfi.txt.template -f jobs.sh
sed -i "s/SETTINGS_PLACEHOLDER/$SETTINGS/g" jobs.sh

# Split the `jobs.sh` file
log "Splitting file"
python split-file.py jobs.sh

# Run part 1 in the tasker pod
log "Running part 1"
bash jobs.sh.part1

# Send part 2, line by line, to the workers
log "Sending part 2 to rabbitmq"
python tasker-send.py jobs.sh.part2

# AFTER part 2 is done, send part 3, line by line, to the workers
log "Sending part 3 to rabbitmq"
python tasker-send.py jobs.sh.part3

log "Done"

# Send results someplace?
# TODO
