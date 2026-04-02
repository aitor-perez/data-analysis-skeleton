# Agent Instructions

This project uses a 5-stage pipeline.

Iteration is expected. Revisit earlier stages as needed when you learn more from the data. The constraint is on dependencies: data and code should flow forward through the pipeline, and downstream stages must not import from or write to upstream folders.

```
0_plan  ->  1_data  ->  2_db  ->  3_analyses  ->  4_output
```

| Stage | Reads from | Produces | Format |
|-------|-----------|----------|--------|
| `0_plan/` | (nothing) | `plan.md` | Markdown |
| `1_data/` | External sources | raw data files, `sources.yaml` | CSV, JSON, XLSX, etc. |
| `2_db/` | `1_data/*` | `project.duckdb`, `schema.md` | DuckDB, Markdown |
| `3_analyses/` | `2_db/project.duckdb` | `results.json`, optional figures | JSON, PDF, PNG |
| `4_output/` | `3_analyses/*/results.json` | report, slides, dashboard, or export | Quarto, Python |

## Rules

- Run `make status` at the start of work.
- Use Python. Prefer Pandas unless told otherwise.
- Keep scripts concise and flat. No `if __name__ == "__main__"`.
- Put dependencies in `requirements.txt`.
- Put API keys in `.env` only. Use `python-dotenv`.
- Ask before making ambiguous data-cleaning or interpretation decisions.
- Avoid em dashes in reports, slides, and written output.
- Reusable helpers live in `utils/`. Keep them generic.
- Use `utils.rcp` for RCP calls instead of ad hoc `requests` code.
- Add the project root to `sys.path` from `__file__`, not from the current working directory.
- Use a single DuckDB database at `2_db/project.duckdb`. Outside `2_db/`, connect with `read_only=True`.
- Confidential files must be added to both `.gitignore` and `.cursorignore`.

From scripts near the project root:

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

From `3_analyses/<name>/run.py`:

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
```

## Stages

- `0_plan/`: define scope and keep `plan.md` current. See `0_plan/README.md`.
- `1_data/`: collect raw data and document every source in `1_data/sources.yaml`. See `1_data/README.md`.
- `2_db/`: build `2_db/project.duckdb` and keep `2_db/schema.md` accurate. See `2_db/README.md`.
- `3_analyses/`: use one subfolder per analysis with `run.py`, `results.json`, and optional `figures/`. Re-run affected analyses after schema changes. See `3_analyses/README.md`.
- `4_output/`: never hardcode numbers. Load values from `3_analyses/*/results.json`. Keep each deliverable in a dated subfolder. Figures must use the same data as their parent analysis JSON, or a subset. See `4_output/README.md`.

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

From deliverable folders in `4_output/`, import shared helpers like this:

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