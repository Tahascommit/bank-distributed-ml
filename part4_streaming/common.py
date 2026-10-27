"""Paths, the stream schema and the Spark session used by all Part 4 scripts."""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK_CSV = HERE.parent / "data" / "bank.csv"
STREAM_DIR = HERE / "stream_data"
CHUNKS_DIR = STREAM_DIR / "chunks"            # the prepared stream, one small csv per chunk
INCOMING_DIR = STREAM_DIR / "incoming"        # the folder Spark watches, the producer drops chunks here
HISTORICAL_CSV = STREAM_DIR / "historical_train.csv"
LATE_ROWS_CSV = STREAM_DIR / "late_rows.csv"
MODEL_DIR = HERE / "model"
CHECKPOINT_DIR = HERE / "checkpoints"

# spark needs java; use the homebrew java 17 on my mac if JAVA_HOME isn't set
JAVA17 = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
if "JAVA_HOME" not in os.environ and os.path.isdir(JAVA17):
    os.environ["JAVA_HOME"] = JAVA17
# spark's python workers must use the same python as this script (the mac's default python3 is 3.9)
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

from pyspark.sql import SparkSession  # noqa: E402
from pyspark.sql.types import IntegerType, StringType, StructField, StructType, TimestampType  # noqa: E402

# a streaming source needs the schema up front (no inferSchema on streams)
STREAM_SCHEMA = StructType([
    StructField("txn_id", IntegerType()),
    StructField("event_time", TimestampType()),
    StructField("age", IntegerType()),
    StructField("job", StringType()),
    StructField("marital", StringType()),
    StructField("education", StringType()),
    StructField("default", StringType()),
    StructField("balance", IntegerType()),
    StructField("housing", StringType()),
    StructField("loan", StringType()),
    StructField("contact", StringType()),
    StructField("day", IntegerType()),
    StructField("month", StringType()),
    StructField("duration", IntegerType()),
    StructField("campaign", IntegerType()),
    StructField("pdays", IntegerType()),
    StructField("previous", IntegerType()),
    StructField("poutcome", StringType()),
    StructField("y", StringType()),
])


def get_spark(app_name):
    spark = (SparkSession.builder
             .master("local[4]")
             .appName(app_name)
             # the default of 200 shuffle partitions is far too many for small micro batches
             .config("spark.sql.shuffle.partitions", "4")
             .config("spark.ui.showConsoleProgress", "false")
             # fixed port for the spark web ui (http://localhost:4050), so it doesn't clash with notebooks
             .config("spark.ui.port", "4050")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark
