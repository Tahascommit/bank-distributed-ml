#!/usr/bin/env python3
"""Q1 reducer: number of clients and average balance per job.
Hadoop sorts the mapper output by key, so all the lines of one job arrive together."""
import sys

print("job\tclients\tavg_balance")
current, total, count = None, 0, 0
for line in sys.stdin:
    job, balance = line.rstrip("\n").split("\t")
    if job != current:
        if current is not None:
            print(f"{current}\t{count}\t{total / count:.2f}")
        current, total, count = job, 0, 0
    total += int(balance)
    count += 1
if current is not None:
    print(f"{current}\t{count}\t{total / count:.2f}")
