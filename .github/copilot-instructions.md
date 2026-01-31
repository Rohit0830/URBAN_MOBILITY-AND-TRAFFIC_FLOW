# GitHub Copilot / AI Agent Instructions for Urban Mobility & Traffic Flow 🔧

## Purpose
Provide concise, actionable guidance so an AI coding agent can be immediately productive in this repo: discover data layout, run experiments, and add reproducible analysis or examples without changing the project's goals (interpretable EDA and dashboard-ready metrics).

## Quick TL;DR ✅
- Primary work is data analysis (Python + Jupyter) and Power BI dashboards (external). See `README.md` for project objective.  
- Large raw data files live in `dataset/` but may not be checked in (e.g., `US_Accidents_March23.csv` is external). Use `dataset/DATASET_DESCRIPTION.md` for schemas and tips.  
- Use sampled subsets for quick experiments (`pd.read_csv(..., nrows=...)` or `sample()` a large file).

## Files & Key Locations 🔎
- `README.md`, `Idea.md`, `Research.md` — project goals, methodology, and scope.  
- `dataset/DATASET_DESCRIPTION.md` — canonical description of CSV schemas (use this for column names & parsing hints).  
- `notebooks/` — Jupyter notebooks; keep them cleaned of outputs (use `nbstripout`, pre-commit hook or `git` filter).

## Conventions & Project-Specific Patterns 🧭
- Focus on interpretable, reproducible EDA and metrics — avoid adding ML models or complex DAX unless explicitly requested.  
- Datasets can be large (US_Accidents ~2GB memory). Always prefer streaming/partial reads and explicit `usecols`, `dtype` downcasting, and `parse_dates` when loading.  
- Station-based analysis uses `station_id` + `timestamp` keys (see `synthetic_traffic_counts.csv` and `synthetic_probe_data.csv`). Aggregations are typically hourly or daily and then classified into `peak`/`off-peak` windows.

## Suggested code patterns (copy/paste-ready) 💡
- Memory-conscious CSV load:

```python
import pandas as pd
cols = ['ID','Start_Time','End_Time','Severity','Start_Lat','Start_Lng','City']
df = pd.read_csv('dataset/US_Accidents_March23.csv', usecols=cols,
                 parse_dates=['Start_Time','End_Time'],
                 dtype={'Severity':'int8'})
```

- Sampling & quick experiments:

```python
sample = pd.read_csv('dataset/synthetic_probe_data.csv', parse_dates=['timestamp'], nrows=200000)
# or
for chunk in pd.read_csv('dataset/US_Accidents_March23.csv', chunksize=500_000):
    process(chunk)
```

- Merge counts → probe → accidents by nearest `station_id` and aligned `timestamp` (hourly) for exposure modeling (see `DATASET_DESCRIPTION.md` for column names).

## Dev & Repro Workflows ⚙️
- Setup: `pip install -r requirements.txt` (runtime) and `pip install -r requirements-dev.txt` (dev tools).  
- Run notebooks: `jupyter lab` or `jupyter notebook` and use small sampled datasets for iteration.  
- Formatting & checks: run `black .`, `isort .`, `flake8`. Install pre-commit hooks via `pre-commit install` to auto-strip notebook outputs and format code.  
- Tests: minimal/no test suite currently; add small pytest-based tests around parsers/transformers for dataset read/save logic if you add code.

## What to change / Where to add examples ✍️
- Add a short example notebook: `notebooks/01-data-merging-example.ipynb` demonstrating a memory-friendly load, merge, and KPI calculation (peak hour share, per-station average speed). Keep cleared outputs in the repo.  
- Add a small sampled CSV (e.g., `dataset/sampled_probe.csv`) for CI and quick runs (document sampling method in `DATASET_DESCRIPTION.md`).

## Safety & Reproducibility Notes ⚠️
- Do not commit large raw datasets to the repo. Document external sources and download instructions in `dataset/README.md`.  
- When adding heavy computations, prefer adding scripts that output intermediate parquet files under `dataset/` and document expected memory/time.

## Acceptance Criteria for PRs by AI agents ✅
- New notebooks have outputs stripped and include a short README/description.  
- Any data-loading function uses explicit `usecols`, `parse_dates`, and documents memory footprint.  
- New data files are small (samples) and included only if they are <5 MB unless the maintainers approve larger test fixtures.

---
If anything here is unclear or you want more examples (example notebook or a sampled dataset), leave a short note in a PR or ask here so I can iterate. 🙋‍♂️
