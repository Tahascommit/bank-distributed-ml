# Part 2: Exploratory Data Analysis with Spark

`Spark_EDA_Bank_Marketing.ipynb` follows the EDA template. All the processing runs in PySpark: loading, schema checks, summaries, filters, new columns, group bys, a UDF, string functions, correlation and Spark SQL. Only small aggregated results go to pandas, for the 23 charts.

What I found:

- No nulls and no duplicate rows, but "unknown" stands for a missing value, mostly in `poutcome` (82%) and `contact` (29%). I kept it as its own category.
- 11.5% of the clients subscribed, so the target is imbalanced.
- A success in the previous campaign gives a 64.3% subscription rate, against 9.1% for clients contacted for the first time.
- 31% of the calls were made in May, the month with the lowest success rate (6.65%). March, October and December converted over 40% of far fewer calls.
- Age has a U shape: 15.4% under 30, 10.2% from 30 to 60, 37.8% over 60.
- The balance is very skewed (median 444, maximum 71,188), and its correlation with age is only 0.084.

Run it locally with `jupyter notebook` (see the setup in the main README) or open it on Colab. The first cell sets up Spark on Colab by itself.
