#!/usr/bin/env python3
"""Top-N products by units sold within each country (N=5)."""
import sys
from collections import Counter
from itertools import groupby

TOP_N = 5
rows = (line.rstrip("\n").split("\t") for line in sys.stdin)
for country, group in groupby(rows, key=lambda r: r[0]):
    units, names = Counter(), {}
    for _, code, desc, qty in group:
        units[code] += int(qty)
        names.setdefault(code, desc)
    for rank, (code, total) in enumerate(units.most_common(TOP_N), 1):
        print(f"{country}\t{rank}\t{code}\t{names[code]}\t{total}")
