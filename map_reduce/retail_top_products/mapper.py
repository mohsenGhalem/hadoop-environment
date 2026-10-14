#!/usr/bin/env python3
"""Emit country<TAB>stockcode<TAB>description<TAB>quantity for real products only."""
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
    if is_valid_sale(inv, qty, price) and PRODUCT_CODE.match(code):
        print(f"{country}\t{code}\t{desc}\t{qty}")
