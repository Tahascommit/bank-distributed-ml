#!/bin/bash
# Runs one MapReduce job (Hadoop Streaming with a Python mapper and reducer) on YARN
# and prints the result as a table.
#
#   usage (from the Mac):  docker exec namenode bash /project/part1_hadoop_hive/mapreduce/run_job.sh q1_avg_balance_by_job
set -e
JOB="$1"
DIR=/project/part1_hadoop_hive/mapreduce/$JOB
INPUT=/user/hive/bank/bank.csv
OUTPUT=/user/hive/output/$JOB
LOG=/tmp/$JOB.log

[ -f "$DIR/mapper.py" ] || { echo "no job called $JOB"; exit 1; }
hdfs dfs -rm -r -f -skipTrash "$OUTPUT" > /dev/null 2>&1

echo "running $JOB on YARN: $INPUT -> $OUTPUT"
mapred streaming \
  -D mapreduce.job.name="$JOB" \
  -D mapreduce.job.reduces=1 \
  -files "$DIR/mapper.py,$DIR/reducer.py" \
  -mapper "python3 mapper.py" \
  -reducer "python3 reducer.py" \
  -input "$INPUT" \
  -output "$OUTPUT" > "$LOG" 2>&1 || { tail -30 "$LOG"; exit 1; }

# the few lines of the job log that matter
grep -oE "Running job: \S+|map [0-9]+% reduce [0-9]+%|Job \S+ completed successfully|Map input records=[0-9]+|Reduce output records=[0-9]+" "$LOG"
echo
hdfs dfs -cat "$OUTPUT/part-00000" 2>/dev/null | python3 -c '
import sys
rows = [line.rstrip("\n").split("\t") for line in sys.stdin if line.strip()]
widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
for k, r in enumerate(rows):
    print("  ".join(v.ljust(w) for v, w in zip(r, widths)))
    if k == 0:
        print("  ".join("-" * w for w in widths))
'
