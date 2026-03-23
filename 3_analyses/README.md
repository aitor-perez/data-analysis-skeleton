# Stage 3: Analyses

## Goal

Answer analysis questions with SQL and structured JSON outputs.

## What Goes Here

- One subfolder per analysis
- `run.py` in each analysis folder
- `results.json` in each analysis folder
- Optional `figures/` folder with outputs based on the same data

## Rules

Every `results.json` must have this structure:

```json
{
  "query": "SELECT ...",
  "n_results": 10,
  "results": [{"col": "val", ...}, ...],
  "description": "What this analysis does (English)",
  "interpretation": "What the results mean (English)",
  "figures": [
    {"file": "figures/chart.pdf", "caption": "What the figure shows"}
  ]
}
```

- Connect to DuckDB with `read_only=True`.
- Run each script from its own subfolder.
- Figures must use the same data as the JSON, or a subset.
- If the schema changes, re-run affected analyses.
- If an analysis is superseded, prefix it with `_deprecated_` instead of deleting it.

See `example_analysis/` for a minimal template.

## Done When

Every planned analysis has a subfolder with a valid `results.json` and reviewed interpretation.
