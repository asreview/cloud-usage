#!/bin/bash

CONSTANT="template arfi" # Edit here to your liking
num_cores=$1

if [ -z "$num_cores" ]; then
  echo "ERROR: Missing number of cores"
  exit 1
fi

if [ ! -f makita-args.txt ]; then
  echo "ERROR: Create a file makita-args.txt before running this"
  exit 1
fi

while read -r arg
do
  # A overwrites all files
  echo "A" | asreview makita "$CONSTANT" "$arg"
  # Edit to your liking from here
  python3 split-file.py jobs.sh
  bash parallel_run.sh "$num_cores"
  mv output "output-args_$arg"
  # to here
done < makita-args.txt
