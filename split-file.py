#!/usr/bin/env python
import sys

if len(sys.argv) < 2:
    print("Please provide a file name as an argument.")
    exit()

file_name = sys.argv[1]

with open(file_name, "r", encoding="utf-8") as f:
    content = f.readlines()

# Find the index of the first occurrence of the word "simulate"
first_simulate_index = -1
last_simulate_index = len(content) - 1
for i, line in enumerate(content):
    if "simulate" in line:
        if first_simulate_index == -1:
            first_simulate_index = i
        last_simulate_index = i

if first_simulate_index == -1:
    print("The word 'simulate' was not found in the file.")
    exit()


def useless(line):
    return len(line.strip()) == 0 or line[0] == "#"


def assign_file(line, line_index):
    if useless(line):
        return 0

    if line_index < first_simulate_index:
        return 1
    elif line_index > last_simulate_index:
        return 3

    if any(s in line for s in ["mkdir", "describe"]):
        return 1
    elif "simulate" in line:
        return 2
    else:
        return 3


# Write each part to a separate file
for i in range(1, 4):
    with open(file_name + f".part{i}", "w", encoding="utf-8") as f:
        f.write(
            "".join(
                line
                for (line_index, line) in enumerate(content)
                if assign_file(line, line_index) == i
            )
        )
