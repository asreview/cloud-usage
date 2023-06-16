#!/bin/bash
# Record the start time
start_time=$(date +%s)

num_cores=$1
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
