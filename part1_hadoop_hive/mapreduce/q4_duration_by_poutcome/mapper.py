#!/usr/bin/env python3
"""Q4 mapper: emit (poutcome, duration) for every client."""
import sys

for line in sys.stdin:
    f = line.strip().split(",")
    if len(f) != 17 or f[0] == "age":
        continue
    print(f"{f[15]}\t{f[11]}")  # poutcome, duration in seconds
