#!/usr/bin/env python3
"""Convert the UCI Online Retail II Excel file (two yearly sheets) into one CSV
that the MapReduce jobs read.

    pip install openpyxl
    python3 scripts/convert_online_retail.py online_retail_II.xlsx data/online_retail.csv
"""
import csv
import datetime
import sys

import openpyxl

COLUMNS = ["Invoice", "StockCode", "Description", "Quantity",
           "InvoiceDate", "Price", "CustomerID", "Country"]


def main(src, dst):
    wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
    rows = 0
    with open(dst, "w", newline="", encoding="utf-8") as f:
        out = csv.writer(f)
        out.writerow(COLUMNS)
        for sheet in wb.worksheets:              # "Year 2009-2010", "Year 2010-2011"
            print("reading sheet", sheet.title, flush=True)
            it = sheet.iter_rows(values_only=True)
            next(it)                             # skip the sheet's header
            for inv, code, desc, qty, date, price, cust, country, *_ in it:
                if isinstance(date, datetime.datetime):
                    date = date.strftime("%Y-%m-%d %H:%M")
                if isinstance(cust, float):      # 13085.0 -> 13085
                    cust = int(cust)
                desc = str(desc if desc is not None else "").strip()
                out.writerow([inv, code, desc, qty, date, price,
                              "" if cust is None else cust, country])
                rows += 1
    print(f"wrote {rows} rows to {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
