---
name: data-analysis-transform
description: Use when the project needs heavy enrichment (LLM classification, extraction, OCR, geocoding, etc.) in 1_data/transformed/<name>/.
---

# data-analysis-transform

Create and run heavy data enrichment transformations in `1_data/transformed/<name>/`.

## Responsibility

- Scaffold a new transformation subfolder with a script template.
- Run a specific transformation.
- Validate that the transformation produced output files.

## How to use

### Scaffold a transformation

```bash
.venv/bin/python <path-to-skills>/data-analysis-transform/transform.py --create classify
```

This creates `1_data/transformed/classify/classify.py` from the template.

### Run a transformation

```bash
.venv/bin/python <path-to-skills>/data-analysis-transform/transform.py --name classify
```

This runs `1_data/transformed/classify/classify.py` from its own folder.

## Template

The template uses `utils.llm` (`call_llm_batch`) for structured LLM calls with Pydantic validation. It expects:

- An input file in `1_data/original/`.
- A Pydantic model defining the LLM output.
- A `save_result()` function writing one output file per input row.
- A final step combining outputs into a single CSV.

## Rules

- Each transformation is self-contained in its own `1_data/transformed/<name>/` folder.
- Read from `1_data/original/` or `1_data/transformed/`; never modify `1_data/original/`.
- Use `utils.llm` for LLM calls instead of ad hoc `requests` code.
- Define a Pydantic model for the expected LLM output.
- Run transformations only when needed, not on every pipeline rebuild.
