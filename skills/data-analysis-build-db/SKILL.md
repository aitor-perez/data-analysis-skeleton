---
name: data-analysis-build-db
description: Use when 2_db/build_db.py needs to be created or run to produce 2_db/project.duckdb and 2_db/schema.md.
---

# data-analysis-build-db

Build the DuckDB database from raw data.

## Responsibility

- Copy `2_db/build_db.py` from the template if it does not exist.
- Run `2_db/build_db.py` to produce `2_db/project.duckdb` and `2_db/schema.md`.
- Validate that the database and schema were created.

## How to use

1. Run the build-db script from the project root using the project's Python:

   ```bash
   .venv/bin/python <path-to-skills>/data-analysis-build-db/build_db.py
   ```

2. Read the output.
   - If the template was just copied, tell the user to edit `2_db/build_db.py` to import their data.
   - If the build succeeded but the schema has no tables, tell the user to edit `2_db/build_db.py`.
   - If the build failed, report the error.
3. Help the user edit `2_db/build_db.py` as needed.
4. Re-run the skill until the database builds with tables.

## Python interpreter

The script uses `.venv/bin/python` if `.venv/` exists, otherwise `python3`.

## Rules

- Do not validate `sources.yaml`; that is `data-analysis-collect`'s job.
- Do not install extra Python packages. If `build_db.py` needs something not in the catalog's `requirements.txt`, add it there instead.
- Do not modify raw data files.
- Do not proceed to `data-analysis-analyze` until `schema.md` has tables.
