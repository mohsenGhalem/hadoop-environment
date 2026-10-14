#!/usr/bin/env python3
"""Input: CSV lines  date,category,product,amount  (first line is a header).
Emits category<TAB>amount."""
import sys
import csv

for row in csv.reader(sys.stdin):
    if not row or row[0] == "date":      # skip header / blank lines
        continue
    try:
        category, amount = row[1].strip(), float(row[3])
    except (IndexError, ValueError):     # skip malformed rows
        continue
    print(f"{category}\t{amount}")
