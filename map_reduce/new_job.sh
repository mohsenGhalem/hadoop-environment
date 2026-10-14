#!/bin/bash
# Create a new MapReduce job from the template.
#   bash map_reduce/new_job.sh my_job
set -e
MR="$(cd "$(dirname "$0")" && pwd)"
NAME=$1
[ -z "$NAME" ] && { echo "usage: $0 <job_name>"; exit 1; }
[ -e "$MR/$NAME" ] && { echo "job '$NAME' already exists"; exit 1; }
cp -r "$MR/_template" "$MR/$NAME"
chmod +x "$MR/$NAME"/*.py
echo "Created $MR/$NAME — edit mapper.py and reducer.py, then:"
echo "  bash map_reduce/test_job.sh $NAME <file in data/>"
