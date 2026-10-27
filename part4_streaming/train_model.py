"""Trains the model used for the real-time predictions (Part 4, question 2).

Trained only on the historical 80% of the clients (historical_train.csv), so the streamed clients
are new to the model. Saves the whole pipeline (feature steps + classifier) to model/, so the
streaming app can apply exactly the same steps to every incoming row.
"""
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.feature import OneHotEncoder, StandardScaler, StringIndexer, VectorAssembler
from pyspark.sql import functions as F

from common import HISTORICAL_CSV, MODEL_DIR, get_spark

CATEGORICAL = ["job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome"]
NUMERIC = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]

spark = get_spark("part4-train-model")
df = spark.read.csv(str(HISTORICAL_CSV), header=True, inferSchema=True)

# only 11.5% of clients subscribe, so "yes" rows get a bigger weight (balanced class weights)
yes_share = df.filter(F.col("y") == "yes").count() / df.count()
df = df.withColumn("class_weight", F.when(F.col("y") == "yes", 0.5 / yes_share).otherwise(0.5 / (1 - yes_share)))

stages = [
    StringIndexer(inputCols=CATEGORICAL, outputCols=[c + "_idx" for c in CATEGORICAL], handleInvalid="keep"),
    OneHotEncoder(inputCols=[c + "_idx" for c in CATEGORICAL], outputCols=[c + "_vec" for c in CATEGORICAL]),
    StringIndexer(inputCol="y", outputCol="label", stringOrderType="alphabetAsc"),  # no -> 0, yes -> 1
    VectorAssembler(inputCols=NUMERIC + [c + "_vec" for c in CATEGORICAL], outputCol="raw_features"),
    StandardScaler(inputCol="raw_features", outputCol="features"),
    # logistic regression scored best on the historical data (AUC 0.88, better than random forest and
    # gradient boosted trees on this small dataset) and it is very cheap to apply to every incoming row
    LogisticRegression(featuresCol="features", labelCol="label", weightCol="class_weight", maxIter=100),
]

train, test = df.randomSplit([0.8, 0.2], seed=42)
model = Pipeline(stages=stages).fit(train)
pred = model.transform(test)

auc = BinaryClassificationEvaluator(metricName="areaUnderROC").evaluate(pred)
acc = MulticlassClassificationEvaluator(metricName="accuracy").evaluate(pred)
tp = pred.filter("label = 1 AND prediction = 1").count()
recall = tp / max(pred.filter("label = 1").count(), 1)
precision = tp / max(pred.filter("prediction = 1").count(), 1)
print(f"trained on {train.count()} rows, tested on {test.count()}")
print(f"test AUC {auc:.3f}  accuracy {acc:.3f}  precision(yes) {precision:.3f}  recall(yes) {recall:.3f}")

# refit on all the historical rows and save
final = Pipeline(stages=stages).fit(df)
final.write().overwrite().save(str(MODEL_DIR))
print(f"model saved to {MODEL_DIR}")
spark.stop()
