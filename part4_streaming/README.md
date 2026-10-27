# Part 4: Real-Time Transaction Analysis with Spark Streaming

Spark Structured Streaming (Spark 3.5, local mode) on a simulated stream of bank transactions.

## How the stream is simulated

- `make_stream_chunks.py` splits `bank.csv`:
  - 80% of the clients go to `stream_data/historical_train.csv`, used to train the model.
  - the other 20% (904 rows) become the live transactions, saved as 31 csv files in `stream_data/chunks/`.
  - every row gets a `txn_id` and an `event_time` (5 transactions per second from 10:00:00).
  - 54 rows are made out of order (10 to 40 s old) and 13 very late (150 to 200 s old), listed in `stream_data/late_rows.csv`.
- `producer.py` drops one chunk every few seconds into `stream_data/incoming/`, the folder Spark watches.

## Run it

```bash
python make_stream_chunks.py      # only needed once, the chunks are already in the repo
python train_model.py             # trains and saves the model to model/

python streaming_app.py --task aggregate                    # Q1 running averages per job
python streaming_app.py --task predict                      # Q2 a prediction for every transaction
python streaming_app.py --task window --size "10 seconds"   # Q3 windows
python streaming_app.py --task window --size "1 minute"
python streaming_app.py --task watermark                    # Q4 late data with and without a watermark
```

- **Producer:** every task starts the producer itself. `--interval` sets the seconds between chunks (default 2).
- **Spark UI:** while a task runs it is at http://localhost:4050, under the Structured Streaming tab.

## Results

| Task | Result |
|---|---|
| Predictions | 83.4% accuracy on the 904 streamed clients, and 81 of the 97 subscribers flagged. The model is a weighted logistic regression, AUC 0.881 on historical test data. |
| Watermark (1 minute) | dropped exactly the 13 very late rows (904 counted without it, 891 with it). All 54 out-of-order rows are still counted. |

The logs of every run are in `outputs/`. The answers with screenshots are in `docs/Part 4 - Real-Time Transaction Analysis.docx`.
