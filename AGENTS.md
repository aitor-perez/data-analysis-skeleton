# Agent Instructions

This project uses a 5-stage pipeline.

Iteration is expected. Revisit earlier stages as needed when you learn more from the data. The constraint is on dependencies: data and code should flow forward through the pipeline, and downstream stages must not import from or write to upstream folders.

```
0_plan  ->  1_data  ->  2_db  ->  3_analyses  ->  4_output
```

| Stage | Reads from | Produces | Format |
|-------|-----------|----------|--------|
| `0_plan/` | (nothing) | `plan.md` | Markdown |
| `1_data/original/` | External sources | raw data files, `sources.yaml` | CSV, JSON, XLSX, etc. |
| `1_data/transformed/<name>/` | `1_data/original/*` | script + enriched data | CSV, JSON, etc. |
| `2_db/` | `1_data/*` | `project.duckdb`, `schema.md` | DuckDB, Markdown |
| `3_analyses/` | `2_db/project.duckdb` | `results.json`, optional figures | JSON, PDF, PNG |
| `4_output/` | `3_analyses/*/results.json` | report, slides, dashboard, or export | Quarto, Python |

## Rules

- Run `make status` at the start of work.
- Use Python. Prefer Pandas unless told otherwise.
- Use a local `.venv/` at the repo root for Python work.
- Keep scripts concise and flat. No `if __name__ == "__main__"`.
- Put dependencies in `requirements.txt`.
- Keep `requirements.txt` clean and minimal. Only include dependencies the project actually uses.
- Put API keys in `.env` only. Use `python-dotenv`.
- Ask before making ambiguous data-cleaning or interpretation decisions.
- Avoid em dashes in reports, slides, and written output.
- Reusable helpers live in `utils/`. Keep them generic.
- Use `utils.llm` for LLM calls instead of ad hoc `requests` code. It supports any OpenAI-compatible provider (RCP, OpenAI). Use `call_llm()` for single structured calls, `call_llm_batch()` for parallel processing, and `get_embeddings()` for batch embedding extraction.
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

## Stage 0: Plan

Define the project scope before collecting data or writing pipeline code.

- `plan.md`: project scope, data sources, analyses, and outputs.
- Finish `plan.md` before moving to `1_data/`.
- Make sure the planned data and analyses are realistic before starting the pipeline.
- Done when `plan.md` has real content in every section and the project direction is clear.

## Stage 1: Data

Gather raw data and document its provenance.

Data lives in two subfolders:

- **`1_data/original/`** -- files collected from external sources, never modified after collection. `sources.yaml` here documents provenance for every collected file.
- **`1_data/transformed/`** -- one subfolder per transformation (e.g., `classify/`, `geocode/`). Each contains a script and its output. These are re-run only when needed, not on every pipeline rebuild.

```
1_data/
  original/
    sources.yaml
    survey_results.csv
  transformed/
    classify/
      classify.py
      survey_classified.csv
    geocode/
      geocode.py
      addresses_geocoded.csv
```

Rules:

- Never modify files in `original/` after collection. Lightweight cleaning (parsing, reshaping) happens in `2_db/`. Heavy enrichment that produces new data (LLM classification, OCR, geocoding) belongs in `transformed/`.
- Every collected file must have an entry in `original/sources.yaml`.
- Each transformation subfolder is self-contained: script + output + optional README.
- Transformation scripts that call an LLM should use `utils.llm` (`call_llm` or `call_llm_batch`). Define a Pydantic model for the expected output schema. For embedding tasks, use `get_embeddings()`.
- Optional fetch or download scripts for original data go in `original/`.
- If data is confidential, add it to both `.gitignore` and `.cursorignore`.
- If data is too large or remote, document how to obtain it and add a download script.
- Done when every planned source has a file or fetch script and a matching entry in `sources.yaml`.

## Stage 2: Database

Import data from `1_data/` into one clean DuckDB database.

- `build_db.py`: the script that imports data and structures it into tables.
- `project.duckdb`: the built database (rebuilt from scripts, not committed).
- `schema.md`: the database contract for analyses. Keep it accurate.
- This stage handles lightweight structural work: joining files, casting types, renaming columns, deduplication, filtering. Heavy enrichment (LLM, OCR, etc.) belongs in `1_data/transformed/`.
- Done when `build_db.py` runs cleanly and `schema.md` matches the actual database structure.

## Stage 3: Analyses

Answer analysis questions with SQL and structured JSON outputs.

- One subfolder per analysis, each containing `run.py`, `results.json`, and optional `figures/`.
- Connect to DuckDB with `read_only=True`.
- Run each script from its own subfolder: `cd 3_analyses/<name> && python run.py`.
- If the schema changes, re-run affected analyses.
- If an analysis is superseded, prefix it with `_deprecated_` instead of deleting it.

Every `run.py` should follow this structure:

```python
import sys, duckdb, json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

DB_PATH = Path("../../2_db/project.duckdb")
Path("figures").mkdir(exist_ok=True)
con = duckdb.connect(str(DB_PATH), read_only=True)

query = """
SELECT ...
"""
df = con.sql(query).df()

# Optional figure
fig, ax = plt.subplots(figsize=(8, 5))
# ... plot ...
fig.savefig("figures/chart.pdf", bbox_inches="tight")
plt.close()

output = {
    "query": query.strip(),
    "n_results": len(df),
    "results": df.to_dict(orient="records"),
    "description": "What this analysis does",
    "interpretation": "What the results mean",
    "figures": [{"file": "figures/chart.pdf", "caption": "What the figure shows"}],
}

with open("results.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"✓ {len(df)} results → results.json")
```

Every `results.json` must contain:

```json
{
  "query": "SELECT ...",
  "n_results": 10,
  "results": [{"col": "val", ...}, ...],
  "description": "What this analysis does",
  "interpretation": "What the results mean",
  "figures": [
    {"file": "figures/chart.pdf", "caption": "What the figure shows"}
  ]
}
```

- Figures must use the same data as the JSON, or a subset.
- Done when every planned analysis has a subfolder with a valid `results.json` and reviewed interpretation.

## Stage 4: Output

Create final deliverables from `3_analyses/*/results.json`.

- Dated deliverable folders such as `2026-02-18-short-report`.
- Quarto files for reports, slides, or dashboards.
- Optional export scripts and generated output files.
- Never hardcode numbers in deliverables. Load them from `3_analyses/*/results.json`.

From deliverable folders in `4_output/`, import shared helpers like this:

```python
import sys

sys.path.insert(0, "..")
from helpers import load_analysis, load_figure, load_value
```

- Render with `make render d=<folder>` or `make outputs`.
- Done when the deliverable renders successfully and all reported numbers come from analysis outputs.

## Utils

Reusable helpers live in `utils/`. Import them after adding the project root to `sys.path`.

- **`utils.llm`** -- Helpers for calling OpenAI-compatible LLM endpoints (RCP, OpenAI). Use `call_llm()` for a single structured call with retries and Pydantic validation, `call_llm_batch()` for parallel processing over a list of items, and `get_embeddings()` for batch embedding extraction. All functions accept a `provider` parameter (`"rcp"` or `"openai"`, defaults to `"rcp"`). See `utils/README.md` for usage examples.

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
