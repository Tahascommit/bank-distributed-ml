#!/usr/bin/env python3
"""Q2 mapper: emit (education, housing) for every client, housing is yes or no."""
import sys

for line in sys.stdin:
    f = line.strip().split(",")
    if len(f) != 17 or f[0] == "age":
        continue
    print(f"{f[3]}\t{f[6]}")  # education, housing
