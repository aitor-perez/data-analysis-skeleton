---
name: data-analysis-analyze
description: Use when 3_analyses/ needs a new analysis subfolder or existing analyses need to be run to produce results.json.
---

# data-analysis-analyze

Create and run analyses in `3_analyses/`.

## Responsibility

- Create new analysis subfolders from the `run.py` template.
- Run every `3_analyses/<name>/run.py`.
- Validate that each analysis produces a valid `results.json`.

## How to use

### Create a new analysis

```bash
.venv/bin/python <path-to-skills>/data-analysis-analyze/analyze.py --create <name>
```

This creates `3_analyses/<name>/run.py` from the template. The assistant should then help the user edit `run.py` to answer the planned question.

### Run all analyses

```bash
.venv/bin/python <path-to-skills>/data-analysis-analyze/analyze.py
```

This runs every `run.py` in `3_analyses/`, validates the resulting `results.json`, and reports any failures.

## Workflow

1. Read `0_plan/plan.md` and identify planned analyses.
2. Compare with existing `3_analyses/<name>/` subfolders.
3. For each missing analysis, ask the user for a short name and confirm the question.
4. Run `analyze.py --create <name>` to scaffold the subfolder.
5. Help the user edit each new `run.py`.
6. Run `analyze.py` to execute all analyses.
7. If any analysis fails or produces invalid `results.json`, fix it and re-run.

## `results.json` schema

Every `results.json` must contain:

```json
{
  "query": "SELECT ...",
  "n_results": 10,
  "results": [{"col": "val"}],
  "description": "What this analysis does",
  "interpretation": "What the results mean",
  "figures": [{"file": "figures/chart.pdf", "caption": "..."}]
}
```

## Rules

- One subfolder per analysis question.
- Connect to DuckDB with `read_only=True`.
- Run each `run.py` from its own subfolder.
- Figures must use the same data as the JSON, or a subset.
- If an analysis is superseded, rename its folder with `_deprecated_` prefix instead of deleting it.
