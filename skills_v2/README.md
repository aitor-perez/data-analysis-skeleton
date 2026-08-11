# Data-analysis skeleton skills

Standalone skills for the data-analysis skeleton pipeline.

## Install

```bash
pip install -e .
```

API keys should be set in a `.env` file at the project root. Generated scripts use `python-dotenv` to load them.

## Skills

### `skeleton`

Bootstrap and report status for a data-analysis project.

```bash
python skills/skeleton/scripts/init.py
.venv/bin/python skills/skeleton/scripts/status.py
```

### `build-duckdb`

Scaffold and run a DuckDB database build from raw data.

```bash
python skills/build-duckdb/scripts/build_duckdb.py --create --data-dir data --out-dir db
python skills/build-duckdb/scripts/build_duckdb.py --data-dir data --out-dir db
```

### `run-analysis`

Scaffold and run an analysis against a DuckDB database.

```bash
python skills/run-analysis/scripts/run_analysis.py --create --db-dir db --out-dir analyses/q1
python skills/run-analysis/scripts/run_analysis.py --db-dir db --out-dir analyses/q1
```

### `transform-data`

Scaffold and run a data transformation or enrichment.

```bash
python skills/transform-data/scripts/transform_data.py --create --input data/input.csv --out-dir transformed/x
python skills/transform-data/scripts/transform_data.py --input data/input.csv --out-dir transformed/x
```

### `render-quarto`

Create and render Quarto deliverables from built-in templates.

```bash
python skills/render-quarto/scripts/render_quarto.py --create report --out-dir my_report
python skills/render-quarto/scripts/render_quarto.py --out-dir my_report
```

## Development notes

- Run generated scripts from their own directories.
- Keep paths inside generated scripts relative to the script file so projects stay portable.
- Heavy enrichment belongs in `transform-data`; lightweight joins and casts belong in `build-duckdb`.
