#!/usr/bin/env python3
"""Q5 mapper: put every client in an age group and emit (age_group, balance)."""
import sys


def age_group(age):
    if age < 30:
        return "1) under 30"
    if age < 40:
        return "2) 30-39"
    if age < 50:
        return "3) 40-49"
    if age < 60:
        return "4) 50-59"
    return "5) 60 and over"


for line in sys.stdin:
    f = line.strip().split(",")
    if len(f) != 17 or f[0] == "age":
        continue
    print(f"{age_group(int(f[0]))}\t{f[5]}")
