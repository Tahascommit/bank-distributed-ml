"""Builds the simulated transaction stream from bank.csv.

- 80% of the clients become the historical data the model is trained on (historical_train.csv)
- the other 20% become the live stream, split into small csv chunks (chunks/chunk_001.csv, ...)
- every streamed row gets a txn_id and an event_time: 5 rows per second, starting at 10:00:00
- some rows are made late on purpose, to test watermarking:
    out of order: 6% of the rows are 10 to 40 seconds older than their neighbours
    very late:    1.5% of the rows (only after the first 2 minutes) are 150 to 200 seconds older
  the list of these rows is saved in late_rows.csv
"""
import numpy as np
import pandas as pd

from common import BANK_CSV, CHUNKS_DIR, HISTORICAL_CSV, LATE_ROWS_CSV

CHUNK_SIZE = 30
START = pd.Timestamp("2026-10-27 10:00:00")
ROWS_PER_SECOND = 5

bank = pd.read_csv(BANK_CSV)
stream = bank.sample(frac=0.2, random_state=42)
bank.drop(stream.index).to_csv(HISTORICAL_CSV, index=False)

stream = stream.reset_index(drop=True)
offset = pd.Series(np.arange(len(stream)) / ROWS_PER_SECOND)  # seconds after the start
rng = np.random.default_rng(7)

delay = pd.Series(0.0, index=stream.index)
kind = pd.Series("", index=stream.index)
out_of_order = rng.choice(stream.index, size=int(0.06 * len(stream)), replace=False)
delay[out_of_order] = rng.uniform(10, 40, size=len(out_of_order)).round(1)
kind[out_of_order] = "out of order"
candidates = stream.index[(offset >= 120) & (kind == "")]
very_late = rng.choice(candidates, size=int(0.015 * len(stream)), replace=False)
delay[very_late] = rng.uniform(150, 200, size=len(very_late)).round(1)
kind[very_late] = "very late"

event_time = START + pd.to_timedelta(offset - delay, unit="s")
stream.insert(0, "event_time", event_time.dt.strftime("%Y-%m-%d %H:%M:%S.%f").str[:-3])
stream.insert(0, "txn_id", range(1, len(stream) + 1))

CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
for old in CHUNKS_DIR.glob("*.csv"):
    old.unlink()
for i, start in enumerate(range(0, len(stream), CHUNK_SIZE), 1):
    stream.iloc[start:start + CHUNK_SIZE].to_csv(CHUNKS_DIR / f"chunk_{i:03d}.csv", index=False)

late = stream.loc[kind != "", ["txn_id", "event_time"]].assign(
    arrives_with_chunk=(stream.index[kind != ""] // CHUNK_SIZE) + 1,
    seconds_late=delay[kind != ""], kind=kind[kind != ""])
late.to_csv(LATE_ROWS_CSV, index=False)

print(f"historical (training) rows: {len(bank) - len(stream)}")
print(f"streamed rows: {len(stream)} in {i} chunks of up to {CHUNK_SIZE}")
print(f"event time from {stream.event_time.min()} to {stream.event_time.max()}")
print(f"late rows: {(kind == 'out of order').sum()} out of order, {(kind == 'very late').sum()} very late")
