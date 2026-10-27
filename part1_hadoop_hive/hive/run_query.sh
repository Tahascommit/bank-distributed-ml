#!/bin/bash
# Runs one HiveQL file through beeline on hiveserver2 and prints the result.
#
#   usage (from the Mac):  docker exec hiveserver2 bash /project/part1_hadoop_hive/hive/run_query.sh queries/q01_total_clients.hql
cd /project/part1_hadoop_hive/hive
TERM=dumb beeline -u jdbc:hive2://localhost:10000/banking_data -n hive \
  --silent=true --showHeader=true --outputformat=table < "$1" 2>&1 \
  | grep -vE "SLF4J|jline|^\s+at |\.\.\. [0-9]+ more|NativeCodeLoader|^Caused by|^0: jdbc|^$"
