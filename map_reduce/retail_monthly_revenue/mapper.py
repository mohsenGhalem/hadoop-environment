#!/usr/bin/env python3
"""Emit YYYY-MM<TAB>revenue for every valid sale line."""
import sys
import csv
import re

PRODUCT_CODE = re.compile(r"^\d{5}")   # real products start with 5 digits; POST, M, DOT... are fees


def records(stdin):
    """Yield parsed rows of online_retail.csv; skips header and malformed lines."""
    for row in csv.reader(stdin):
        if len(row) != 8 or row[0] == "Invoice":
            continue
        inv, code, desc, qty, date, price, cust, country = row
        try:
            qty, price = int(float(qty)), float(price)
        except ValueError:
            continue
        yield inv, code, desc, qty, date, price, cust, country


def is_valid_sale(inv, qty, price):
    return not inv.startswith("C") and qty > 0 and price > 0


for inv, code, desc, qty, date, price, cust, country in records(sys.stdin):
    if is_valid_sale(inv, qty, price):
        print(f"{date[:7]}\t{qty * price:.2f}")
