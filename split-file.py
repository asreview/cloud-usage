#!/usr/bin/env python
import sys

if len(sys.argv) < 2:
    print("Please provide a file name as an argument.")
    exit()

file_name = sys.argv[1]

with open(file_name, 'r') as f:
    content = f.readlines()

# Find the index of the first occurrence of the word "simulate"
simulate_index = -1
for i, line in enumerate(content):
    if "simulate" in line:
        simulate_index = i
        break

if simulate_index == -1:
    print("The word 'simulate' was not found in the file.")
    exit()

# Split the content into three parts
part1 = "".join(line for line in content[:simulate_index])
part2 = "".join(line for line in content[simulate_index:] if "simulate" in line)
part3 = "".join(line for line in content[simulate_index:] if "simulate" not in line)

# Write each part to a separate file
with open(file_name + ".part1", 'w') as f:
    f.write(part1)

with open(file_name + ".part2", 'w') as f:
    f.write(part2)

with open(file_name + ".part3", 'w') as f:
    f.write(part3)
