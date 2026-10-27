#!/usr/bin/env python3
"""Q5b mapper: Pearson correlation in one pass. Every mapper sums its own rows
(n, x, y, x^2, y^2, xy) and emits only those 6 numbers, so very little data goes to the reducer."""
import sys

n = sx = sy = sxx = syy = sxy = 0
for line in sys.stdin:
    f = line.strip().split(",")
    if len(f) != 17 or f[0] == "age":
        continue
    x, y = int(f[0]), int(f[5])  # age, balance
    n += 1
    sx += x
    sy += y
    sxx += x * x
    syy += y * y
    sxy += x * y
print(f"sums\t{n},{sx},{sy},{sxx},{syy},{sxy}")
