-- Hive part: database, table and data load
-- default, day and month are reserved words in Hive, so they are quoted with backticks

CREATE DATABASE IF NOT EXISTS banking_data;
USE banking_data;

DROP TABLE IF EXISTS client_info;

CREATE TABLE client_info (
  age         INT,
  job         STRING,
  marital     STRING,
  education   STRING,
  `default`   STRING,
  balance     INT,
  housing     STRING,
  loan        STRING,
  contact     STRING,
  `day`       INT,
  `month`     STRING,
  duration    INT,
  campaign    INT,
  pdays       INT,
  previous    INT,
  poutcome    STRING,
  y           STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count" = "1");

-- LOAD DATA INPATH moves the file from its HDFS folder into the table's folder
LOAD DATA INPATH '/user/hive/bank/staging/bank.csv' INTO TABLE client_info;

DESCRIBE client_info;
