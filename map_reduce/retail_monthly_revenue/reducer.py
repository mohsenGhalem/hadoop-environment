#!/usr/bin/env python3
"""Sum revenue per month. Same in/out format, so it doubles as the combiner."""
import sys
from itertools import groupby

pairs = (line.rstrip("\n").split("\t", 1) for line in sys.stdin)
for month, group in groupby(pairs, key=lambda kv: kv[0]):
    print(f"{month}\t{sum(float(v) for _, v in group):.2f}")
