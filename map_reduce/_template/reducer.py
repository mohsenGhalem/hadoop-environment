#!/usr/bin/env python3
"""REDUCER — receives mapper output SORTED by key.

All lines with the same key arrive one after another, so we can process
one key at a time with itertools.groupby.

Output: whatever you print becomes the final result (usually key<TAB>result).
"""
import sys
from itertools import groupby


def parse(stdin):
    for line in stdin:
        key, value = line.rstrip("\n").split("\t", 1)
        yield key, value


for key, group in groupby(parse(sys.stdin), key=lambda kv: kv[0]):
    values = [v for _, v in group]

    # TODO: combine all values for this key
    result = sum(int(v) for v in values)

    print(f"{key}\t{result}")
