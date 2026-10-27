"""Part 4: real-time transaction analysis with Spark Structured Streaming.

One app, four tasks (one per question). Every task starts the producer in the background,
reads the stream of csv chunks, prints each micro batch as it is processed and stops when
the whole stream has been processed.

    python streaming_app.py --task aggregate          # Q1 running averages per job
    python streaming_app.py --task predict            # Q2 live predictions with the trained model
    python streaming_app.py --task window --size "10 seconds"   # Q3 tumbling windows
    python streaming_app.py --task window --size "1 minute"
    python streaming_app.py --task watermark          # Q4 late and out of order data
"""
import argparse
import shutil
import threading
import time

import pandas as pd
from pyspark.ml import PipelineModel
from pyspark.ml.functions import vector_to_array
from pyspark.sql import functions as F

from common import CHECKPOINT_DIR, INCOMING_DIR, LATE_ROWS_CSV, MODEL_DIR, STREAM_SCHEMA, get_spark
from producer import produce, reset_incoming

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)


def read_stream(spark):
    return (spark.readStream
            .schema(STREAM_SCHEMA)
            .option("header", True)
            .option("maxFilesPerTrigger", 1)   # one chunk per micro batch, so we can watch it build up
            .csv(str(INCOMING_DIR)))


def show(title, pdf):
    print(f"\n{title}")
    print(pdf.to_string(index=False) if len(pdf) else "(nothing yet)", flush=True)


# ---------- Q1: running aggregates per job ----------
def aggregate_task(spark):
    per_job = (read_stream(spark)
               .groupBy("job")
               .agg(F.count("*").alias("transactions"),
                    F.round(F.avg("balance"), 1).alias("avg_balance"),
                    F.round(F.avg("duration"), 1).alias("avg_duration_sec")))

    def on_batch(batch_df, batch_id):
        show(f"--- batch {batch_id}: averages per job so far ---", batch_df.orderBy("job").toPandas())

    # complete mode: every batch outputs the whole, updated result table
    return [per_job.writeStream.outputMode("complete").foreachBatch(on_batch)
            .option("checkpointLocation", str(CHECKPOINT_DIR / "aggregate")).start()]


# ---------- Q2: real-time predictions ----------
def predict_task(spark):
    model = PipelineModel.load(str(MODEL_DIR))
    scored = (model.transform(read_stream(spark))
              .withColumn("prob_yes", F.round(vector_to_array("probability")[1], 3))
              .withColumn("predicted", F.when(F.col("prediction") == 1, "yes").otherwise("no"))
              .select("txn_id", "age", "job", "balance", "duration", "poutcome", "prob_yes", "predicted", "y"))
    totals = {"rows": 0, "correct": 0, "yes": 0, "caught": 0}

    def on_batch(batch_df, batch_id):
        pdf = batch_df.toPandas()
        if pdf.empty:
            return
        correct = int((pdf.predicted == pdf.y).sum())
        totals["rows"] += len(pdf)
        totals["correct"] += correct
        totals["yes"] += int((pdf.y == "yes").sum())
        totals["caught"] += int(((pdf.y == "yes") & (pdf.predicted == "yes")).sum())
        show(f"--- batch {batch_id}: {len(pdf)} new transactions, first 8 with their prediction ---", pdf.head(8))
        print(f"batch accuracy {correct / len(pdf):.1%} | running accuracy {totals['correct'] / totals['rows']:.1%} "
              f"over {totals['rows']} rows | subscribers caught so far {totals['caught']}/{totals['yes']}", flush=True)

    return [scored.writeStream.outputMode("append").foreachBatch(on_batch)
            .option("checkpointLocation", str(CHECKPOINT_DIR / "predict")).start()]


# ---------- Q3: window operations ----------
def window_task(spark, size):
    windows = (read_stream(spark)
               .groupBy(F.window("event_time", size).alias("w"))
               .agg(F.count("*").alias("transactions"), F.round(F.avg("balance"), 1).alias("avg_balance"))
               .select(F.date_format("w.start", "HH:mm:ss").alias("window_start"),
                       F.date_format("w.end", "HH:mm:ss").alias("window_end"), "transactions", "avg_balance"))
    final = {}

    def on_batch(batch_df, batch_id):
        pdf = batch_df.orderBy("window_start").toPandas()
        for r in pdf.itertuples():
            final[r.window_start] = r
        show(f"--- batch {batch_id}: windows of {size} updated in this batch ---", pdf)

    query = (windows.writeStream.outputMode("update").foreachBatch(on_batch)
             .option("checkpointLocation", str(CHECKPOINT_DIR / f"window_{size.replace(' ', '_')}")).start())
    query.final_table = final
    return [query]


