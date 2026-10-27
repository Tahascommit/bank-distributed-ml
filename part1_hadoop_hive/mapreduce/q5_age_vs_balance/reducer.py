#!/usr/bin/env python3
"""Q5 reducer: balance summary per age group (count, average, median, min, max, share with a negative balance)."""
import sys
from statistics import median

print("age_group\tclients\tavg_balance\tmedian_balance\tmin_balance\tmax_balance\tnegative_balance_%")
current, balances = None, []


def emit():
    n = len(balances)
    negative = sum(1 for b in balances if b < 0)
    print(f"{current[3:]}\t{n}\t{sum(balances) / n:.0f}\t{median(balances):.0f}\t"
          f"{min(balances)}\t{max(balances)}\t{100 * negative / n:.1f}")


for line in sys.stdin:
    group, balance = line.rstrip("\n").split("\t")
    if group != current:
        if current is not None:
            emit()
        current, balances = group, []
    balances.append(int(balance))
if current is not None:
    emit()
