# Part 3: Predictive Modeling with Spark ML

`Spark_ML_Bank_Marketing.ipynb` follows the ML template and predicts `y` (term deposit subscription) with Spark ML.

- **Features:** "unknown" kept as a category, `pdays` split into a flag and a cleaned value, outliers capped at the 1st and 99th percentiles of the training set, log1p on the skewed counts. StringIndexer, OneHotEncoder and VectorAssembler sit in one Pipeline with the model. `default` (chi-square p = 0.93) and `day` are dropped.
- **duration:** only known after the call, so it can't be used to decide who to call. With it the models reach an AUC-ROC of about 0.89, without it about 0.74. The final model leaves it out.
- **Models:** logistic regression, random forest and gradient boosted trees, with class weights for the imbalance, tuned with ParamGridBuilder and a 3-fold CrossValidator on the area under the PR curve.
- **Final model:** the tuned logistic regression. Test AUC-ROC 0.744, AUC-PR 0.337 (random would be 0.108). If the bank only called the 31% of clients the model flags, it would still reach 60% of the subscribers.

The final PipelineModel is saved in `model/` and reloaded at the end of the notebook. `log4j2-errors-only.properties` keeps Spark's log output down to errors.
