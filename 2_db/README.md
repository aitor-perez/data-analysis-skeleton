# Stage 2: Database

## Goal

Transform raw data from `1_data/` into one clean DuckDB database.

## What Goes Here

- `build_db.py`: the script that imports and transforms raw data
- `project.duckdb`: the built database
- `schema.md`: the database contract for analyses

## Rules

- Output is always a single file: `project.duckdb`.
- All cleaning and transformations happen here.
- `project.duckdb` is rebuilt from scripts, not committed.
- Keep `schema.md` accurate. `3_analyses/` depends on it.

## Done When

`build_db.py` runs cleanly and `schema.md` matches the actual database structure.
