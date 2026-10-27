#!/usr/bin/env python3
"""Q3 reducer: per month, clients contacted, how many subscribed (y = yes) and the success rate."""
import sys

print("month\tcontacted\tsubscribed\tnot_subscribed\tsuccess_rate_%")
current, yes, no = None, 0, 0


def emit():
    print(f"{current[3:]}\t{yes + no}\t{yes}\t{no}\t{100 * yes / (yes + no):.1f}")


for line in sys.stdin:
    month, y = line.rstrip("\n").split("\t")
    if month != current:
        if current is not None:
            emit()
        current, yes, no = month, 0, 0
    if y == "yes":
        yes += 1
    else:
        no += 1
if current is not None:
    emit()