# ---------- Q4: watermarking ----------
def watermark_task(spark):
    stream = read_stream(spark)
    results = {"no watermark": {}, "watermark 1 minute": {}}

    def windowed(df):
        return (df.groupBy(F.window("event_time", "30 seconds").alias("w"))
                .agg(F.count("*").alias("transactions"), F.round(F.avg("balance"), 1).alias("avg_balance"))
                .select(F.date_format("w.start", "HH:mm:ss").alias("window_start"), "transactions", "avg_balance"))

    def collector(name):
        def on_batch(batch_df, batch_id):
            for r in batch_df.collect():
                results[name][r.window_start] = (r.transactions, r.avg_balance)
        return on_batch

    plain = (windowed(stream).writeStream.outputMode("update").foreachBatch(collector("no watermark"))
             .option("checkpointLocation", str(CHECKPOINT_DIR / "no_watermark")).start())
    # rows more than 1 minute older than the newest event time seen are dropped, and windows that
    # are older than that can be finalized and removed from the state
    marked = (windowed(stream.withWatermark("event_time", "1 minute")).writeStream.outputMode("update")
              .foreachBatch(collector("watermark 1 minute"))
              .option("checkpointLocation", str(CHECKPOINT_DIR / "watermark")).start())
    marked.results = results
    return [plain, marked]


def report_watermark(queries):
    plain, marked = queries
    results = marked.results
    table = pd.DataFrame({
        "window_start": sorted(results["no watermark"]),
    })
    table["count_no_watermark"] = table.window_start.map(lambda w: results["no watermark"][w][0])
    table["count_with_watermark"] = table.window_start.map(lambda w: results["watermark 1 minute"].get(w, (0,))[0])
    table["dropped"] = table.count_no_watermark - table.count_with_watermark
    show("=== final counts per 30 second window ===", table)
    dropped = sum(p["stateOperators"][0].get("numRowsDroppedByWatermark", 0) for p in marked.recentProgress if p["stateOperators"])
    late = pd.read_csv(LATE_ROWS_CSV)
    print(f"\nrows counted without watermark: {table.count_no_watermark.sum()}")
    print(f"rows counted with a 1 minute watermark: {table.count_with_watermark.sum()}")
    print(f"rows dropped by the watermark: {table.dropped.sum()}")
    print(f"rows I made very late on purpose: {(late.kind == 'very late').sum()}, "
          f"out of order but within 1 minute: {(late.kind == 'out of order').sum()} (these are still counted)")
    print(f"spark's own numRowsDroppedByWatermark metric: {dropped} (it counts after the partial aggregation "
          f"inside each batch, so two late rows of the same window in one batch count once)")
    state_plain = plain.lastProgress["stateOperators"][0]["numRowsTotal"]
    state_marked = marked.lastProgress["stateOperators"][0]["numRowsTotal"]
    print(f"windows kept in state at the end: {state_plain} without watermark, {state_marked} with watermark")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["aggregate", "predict", "window", "watermark"], required=True)
    parser.add_argument("--size", default="10 seconds", help="window size for --task window")
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between chunks")
    args = parser.parse_args()

    spark = get_spark(f"part4-{args.task}")
    shutil.rmtree(CHECKPOINT_DIR, ignore_errors=True)
    reset_incoming()

    if args.task == "aggregate":
        queries = aggregate_task(spark)
    elif args.task == "predict":
        queries = predict_task(spark)
    elif args.task == "window":
        queries = window_task(spark, args.size)
    else:
        queries = watermark_task(spark)

    # the producer runs next to the stream, like an external system sending transactions
    producer = threading.Thread(target=produce, args=(args.interval, True))
    producer.start()
    print(f"[producer] sending chunks every {args.interval} seconds", flush=True)
    producer.join()
    for q in queries:
        q.processAllAvailable()  # wait until every chunk has gone through
    time.sleep(1)

    if args.task == "window":
        show(f"=== final result: windows of {args.size} ===", pd.DataFrame(list(queries[0].final_table.values())).drop(columns="Index"))
    if args.task == "watermark":
        report_watermark(queries)
    for q in queries:
        q.stop()
    spark.stop()


if __name__ == "__main__":
    main()
