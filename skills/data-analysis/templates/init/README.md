# Project Name

Short description of this analysis project.

## Pipeline

```
0_plan -> 1_data -> 2_db -> 3_analyses -> 4_output
```

## Getting started

1. Fill in `0_plan/plan.md`.
2. Collect raw data in `1_data/original/` and document it in `1_data/original/sources.yaml`.
3. Build the database: `python 2_db/build_db.py`
4. Run analyses in `3_analyses/<name>/`.
5. Render deliverables in `4_output/`.

## Environment

Add API keys to `.env` if needed:

```bash
cp .env.example .env
```
