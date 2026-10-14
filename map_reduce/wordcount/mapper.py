#!/usr/bin/env python3
"""Mapper: reads lines from stdin, emits "word<TAB>1" for every word."""
import sys
import re

for line in sys.stdin:
    for word in re.findall(r"[a-z0-9']+", line.lower()):
        print(f"{word}\t1")
