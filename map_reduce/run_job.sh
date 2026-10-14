#!/bin/bash
# Run a job on the Hadoop cluster. Call from your Mac:
#   docker exec -it namenode bash /hadoop-data/map_reduce/run_job.sh <job_name> <file in data/> [reducers]
#
# - <file> may also be a folder inside data/ (all files in it are used)
# - <file> = hdfs:/some/path reads a previous job's output (job chaining)
# - combiner.py is used automatically if it exists in the job folder
# - if there is no reducer.py, the job is map-only
# - SPLIT_MB=16 ... sets input split size (default 32 MB) = how many map tasks run
set -e
JOB=$1; FILE=$2; REDUCERS=${3:-1}
[ -z "$JOB" ] || [ -z "$FILE" ] && { echo "usage: $0 <job_name> <input_file> [num_reducers]"; exit 1; }
MR=/hadoop-data/map_reduce
DIR=$MR/$JOB
HDFS_IN=/user/root/input/$FILE
HDFS_OUT=/user/root/output/$JOB

[ -f "$DIR/mapper.py" ] || { echo "no mapper.py in $DIR"; exit 1; }

if [[ "$FILE" == hdfs:* ]]; then
  HDFS_IN=${FILE#hdfs:}          # chain jobs: read a previous job's output
  echo ">> Using HDFS input $HDFS_IN"
elif hdfs dfs -test -e "$HDFS_IN" && [ "${REUPLOAD:-0}" != 1 ]; then
  echo ">> data/$FILE already in HDFS ($HDFS_IN) — set REUPLOAD=1 to replace it"
else
  echo ">> Uploading data/$FILE to HDFS $HDFS_IN"
  hdfs dfs -mkdir -p "$(dirname $HDFS_IN)"
  hdfs dfs -rm -r -f -skipTrash "$HDFS_IN" >/dev/null
  hdfs dfs -put "/hadoop-data/input/$FILE" "$HDFS_IN"
fi
hdfs dfs -rm -r -f -skipTrash "$HDFS_OUT" >/dev/null

FILES="$DIR/mapper.py"
ARGS=(-mapper "python3 mapper.py")
if [ -f "$DIR/combiner.py" ]; then
  FILES="$FILES,$DIR/combiner.py"; ARGS+=(-combiner "python3 combiner.py")
fi
if [ -f "$DIR/reducer.py" ]; then
  FILES="$FILES,$DIR/reducer.py"; ARGS+=(-reducer "python3 reducer.py" -numReduceTasks "$REDUCERS")
else
  ARGS+=(-numReduceTasks 0)
fi
# extra files (lookup tables, helper modules) placed in the job folder
for f in "$DIR"/*; do
  case "$(basename "$f")" in mapper.py|combiner.py|reducer.py|__pycache__) ;; *) FILES="$FILES,$f";; esac
done

echo ">> Running job '$JOB'"
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -D mapreduce.job.name="$JOB" \
  -D mapreduce.input.fileinputformat.split.maxsize=$(( ${SPLIT_MB:-32} * 1024 * 1024 )) \
  -files "$FILES" "${ARGS[@]}" \
  -input "$HDFS_IN" -output "$HDFS_OUT"

echo ">> Result (first 30 lines) — full output: hdfs dfs -cat $HDFS_OUT/part-*"
hdfs dfs -cat "$HDFS_OUT/part-*" | head -30
