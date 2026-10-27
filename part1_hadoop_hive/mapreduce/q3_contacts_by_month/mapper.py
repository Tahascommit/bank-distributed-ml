#!/usr/bin/env python3
"""Q3 mapper: emit (month, y) for every client.
The month number is put in front of the name (05-may) so Hadoop sorts the months in calendar order."""
import sys

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

for line in sys.stdin:
    f = line.strip().split(",")
    if len(f) != 17 or f[0] == "age":
        continue
    month, y = f[10], f[16]
    print(f"{MONTHS.index(month) + 1:02d}-{month}\t{y}")
