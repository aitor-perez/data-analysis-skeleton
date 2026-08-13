---
name: run-analysis
description: Scaffold and run an analysis against a DuckDB database.
---

# run-analysis

Scaffold and run a single analysis against a DuckDB database.

## Usage

```bash
# Scaffold the analysis script
python skills/run-analysis/scripts/run_analysis.py --create --db-dir db --out-dir analyses/q1

# Run the analysis
python skills/run-analysis/scripts/run_analysis.py --db-dir db --out-dir analyses/q1
```

## Inputs

- `--db-dir`: directory containing exactly one `.duckdb` file and a `schema.md`.
- `--out-dir`: directory where `run.py` and `results.json` are written.
- `--create`: copy the `run.py` template into `--out-dir` and exit.

## Behavior

- With `--create`: copy `assets/run.py` into `--out-dir/run.py` only if it does not already exist. The template contains commented placeholders that you must edit before running.
- Without `--create`: require `run.py` in `--out-dir`, run it, and validate that `results.json` matches the expected schema.
- Fail fast with a clear error if `schema.md` is missing, if there is not exactly one `.duckdb` file, or if validation fails.

## Generated script conventions

When editing `run.py`, keep paths relative to the script's own directory so the project stays portable if moved. For example:

```python
DB_PATH = Path(__file__).resolve().parent / ".." / "data.duckdb"
```

Avoid hardcoding absolute paths.

## When invoked by the skeleton

Use `0_plan/plan.md` and `2_db/schema.md` to decide which question to answer. Scaffold with `--create`, edit `3_analyses/<name>/run.py`, then run the skill without `--create`.

## When invoked standalone

Inspect `schema.md`, scaffold `run.py` with `--create`, edit it to query the database, then run the skill without `--create`.
