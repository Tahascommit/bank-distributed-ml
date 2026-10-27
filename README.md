# Distributed ML on Bank Marketing Data

My project on the bank marketing dataset (`data/bank.csv`): the phone campaigns of a Portuguese bank that sold term deposits. Each of the 4,521 rows is a client who was called, and `y` says if they subscribed (only 11.5% did). I worked through the data with Hadoop, Hive, Spark, Spark ML and Spark Streaming, to answer questions about the clients and to predict who will subscribe.

## The five parts

| Part | Tools | Folder | Deliverable |
|---|---|---|---|
| 1. Data analysis and management | Hadoop (HDFS, YARN, MapReduce in Python), Hive | [`part1_hadoop_hive/`](part1_hadoop_hive/) | [question doc with screenshots](docs/) |
| 2. Exploratory data analysis | PySpark DataFrames, Spark SQL | [`part2_spark_eda/`](part2_spark_eda/) | notebook |
| 3. Predictive modeling | Spark ML Pipeline, CrossValidator | [`part3_spark_ml/`](part3_spark_ml/) | notebook |
| 4. Real-time transaction analysis | Spark Structured Streaming | [`part4_streaming/`](part4_streaming/) | scripts, stream chunks, [question doc](docs/) |
| 5. Data parallelism | partitions, RDDs, Spark UI and REST API, FAIR scheduler | [`part5_parallelism/`](part5_parallelism/) | notebook |

Every folder has its own README with the commands to run that part.

## Main results

- **Part 1:** a 6-container Hadoop + Hive cluster in Docker. 6 MapReduce jobs (Python mapper and reducer through Hadoop Streaming) and 13 Hive queries. For example, retired clients have the highest average balance (2,319), and a success in the previous campaign gives a 64.3% subscription rate against 9.1% for new contacts.
- **Part 2:** no nulls or duplicates, but "unknown" is used as a missing value (82% of `poutcome`). The bank made 31% of its calls in May, the month with the lowest success rate (6.65%). Age has a U shape: 37.8% of the clients over 60 subscribed.
- **Part 3:** logistic regression, random forest and gradient boosted trees, all with class weights and tuned with 3-fold cross validation. `duration` is only known after the call, so the final model leaves it out. The final model is a logistic regression with AUC-ROC 0.744 and AUC-PR 0.337 (random would be 0.108). Calling only the 31% of clients it flags would still reach 60% of the subscribers.
- **Part 4:** a producer drops 31 chunks (904 transactions) into a folder that Spark watches. Running averages, a prediction for every transaction (83.4% accuracy), 10-second and 1-minute windows, and a 1-minute watermark that drops exactly the 13 very late rows.
- **Part 5:** hash partitioning on job is skewed (5 of 12 partitions empty) but saves a shuffle. An explicit map and reduce over partitions on 4.5 million rows runs 4 times faster with 12 partitions. Logistic regression trains 3.5 times faster on 1.1 million rows, and five preprocessing tasks run 1.7 times faster together with FAIR pools.

## Two things the data doesn't have

- **No year column:** the data only has day and month, so the "trend over time" questions are answered by month.
- **`loan` has no amount:** it is yes/no, so "age groups by loan amount" is answered with the number and the share of clients with a loan in each age group.

## Setup

Part 1 only needs Docker Desktop, see [its README](part1_hadoop_hive/README.md).

Parts 2 to 5 need Java 17 and Python 3.12:

```bash
brew install openjdk@17            # the code finds it there, otherwise set JAVA_HOME
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/jupyter notebook
```

The notebooks of parts 2, 3 and 5 also run on Google Colab. Their first cell installs Java and PySpark when they are missing and downloads `bank.csv` from this repo. Part 5 was run on my laptop with 12 cores. On Colab (2 cores) the code works, but the speedups are much smaller and the Spark UI screenshots are skipped.

## Layout

```
data/bank.csv                 the dataset
docs/                         question docs for parts 1 and 4, with the screenshots
part1_hadoop_hive/            docker cluster, mapreduce jobs, hive queries, outputs
part2_spark_eda/              eda notebook
part3_spark_ml/               modeling notebook and the saved pipeline model
part4_streaming/              streaming scripts, stream chunks, model, run logs
part5_parallelism/            data parallelism notebook and spark ui screenshots
```
