---
name: data-analysis-clean
description: Use when the user wants to remove generated files (database, results, rendered outputs) to rebuild the pipeline from raw data and scripts.
---

# data-analysis-clean

Remove generated pipeline artifacts while preserving raw data, plans, scripts, and deliverable sources.

## Responsibility

- Delete `2_db/project.duckdb` and write-ahead logs.
- Delete `3_analyses/<name>/results.json` and `3_analyses/<name>/figures/`.
- Delete rendered outputs and intermediates in `4_output/<deliverable>/`.
- Preserve source files (`.qmd`, `export.py`, `run.py`, `build_db.py`, raw data, plans).

## How to use

1. Run the clean script to see what would be deleted using the project's Python:

   ```bash
   .venv/bin/python <path-to-skills>/data-analysis-clean/clean.py
   ```

2. If the list looks correct, run with `--yes`:

   ```bash
   .venv/bin/python <path-to-skills>/data-analysis-clean/clean.py --yes
   ```

## What is removed

- `2_db/project.duckdb`
- `2_db/*.wal`
- `3_analyses/*/results.json`
- `3_analyses/*/figures/`
- `4_output/<deliverable>/*.pdf`
- `4_output/<deliverable>/*.html`
- `4_output/<deliverable>/*.tex` (except `titlepage.tex`)
- `4_output/<deliverable>/*.log`
- `4_output/<deliverable>/*.csv`, `*.xlsx`
- `4_output/<deliverable>/export.json`
- `4_output/<deliverable>/*_files/` directories

## What is preserved

- `1_data/` (raw and transformed data)
- `0_plan/plan.md`
- `2_db/build_db.py`
- `3_analyses/*/run.py`
- `4_output/<deliverable>/*.qmd`
- `4_output/<deliverable>/export.py`
- `4_output/helpers.py`
- `.venv/`

## Rules

- Default to a dry run; require `--yes` for actual deletion.
- Never delete raw data files.
- Never delete `.venv/`.
