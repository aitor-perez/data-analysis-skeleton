# Skill Refactor Design

Goal: separate the current `data-analysis` skills catalog into a single
skeleton-aware orchestrator skill and several generic, reusable skills.

## Design principles

- **Standalone skills are explicit.** Every input is a CLI argument. There are no
  skeleton-specific defaults inside generic skills.
- **The orchestrator is ergonomic.** It knows the `0_plan -> 1_data -> 2_db ->
  3_analyses -> 4_output` skeleton and converts those conventions into explicit
  arguments for the standalone skills.
- **Skills are narrow and reusable.** Each skill does one thing and can be
  invoked directly or summoned by the orchestrator.
- **Built-in templates are fixed.** When a skill uses a template, the template is
  part of the skill's contract and is not user-customizable. This keeps outputs
  predictable.
- **Agent interaction is suggest-and-confirm.** Skills should propose content,
  structure, or next steps, and let the user approve or edit. They should not ask
  open-ended "what do you want?" questions unless there is no other way.

## What stays in the orchestrator

The orchestrator (`skeleton`) keeps skeleton-specific responsibilities:

- Initialize a new project (`init.py`): create directories, generate scaffold
  files (`.env.example`, `.gitignore`) only if they do not already exist, create
  `.venv`, and install the catalog Python package in editable mode so generated
  scripts can import `data_analysis_skills`.
- Report pipeline state (`status.py`).
- Decide the next pipeline step and invoke the appropriate standalone skill with
  skeleton-specific paths.
- Clean generated artifacts (`clean.py`).
- Skeleton-specific report constraints: when invoking `render-quarto`, wire the
  `.qmd` to import `data_analysis_skills.helpers` and load values and figures
  from `3_analyses/*/results.json`, and ensure no numbers are hardcoded.
- Data collection and provenance: document raw files in `1_data/original/` using
  `document_sources.py`, invoked by the orchestrator with skeleton-specific paths.
- Planning: a two-step, conversational process to fill `0_plan/plan.md` using
  the checklist in `skeleton/SKILL.md`.

### Data collection and provenance

Collection is skeleton-specific because it targets the `1_data/original/`
directory and the `sources.yaml` format. The implementation lives in the
orchestrator as `skeleton/document_sources.py`, but it is written like a
standalone skill: all inputs are CLI arguments and no skeleton paths are
hard-coded inside it.

```bash
skeleton/document_sources.py --input-dir 1_data/original --output 1_data/original/sources.yaml
```

This keeps the orchestrator thin and makes it easy to promote
`document_sources.py` to a standalone `document-sources` skill later if desired.

### Planning workflow

Planning is a skeleton-specific responsibility. The interaction is not a
mechanical, question-by-question fill. Instead:

1. **Exploration**: The agent has a free-form conversation with the user to
   understand the project's goal, data, audience, risks, and desired outputs.
2. **Proposal**: The agent writes a structured `0_plan/plan.md` covering all
   sections from the planning checklist in `skeleton/SKILL.md`.
3. **Review**: The user edits the proposal. The agent refines until the plan is
   complete.

The checklist in `skeleton/SKILL.md` acts as an output checklist, not as an
interview script.

## Standalone skills

### 1. `render-quarto`

Create and render Quarto deliverables from built-in templates.

The skill owns generic deliverable templates (`.qmd`, `.tex`, `.css`, images)
and guidance for populating them. It is agnostic of the data-analysis skeleton
and can be invoked in any project.

```bash
render-quarto --type report --out-dir my_report
render-quarto --type report-brief --out-dir 4_output/2026-08-06-brief
render-quarto --input my_report/report.qmd --to pdf
```

Inputs:
- `--type`: template to use (`report`, `report-brief`, `slides`, `dashboard`).
- `--out-dir`: directory where the deliverable folder is created.
- `--input` (optional): path to an existing `.qmd` file to render directly.
- `--to` (optional, with `--input`): output format (`pdf`, `html`, ...).

Behavior when using `--type`:
- Copy the chosen template into `--out-dir`.
- Propose a structure (chapters, sections, appendices) based on the template
  rules and any available context.
- Work with the user to fill the `.qmd` files.
- Render when the user confirms.

Behavior when using `--input`:
- Render the existing `.qmd` file to the requested format.

Templates and guidance:
- Templates live in `render-quarto/assets/`.
- General guidance applies to all templates (e.g., propose a chapter split and
  ask for confirmation).
- Type-specific guidance applies to one template (e.g., label appendices A, B,
  C and reference them in a regular chapter; create one `.qmd` per chapter).
- The templates contain no analysis-specific logic. When the skeleton
  orchestrator invokes this skill, it combines the generic templates with
  `data_analysis_skills.helpers` and enforces skeleton-specific report
  constraints.

Outputs:
- `out-dir/*.qmd` and supporting files.
- Rendered `.pdf` or `.html` files after user confirmation.

### 2. `build-duckdb`

Build and validate a DuckDB database from raw data files.

```bash
build-duckdb --script 2_db/build_db.py --db-dir 2_db
```

Inputs:
- `--script`: path to the Python script that builds the database.
- `--db-dir`: directory where the database and schema live.
- `--no-schema-doc` (optional): skip generating `schema.md`.

