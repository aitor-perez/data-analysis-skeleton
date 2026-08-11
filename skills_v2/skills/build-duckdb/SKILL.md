---
name: build-duckdb
description: Build a DuckDB database from raw data files.
---

# build-duckdb

Build and validate a DuckDB database from raw data files.

## Usage

```bash
# Scaffold the build script
python skills/build-duckdb/scripts/build_duckdb.py --create --data-dir 1_data --out-dir 2_db

# Run the build
python skills/build-duckdb/scripts/build_duckdb.py --data-dir 1_data --out-dir 2_db
```

## Inputs

- `--data-dir`: directory containing raw data files.
- `--out-dir`: directory where `build_db.py`, the `.duckdb` database, and `schema.md` are written.
- `--create`: copy the `build_db.py` template into `--out-dir` and exit.

## Behavior

- With `--create`: copy `assets/build_db.py` into `--out-dir/build_db.py` only if it does not already exist. Substitute `__DATA_DIR__` with the absolute path of `--data-dir`.
- Without `--create`: require `build_db.py` in `--out-dir`, run it, and validate that exactly one `.duckdb` file and a non-empty `schema.md` were produced.
- Fail fast with a clear error if `build_db.py` is missing and `--create` was not passed, or if validation fails.

## Generated script conventions

When editing `build_db.py`, keep paths relative to the script's own directory so the project stays portable if moved. For example:

```python
DATA_DIR = Path(__file__).resolve().parent / "data"
```

Avoid hardcoding absolute paths.

## When invoked by the skeleton

Use `0_plan/plan.md` context to decide which files to load, how to clean/join them, and which derived tables to create. Scaffold with `--create`, edit `2_db/build_db.py`, then run the skill without `--create`.

## When invoked standalone

Inspect the files in `--data-dir`, scaffold `build_db.py` with `--create`, edit it to load the data, then run the skill without `--create`.
