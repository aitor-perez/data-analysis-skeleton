# Data Analysis Skeleton

A ready-to-use project template for data analysis work. Clone it, fill in your data, and let the pipeline handle the rest.

## Why use this?

Most analysis projects start the same way: collect some data, wrangle it, run queries, make charts, write a report. Without structure, this quickly turns into a tangle of notebooks, stale CSVs, and copy-pasted numbers.

This skeleton solves that by separating the work into five stages with a clear rule: **data and code flow forward, never backward**.

```
0_plan  ->  1_data  ->  2_db  ->  3_analyses  ->  4_output
```

Each stage reads from the one before it and writes to its own folder. That means:

- **Nothing is wired together by accident.** If you change the raw data, you rebuild the database, re-run the analyses, and re-render the output. The Makefile does this in one command.
- **Raw data stays raw.** Original files live in `1_data/original/` and are never modified. Heavy enrichment (LLM calls, OCR) goes to `1_data/transformed/`, while lightweight cleaning happens in `2_db/`. You can always go back to the originals.
- **Numbers in reports are never hardcoded.** Deliverables in `4_output/` pull their values from `3_analyses/*/results.json`, so the output always matches the analysis.
- **Each analysis is self-contained.** One folder, one script, one JSON output. Easy to review, easy to re-run, easy to deprecate if the question changes.
- **AI agents can follow the rules too.** The pipeline conventions are documented in [AGENTS.md](AGENTS.md), which AI coding assistants read automatically. They will follow the same structure you do.

## What goes where

| Folder | Purpose | Key files |
|--------|---------|-----------|
| `0_plan/` | Define what you are doing and why | `plan.md` |
| `1_data/original/` | Raw data files, untouched after collection | CSVs, JSONs, `sources.yaml` |
| `1_data/transformed/` | One subfolder per enrichment step (LLM, OCR, etc.) | `<name>/script.py` + output files |
| `2_db/` | Clean and transform data into a single database | `build_db.py`, `project.duckdb`, `schema.md` |
| `3_analyses/` | One subfolder per analysis question | `<name>/run.py`, `<name>/results.json` |
| `4_output/` | Final deliverables (reports, slides, dashboards, exports) | Quarto files, `helpers.py` |
| `utils/` | Shared Python helpers (e.g., API clients) | `rcp.py` |

## Getting started

```bash
# 1. Create a virtual environment and install dependencies
make venv

# 2. Set up API keys (if needed)
cp .env.example .env       # then fill in your keys

# 3. Check the pipeline status
make status
```

From there, work through the stages in order: write your plan, collect data, build the database, run analyses, and create outputs. See [AGENTS.md](AGENTS.md) for detailed per-stage instructions.

## Make commands

| Command | What it does |
|---------|-------------|
| `make venv` | Create `.venv/` and install dependencies |
| `make status` | Show pipeline progress and validation |
| `make db` | Build the DuckDB database from `1_data/` |
| `make analyses` | Run every `run.py` in `3_analyses/` |
| `make render d=<folder>` | Render one deliverable in `4_output/` |
| `make outputs` | Render all deliverables |
| `make all` | Full pipeline: db, analyses, outputs |
| `make clean` | Remove all generated files |

## Prerequisites

- Python 3.10+
- [Quarto](https://quarto.org/docs/get-started/) (for rendering reports, slides, and dashboards)
- LuaLaTeX (e.g., TeX Live or MacTeX) if rendering PDF output
