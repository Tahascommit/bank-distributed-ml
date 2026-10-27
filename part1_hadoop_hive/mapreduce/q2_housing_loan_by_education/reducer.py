#!/usr/bin/env python3
"""Q2 reducer: per education level, count clients with and without a housing loan."""
import sys

print("education\twith_housing_loan\twithout_housing_loan\tshare_with_loan_%")
current, yes, no = None, 0, 0


def emit():
    print(f"{current}\t{yes}\t{no}\t{100 * yes / (yes + no):.1f}")


for line in sys.stdin:
    education, housing = line.rstrip("\n").split("\t")
    if education != current:
        if current is not None:
            emit()
        current, yes, no = education, 0, 0
    if housing == "yes":
        yes += 1
    else:
        no += 1
if current is not None:
    emit()
