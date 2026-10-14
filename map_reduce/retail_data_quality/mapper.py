#!/usr/bin/env python3
"""Data-quality profile: classify every row, emit issue<TAB>1."""
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
    print("total_rows\t1")
    if inv.startswith("C"):
        print("cancelled_invoice\t1")
    if qty <= 0:
        print("non_positive_quantity\t1")
    if price <= 0:
        print("zero_or_negative_price\t1")
    if not cust:
        print("missing_customer_id\t1")
    if not PRODUCT_CODE.match(code):
        print("non_product_code\t1")
    if is_valid_sale(inv, qty, price):
        print("valid_sale\t1")
