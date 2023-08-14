#!/bin/bash

function usage {
  echo "Usage:"
  echo ""
  echo "Generate your jobs.sh file, obtain split-file.py and run"
  echo ""
  echo "    python3 split-file.py jobs.sh"
  echo "    bash parallel_run.sh NUMBER_OF_CORES"
}

# Record the start time
start_time=$(date +%s)

num_cores=$1

if [ -z "$num_cores" ]; then
  echo "ERROR: Missing number of cores"
  usage
  exit 1
fi
for i in 1 2 3
do
  if [ ! -f "jobs.sh.part$i" ]; then
    echo "ERROR: File jobs.sh.part$i not found. Did you run split-file.py?"
    usage
    exit 1
  fi
done

# Utilize the GNU package for parallelization
bash jobs.sh.part1
parallel -j "$num_cores" < jobs.sh.part2
parallel -j "$num_cores" < jobs.sh.part3

# Record the end time
end_time=$(date +%s)

# Calculate the runtime
runtime=$((end_time - start_time))

# Print the runtime
echo "Job completed"
echo "Script runtime: $runtime seconds"
