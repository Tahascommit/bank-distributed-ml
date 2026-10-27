"""Simulates the live feed: drops one chunk of transactions into stream_data/incoming every few seconds.

Spark's file source picks up every new file in that folder. Each chunk is written under a temporary
name and then renamed, so Spark never sees a half written file.

    python producer.py --interval 2
"""
import argparse
import shutil
import time

from common import CHUNKS_DIR, INCOMING_DIR


def reset_incoming():
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    for f in INCOMING_DIR.iterdir():
        f.unlink()


def produce(interval, quiet=False):
    chunks = sorted(CHUNKS_DIR.glob("chunk_*.csv"))
    for chunk in chunks:
        tmp = INCOMING_DIR / f".{chunk.name}.tmp"
        shutil.copy(chunk, tmp)
        tmp.rename(INCOMING_DIR / chunk.name)
        if not quiet:
            print(f"[producer] sent {chunk.name}", flush=True)
        time.sleep(interval)
    return len(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=float, default=2.0, help="seconds between chunks")
    args = parser.parse_args()
    reset_incoming()
    print(f"[producer] sent all {produce(args.interval)} chunks")
