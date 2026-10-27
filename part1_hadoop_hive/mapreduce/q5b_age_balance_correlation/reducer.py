#!/usr/bin/env python3
"""Q5b reducer: add up the partial sums of all mappers and compute Pearson's r between age and balance."""
import math
import sys

n = sx = sy = sxx = syy = sxy = 0
for line in sys.stdin:
    _, values = line.rstrip("\n").split("\t")
    a, b, c, d, e, g = map(int, values.split(","))
    n, sx, sy, sxx, syy, sxy = n + a, sx + b, sy + c, sxx + d, syy + e, sxy + g

r = (n * sxy - sx * sy) / math.sqrt((n * sxx - sx ** 2) * (n * syy - sy ** 2))
print("clients\tmean_age\tmean_balance\tpearson_r_age_balance")
print(f"{n}\t{sx / n:.1f}\t{sy / n:.1f}\t{r:.4f}")
