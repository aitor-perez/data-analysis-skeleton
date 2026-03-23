# Agent Instructions

This project uses a 5-stage pipeline. Data flows forward only.

```
0_plan  ->  1_data  ->  2_db  ->  3_analyses  ->  4_output
```

| Stage | Reads from | Produces | Format |
|-------|-----------|----------|--------|
| `0_plan/` | (nothing) | `plan.md`, `decisions.md` | Markdown |
| `1_data/` | External sources | raw data files, `sources.yaml` | CSV, JSON, XLSX, etc. |
| `2_db/` | `1_data/*` | `project.duckdb`, `schema.md` | DuckDB, Markdown |
| `3_analyses/` | `2_db/project.duckdb` | `results.json`, optional figures | JSON, PDF, PNG |
| `4_output/` | `3_analyses/*/results.json` | report, slides, dashboard, or export | Quarto, Python |

## General Rules

- Use Python. Prefer Pandas unless told otherwise.
- Keep scripts concise and flat. No `if __name__ == "__main__"`.
- Run `make status` at the start of work.
- Respect stage gates. Do not skip ahead if upstream files are incomplete.
- Put dependencies in `requirements.txt`.
- Put API keys in `.env` only. Use `python-dotenv`.
- Ask before making ambiguous data-cleaning or interpretation decisions.
- Avoid em dashes in reports, slides, and written output.

## Shared Utilities

- Reusable helpers live in `utils/`. See `utils/README.md`.
- Use `utils.rcp` for RCP calls instead of ad hoc `requests` code.
- Keep utilities generic. Keep dataset-specific logic in the calling script.
- Add the project root to `sys.path` from `__file__`, not from the current working directory.

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

From `3_analyses/<name>/run.py`, use:

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
```

## Stage Notes

### Stage 0: Plan

- Goal: define the project before collecting data or writing pipeline code.
- See `0_plan/README.md`.
- Keep `plan.md` current. Log non-trivial changes in `decisions.md`.

### Stage 1: Data Collection

- Goal: gather raw data and document provenance.
- See `1_data/README.md`.
- Every file in `1_data/` must be documented in `sources.yaml`.
- Confidential files must be added to both `.gitignore` and `.cursorignore`.

### Stage 2: Database

- Goal: transform raw data into a single DuckDB database.
- See `2_db/README.md`.
- Output is `2_db/project.duckdb`.
- Keep `2_db/schema.md` accurate. It is the contract for analyses.

### Stage 3: Analyses

- Goal: answer questions with SQL and structured JSON outputs.
- See `3_analyses/README.md`.
- Connect with `read_only=True` outside `2_db/`.
- Use one subfolder per analysis.
- If the schema changes, re-run affected analyses.

## Analysis JSON Contract

Every `results.json` must contain:

```json
{
  "query": "SELECT ...",
  "n_results": 10,
  "results": [],
  "description": "What this analysis does",
  "interpretation": "What the results mean",
  "figures": []
}
```

### Stage 4: Output

- Goal: create reports, slides, dashboards, or data exports.
- See `4_output/README.md`.
- Never hardcode numbers in `4_output/`. Load them from `3_analyses/*/results.json`.
- Each deliverable is a dated subfolder in `4_output/`.

Use the shared helpers from deliverable folders like this:

```python
import sys

sys.path.insert(0, "..")
from helpers import load_analysis, load_figure, load_value
```

## Make Commands

```bash
make status
make db
make analyses
make render d=<folder>
make outputs
make all
make clean
```