#!/usr/bin/env python3
"""Q4 reducer: average contact duration (seconds) per outcome of the previous campaign."""
import sys

print("poutcome\tclients\tavg_duration_sec\tavg_duration_min")
current, total, count = None, 0, 0


def emit():
    avg = total / count
    print(f"{current}\t{count}\t{avg:.1f}\t{avg / 60:.1f}")


for line in sys.stdin:
    poutcome, duration = line.rstrip("\n").split("\t")
    if poutcome != current:
        if current is not None:
            emit()
        current, total, count = poutcome, 0, 0
    total += int(duration)
    count += 1
if current is not None:
    emit()
