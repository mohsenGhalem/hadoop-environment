#!/bin/bash
# Simulate a job locally (no Hadoop): cat | mapper | sort | [combiner] | reducer
# Works on your Mac or inside a container.
#   bash map_reduce/test_job.sh <job_name> <file in data/ | - for stdin>
#   LINES_SHOWN=all to print everything (default 30 lines)
set -eo pipefail
MR="$(cd "$(dirname "$0")" && pwd)"
JOB=$1; FILE=$2
[ -z "$JOB" ] || [ -z "$FILE" ] && { echo "usage: $0 <job_name> <input_file>"; exit 1; }
DATA="$MR/../data"; [ -d "$DATA" ] || DATA=/hadoop-data/input
DIR="$MR/$JOB"
[ -f "$DIR/mapper.py" ] || { echo "no mapper.py in $DIR"; exit 1; }

stage() { [ -f "$DIR/$1.py" ] && python3 "$DIR/$1.py" || cat; }
export LC_ALL=C   # same byte-wise sort order as Hadoop
if [ "$FILE" = "-" ]; then IN=/dev/stdin; else IN="$DATA/$FILE"; fi
show() { if [ "${LINES_SHOWN:-30}" = all ]; then cat; else head -${LINES_SHOWN:-30}; fi; }
cat "$IN" | python3 "$DIR/mapper.py" | sort -t$'\t' -k1,1 \
  | stage combiner | sort -t$'\t' -k1,1 | stage reducer | show
