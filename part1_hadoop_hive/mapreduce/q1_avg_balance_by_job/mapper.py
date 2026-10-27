#!/usr/bin/env python3
"""Q1 mapper: emit (job, balance) for every client."""
import sys

for line in sys.stdin:
    f = line.strip().split(",")
    if len(f) != 17 or f[0] == "age":  # skip the header and broken lines
        continue
    print(f"{f[1]}\t{f[5]}")  # job, balance
