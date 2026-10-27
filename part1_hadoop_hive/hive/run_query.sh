#!/bin/bash
# Runs one HiveQL file through beeline on hiveserver2 and prints the result.
#
#   usage (from the Mac):  docker exec hiveserver2 bash /project/part1_hadoop_hive/hive/run_query.sh queries/q01_total_clients.hql
#   an optional second argument changes the output format, e.g. csv2 for wide results
cd /project/part1_hadoop_hive/hive
TERM=dumb beeline -u jdbc:hive2://localhost:10000/banking_data -n hive \
  --hiveconf hive.resultset.use.unique.column.names=false \
  --silent=true --showHeader=true --outputformat=${2:-table} < "$1" 2>&1 \
  | sed -E 's/(0: jdbc:hive2:[^>]*> ?)+//' \
  | grep -vE "SLF4J|jline|^\s+at |\.\.\. [0-9]+ more|NativeCodeLoader|^Caused by|^$"
