# Part 5: Data Parallelism

`Data_Parallelism_Bank_Marketing.ipynb` shows how Spark splits the work over partitions, and measures what that changes. I ran it on my laptop (12 cores, Spark in local mode, one task per core).

| Section | What it does | Result |
|---|---|---|
| 1. Partitioning | compares the csv as read, round robin, hash on job and range on balance | the file is read as 1 partition. Hash on job leaves 5 of 12 partitions empty but saves a shuffle for groupBy("job") |
| 2. Parallel processing | average balance per job with groupBy and with an explicit mapPartitions + reduceByKey, then loans per age group | same averages both ways. On 4.5 million rows the Python version runs 4 times faster with 12 partitions than with 1 |
| 3. Parallel training | weighted logistic regression (gradients per partition, added up with treeAggregate) | AUC 0.893. On 1.1 million rows training is 3.5 times faster with 12 partitions |
| 4. Monitoring | a psutil thread for CPU and memory, Spark's REST API for stages and executors, Spark UI screenshots | 5 to 7 busy cores on average with 12 partitions against 1.4 with one. Memory never close to the limit |
| 5. Task scheduling | five preprocessing tasks run one after the other and from a thread pool, with FAIR pools and job groups | 3.1 s sequential, 1.8 s concurrent |

The timings change a little from run to run. `spark_ui_executors.png` and `spark_ui_stages.png` are the Spark UI screenshots taken by the notebook (needs playwright, skipped on Colab). The driver's log goes to `spark_driver.log`, which is not in the repo.
