# Notebooks

This directory contains Jupyter notebooks for exploratory analysis and reproducible examples. Keep a cleaned, non-output version of notebooks here and avoid committing large datasets and outputs. Use `nbstripout` or pre-commit hooks to remove outputs before committing.

## Example notebooks
- `01-data-merging-example.ipynb` — demonstrates recommended environment creation/registration, memory-safe data loads, hourly aggregation of `dataset/sampled_probe.csv`, and a merge with `dataset/synthetic_traffic_counts.csv`. Output-stripped and intended for reproducible examples.