#!/usr/bin/env python3
"""MAPPER — runs on every input line, in parallel across the cluster.

Input : raw lines of your file on stdin (one record per line).
Output: lines of the form  key<TAB>value  on stdout.

Hadoop then SORTS all mapper output by key and sends every line with the
same key to the same reducer.
"""
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    # TODO: parse the record and decide what to group by (key) and what to
    #       aggregate (value). You may emit 0, 1 or many pairs per line.
    key = line
    value = 1

    print(f"{key}\t{value}")