Behavior:
- Copy the built-in `build_db.py` template from `build-duckdb/assets/` into
  `--db-dir` only if `--script` does not already exist. Never overwrite an
  existing build script.
- The assistant generates the database build logic from the available data
  files and `plan.md`.
- Run the generated script automatically.
- Find the single `.duckdb` file in `--db-dir`.
- Validate the database exists and has tables.
- Generate or update `schema.md` in `--db-dir` by default.

Outputs:
- `<db-dir>/<name>.duckdb`
- `<db-dir>/schema.md` (unless `--no-schema-doc` is passed)

### 3. `run-analysis`

Scaffold and run an analysis from instructions against a DuckDB database.

```bash
run-analysis \
  --db-dir 2_db \
  --instructions instructions.md \
  --out-dir 3_analyses/q1
```

Inputs:
- `--db-dir`: directory containing exactly one `.duckdb` file and a `schema.md`.
- `--instructions`: path to a markdown file describing the analysis.
- `--out-dir`: directory where `run.py`, `results.json`, and `figures/` are
  written.

Behavior:
- Copy the built-in `run.py` template from `run-analysis/assets/` into
  `--out-dir` only if `run.py` does not already exist. Never overwrite an
  existing `run.py`.
- The assistant uses the inferred database path, `schema.md`, and
  `instructions.md` to help the user write the analysis code inside the template.
- Once the user confirms, run `run.py`.
- Validate `results.json` against the standard schema.

Outputs:
- `out-dir/run.py`
- `out-dir/results.json`
- `out-dir/figures/*`

Output schema (unchanged from current skeleton):
- `query`
- `n_results`
- `results`
- `description`
- `interpretation`
- `figures`

### 4. `transform-data`

Scaffold and run a data transformation from instructions.

```bash
transform-data \
  --input path/to/file1.csv \
  --input path/to/file2.json \
  --input path/to/pdfs/ \
  --instructions instructions.md \
  --out-dir 1_data/transformed/classify
```

Inputs:
- `--input`: one or more input files and/or directories. Repeat the flag for each
  path.
- `--instructions`: path to a markdown file describing the transformation.
- `--out-dir`: directory where `run.py` and output files are written.

Behavior:
- Copy the minimal `run.py` template from `transform-data/assets/` into
  `--out-dir` only if `run.py` does not already exist. Never overwrite an
  existing `run.py`.
- The assistant uses the provided input paths, output directory, and
  `instructions.md` to help the user write the transformation code inside the
  template.
- Once the user confirms, run `run.py`.
- Validate that `--out-dir` contains at least one output file; fail if it is empty.

Template contents (minimal):
```python
from pathlib import Path

INPUT_PATHS = [...]        # filled by the skill
OUTPUT_DIR = Path("...")   # filled by the skill

# Generated transformation code goes here.
```

The generated code imports only the libraries it needs (no unused imports).

Outputs:
- `out-dir/run.py`
- one or more output files in `out-dir`

## Shared Python package: `data_analysis_skills`

`data_analysis_skills` is a shared Python package installed into project virtual
environments. It is not a skill. Generated `run.py` scripts import
`data_analysis_skills.llm_batch` for structured LLM batch calls; Quarto
deliverables import `data_analysis_skills.helpers` to load `results.json`.

The package provides:
- `llm_batch`: structured LLM batch calls with Pydantic validation, retry logic,
  and support for multiple providers (RCP, OpenAI, ...).
- `helpers`: output helpers for loading analysis results into reports.

Location: `skills_v2/src/data_analysis_skills/`. The skill catalog root contains
a `pyproject.toml` that packages `data_analysis_skills` so it can be installed
into project virtual environments. `init.py` installs it in editable mode into
the project `.venv`; standalone skills invoked outside a skeleton project ensure
it is available before running generated scripts.

## Physical layout

`skills_v2/` is the root of the new skill catalog and future repo:

```text
skills_v2/
  .opencode/
    plugins/
      data-analysis.js       # plugin registration for OpenCode
  skills/                    # all skills
    skeleton/                # skeleton-aware orchestrator
      SKILL.md
      scripts/
        init.py
        status.py
        document_sources.py
        clean.py
      assets/
      references/
    render-quarto/           # standalone
      SKILL.md
      scripts/
        render_quarto.py
      assets/
        report/
        report-brief/
        slides/
        dashboard/
        images/
        css/
      references/
    build-duckdb/            # standalone
      SKILL.md
      scripts/
        build_duckdb.py
      assets/
        build_db.py
      references/
    run-analysis/            # standalone
      SKILL.md
      scripts/
        run_analysis.py
      assets/
        run.py
      references/
    transform-data/          # standalone
      SKILL.md
      scripts/
        transform_data.py
      assets/
        run.py
      references/
  src/                       # shared Python package source
    data_analysis_skills/
      __init__.py
      llm_batch.py
      helpers.py
  pyproject.toml
  requirements.txt
```

Each skill is self-contained and carries its own `scripts/`, `assets/`, and
`references/`. Shared code lives in `src/data_analysis_skills/`. The catalog is
installable as a Python package via `pyproject.toml` so generated scripts can
`import data_analysis_skills`.

## Migration approach

No backwards compatibility is required. The current `skills/` catalog is only a
prototype. This design replaces it entirely.
