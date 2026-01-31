#!/usr/bin/env python3
"""Chunked reservoir sampling from a large CSV to produce a fixed-size sampled CSV.

Usage:
    python tools/sample_probe.py --input dataset/synthetic_probe_data.csv --output dataset/sampled_probe.csv --n 100000 --seed 42
"""
import argparse
import csv
import random
import pandas as pd


def reservoir_sample_csv(input_path, output_path, n=100000, seed=42, chunksize=100_000):
    random.seed(seed)
    reservoir = []
    total_seen = 0
    cols = None

    for chunk in pd.read_csv(input_path, chunksize=chunksize):
        if cols is None:
            cols = list(chunk.columns)
        for _, row in chunk.iterrows():
            total_seen += 1
            if len(reservoir) < n:
                reservoir.append(row.tolist())
            else:
                s = random.randrange(total_seen)
                if s < n:
                    reservoir[s] = row.tolist()

    # write
    with open(output_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        writer.writerows(reservoir)

    print(f"Wrote {len(reservoir)} rows to {output_path} (seed={seed})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--n', type=int, default=100000)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    reservoir_sample_csv(args.input, args.output, n=args.n, seed=args.seed)
