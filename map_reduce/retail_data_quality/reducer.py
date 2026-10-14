#!/usr/bin/env python3
"""Sum counts per key. Output format == input format, so it is also used as the combiner."""
import sys
from itertools import groupby

pairs = (line.rstrip("\n").split("\t", 1) for line in sys.stdin)
for key, group in groupby(pairs, key=lambda kv: kv[0]):
    print(f"{key}\t{sum(int(v) for _, v in group)}")
