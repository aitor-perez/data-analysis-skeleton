---
name: data-analysis-init
description: Use when starting a new data-analysis project in an empty or uninitalized directory.
---

# data-analysis-init

Bootstrap a new data-analysis project in the current directory.

## Responsibility

Create the minimal project scaffold and a local virtual environment. Stage-specific files are created by their respective stage skills.

## How to use

1. Run the init script from the directory you want to initialize:

   ```bash
   python <path-to-skills>/data-analysis-init/init.py
   ```

   To initialize a different directory:

   ```bash
   python <path-to-skills>/data-analysis-init/init.py --project-dir /path/to/project
   ```

2. Review the created files and report them to the user.
3. Suggest the user invoke `data-analysis` (the orchestrator) or `data-analysis-plan` next.

## What it creates

- Empty stage directories:
  - `0_plan/`
  - `1_data/original/`
  - `1_data/transformed/`
  - `2_db/`
  - `3_analyses/`
  - `4_output/`
- Cross-cutting files:
  - `utils/llm.py` and `utils/README.md`
  - `.env.example`
  - `.gitignore`
  - `README.md` (project-specific template)
- `.venv/` with catalog dependencies installed

## What it does NOT create

- `0_plan/plan.md` — created by `data-analysis-plan`
- `1_data/original/sources.yaml` — created by `data-analysis-collect`
- `2_db/build_db.py`, `2_db/project.duckdb`, `2_db/schema.md` — created by `data-analysis-build-db`
- `3_analyses/<name>/` — created by `data-analysis-analyze`
- `4_output/helpers.py`, `4_output/templates/`, deliverables — created by `data-analysis-output`

## Rules

- Skip any files or directories that already exist. Do not overwrite.
- Create `.venv/` only if it does not already exist.
- Install dependencies from the catalog's `requirements.txt` into `.venv/`.
- Do not create a project-level `requirements.txt` by default.
- Do not create `AGENTS.md`, `Makefile`, `SKELETON.md`, `status.py`, or `.cursor/`.
