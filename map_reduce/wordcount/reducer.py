#!/usr/bin/env python3
"""Reducer: input arrives SORTED by key, so equal words are consecutive.
Sums the counts for each word and emits "word<TAB>total"."""
import sys

current_word, current_count = None, 0

for line in sys.stdin:
    word, count = line.rstrip("\n").split("\t", 1)
    count = int(count)
    if word == current_word:
        current_count += count
    else:
        if current_word is not None:
            print(f"{current_word}\t{current_count}")
        current_word, current_count = word, count

if current_word is not None:
    print(f"{current_word}\t{current_count}")
