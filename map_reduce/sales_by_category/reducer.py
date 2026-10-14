#!/usr/bin/env python3
"""For each category: number of sales, total, average, min, max."""
import sys
from itertools import groupby


def parse(stdin):
    for line in stdin:
        key, value = line.rstrip("\n").split("\t", 1)
        yield key, float(value)


for category, group in groupby(parse(sys.stdin), key=lambda kv: kv[0]):
    amounts = [v for _, v in group]
    n, total = len(amounts), sum(amounts)
    print(f"{category}\tcount={n}\ttotal={total:.2f}\tavg={total/n:.2f}"
          f"\tmin={min(amounts):.2f}\tmax={max(amounts):.2f}")
