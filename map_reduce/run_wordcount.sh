#!/bin/bash
# Kept for convenience — same as: run_job.sh wordcount <file>
exec bash /hadoop-data/map_reduce/run_job.sh wordcount "${1:-file.txt}"
