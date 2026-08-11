---
name: transform-data
description: Scaffold and run a heavy data transformation or enrichment.
---

# transform-data

Scaffold and run a data transformation or enrichment, such as LLM classification, extraction, or geocoding.

## Usage

```bash
# Scaffold the transformation script
python skills/transform-data/scripts/transform_data.py --create \
  --input 1_data/original/input.csv \
  --out-dir 1_data/transformed/classify

# Run the transformation
python skills/transform-data/scripts/transform_data.py \
  --input 1_data/original/input.csv \
  --out-dir 1_data/transformed/classify
```

## Inputs

- `--input`: one or more input files or directories. Repeat the flag for each path.
- `--out-dir`: directory where `run.py` and output files are written.
- `--create`: copy the `run.py` template into `--out-dir` and exit.

## Behavior

- With `--create`: copy `assets/run.py` into `--out-dir/run.py` only if it does not already exist. Substitute `__INPUT_PATHS__` and `__OUTPUT_DIR__` with absolute paths.
- Without `--create`: require `run.py` in `--out-dir`, run it, and validate that at least one output file was produced.
- Fail fast if any input path does not exist, or if no output files are produced.

## Generated script conventions

When editing `run.py`, keep `INPUT_PATHS` and `OUTPUT_DIR` relative to the script's own directory so the project stays portable if moved. For example:

```python
INPUT_PATHS = [Path(__file__).resolve().parent / ".." / "input.csv"]
OUTPUT_DIR = Path(__file__).resolve().parent
```

Avoid hardcoding absolute paths.

## When invoked by the skeleton

Use `0_plan/plan.md` to understand the required enrichment. Scaffold with `--create`, edit `1_data/transformed/<name>/run.py`, then run the skill without `--create`.

## When invoked standalone

Inspect the inputs, scaffold `run.py` with `--create`, edit it to implement the transformation, then run the skill without `--create`.
