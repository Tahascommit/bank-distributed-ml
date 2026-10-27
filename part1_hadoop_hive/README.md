# Part 1: Data Analysis and Management with Hadoop & Hive

A small Hadoop + Hive cluster runs in Docker on my laptop. It is all built from one image: the official `apache/hive:4.2.1` image, which already contains Hadoop 3.4.1. I added Python 3 (for MapReduce in Python), Java 11 (for the Hadoop daemons) and the HDFS web files the Hive image leaves out.

| Container | What it does | Web page |
|---|---|---|
| namenode | HDFS master, keeps the file system metadata | http://localhost:9870 |
| datanode | stores the HDFS blocks | |
| resourcemanager | YARN, schedules the MapReduce jobs | http://localhost:8088 |
| nodemanager | YARN worker, runs the map and reduce tasks | http://localhost:8042 |
| historyserver | history of finished MapReduce jobs | http://localhost:19888 |
| hiveserver2 | Hive SQL over the data in HDFS (embedded metastore) | http://localhost:10002 |

## Run it

```bash
cd part1_hadoop_hive
docker compose up -d

# data ingestion: local file -> HDFS
docker exec namenode hdfs dfs -mkdir -p /user/hive/bank
docker exec namenode hdfs dfs -put -f /project/data/bank.csv /user/hive/bank/

# a MapReduce job (Python mapper + reducer through Hadoop Streaming), result printed as a table
docker exec namenode bash /project/part1_hadoop_hive/mapreduce/run_job.sh q1_avg_balance_by_job

# hive: create the database and the table, load the data, then any query
docker exec namenode bash -c "hdfs dfs -mkdir -p /user/hive/bank/staging && hdfs dfs -cp -f /user/hive/bank/bank.csv /user/hive/bank/staging/"
docker exec hiveserver2 bash -c "beeline -u jdbc:hive2://localhost:10000/ -n hive < /project/part1_hadoop_hive/hive/01_create_and_load.hql"
docker exec hiveserver2 bash /project/part1_hadoop_hive/hive/run_query.sh queries/q12_poutcome_subscription_rate.hql
```

The repo folder is mounted at `/project` inside every container.

## Files

- `mapreduce/<job>/mapper.py` and `reducer.py`: one folder per MapReduce question
  - `q1_avg_balance_by_job`
  - `q2_housing_loan_by_education`
  - `q3_contacts_by_month`
  - `q4_duration_by_poutcome`
  - `q5_age_vs_balance`
  - `q5b_age_balance_correlation`
- `mapreduce/run_job.sh`: runs one job on YARN and prints the result
- `hive/01_create_and_load.hql`: database `banking_data`, table `client_info` and the data load
- `hive/queries/q01 ... q13`: one file per Hive question
- `hive/run_query.sh`: runs one query file through beeline
- `outputs/`: the result of every job and query
- `docker/`: the image and the Hadoop configuration

The answers with screenshots are in `docs/Part 1 - Data Analysis and Management using Hadoop & Hive.docx`.
