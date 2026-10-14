#!/usr/bin/env python3
"""Per country: total revenue, number of orders (distinct invoices), average order value."""
import sys
from itertools import groupby

rows = (line.rstrip("\n").split("\t") for line in sys.stdin)
for country, group in groupby(rows, key=lambda r: r[0]):
    revenue, invoices, lines = 0.0, set(), 0
    for _, amount, inv in group:
        revenue += float(amount)
        invoices.add(inv)
        lines += 1
    orders = len(invoices)
    print(f"{country}\trevenue={revenue:.2f}\torders={orders}\tlines={lines}"
          f"\tavg_order={revenue / orders:.2f}")
