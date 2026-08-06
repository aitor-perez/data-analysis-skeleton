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

- Initialize a new project (`init.py`): create directories, copy skeleton
  templates, create `.venv`, install requirements.
- Report pipeline state (`status.py`).
- Decide the next pipeline step and invoke the appropriate standalone skill with
  skeleton-specific paths.
- Clean generated artifacts (`clean.py`).
- Skeleton-specific report constraints, such as: never hardcode numbers; load
  values and figures from `3_analyses/*/results.json` using `helpers.py`.
- Data collection and provenance: document raw files in `1_data/original/` using
  `document_sources.py`, invoked by the orchestrator with skeleton-specific paths.
- Planning: a two-step, conversational process to fill `0_plan/plan.md` from the
  skeleton template.

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

Planning is a skeleton-specific responsibility because it uses the skeleton's
`plan.md` template and section structure. The interaction is not a mechanical,
question-by-question fill. Instead:

1. **Exploration**: The agent has a free-form conversation with the user to
   understand the project's goal, data, audience, risks, and desired outputs.
2. **Proposal**: The agent writes a structured `0_plan/plan.md` from the skeleton
   template, covering all required sections based on the conversation.
3. **Review**: The user edits the proposal. The agent refines until the plan is
   complete.

The template acts as an output checklist, not as an interview script.

## Standalone skills

### 1. `render-quarto`

Create and render Quarto deliverables from built-in templates.

The skill owns the deliverable templates and the general/type-specific guidance
for populating them. It can be invoked in any project, whether or not that
project follows the data-analysis skeleton.

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
- Templates live with the `render-quarto` skill.
- General guidance applies to all templates (e.g., propose a chapter split and
  ask for confirmation).
- Type-specific guidance applies to one template (e.g., label appendices A, B,
  C and reference them in a regular chapter; create one `.qmd` per chapter).
- The skill is agnostic of the skeleton. Skeleton-specific rules live in the
  orchestrator and are enforced by the agent when the orchestrator invokes this
  skill.

Outputs:
- `out-dir/*.qmd` and supporting files.
- Rendered `.pdf` or `.html` files after user confirmation.

### 2. `build-duckdb`

Run a user-provided build script and validate the resulting DuckDB database.

```bash
build-duckdb --script 2_db/build_db.py --db-dir 2_db
```

Inputs:
- `--script`: path to the Python script that builds the database.
- `--db-dir`: directory where the database and schema live.
- `--no-schema-doc` (optional): skip generating `schema.md`.

Behavior:
- Run the script.
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
- Copy a built-in, fixed `run.py` template into `--out-dir` only if `run.py` does
  not already exist. Never overwrite an existing `run.py`.
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
  --input "path/to/file1.csv path/to/file2.json path/to/pdfs/" \
  --instructions instructions.md \
  --out-dir 1_data/transformed/classify
```

Inputs:
- `--input`: a single flag containing a space-separated list of input files and/or
  directories.
- `--instructions`: path to a markdown file describing the transformation.
- `--out-dir`: directory where `run.py` and output files are written.

Behavior:
- Copy a minimal, generic `run.py` template into `--out-dir` only if `run.py`
  does not already exist. Never overwrite an existing `run.py`.
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

## Shared module: `llm_batch`

`llm_batch` is a shared Python module for structured LLM batch calls. It is not
a skill. Generated `run.py` scripts from `run-analysis` and `transform-data` can
import it.

The module provides:
- Structured output with Pydantic validation.
- Retry logic.
- Support for multiple providers (RCP, OpenAI, ...).

Location: `skills_v2/llm_batch/` (will become its own package when `skills_v2`
is extracted to a repo).

## Physical layout

`skills_v2/` is the root of the new skill catalog and future repo:

```text
skills_v2/
  .opencode/
    plugins/
      data-analysis.js   # plugin registration for OpenCode
  skeleton/               # skeleton-aware orchestrator
    SKILL.md
    init.py
    status.py
    document_sources.py
    clean.py
    templates/
      init/
      report/
      slides/
      dashboard/
      export/
  render-quarto/          # standalone
    SKILL.md
    render_quarto.py
    templates/
      report/
      report-brief/
      slides/
      dashboard/
  build-duckdb/           # standalone
    SKILL.md
    build_duckdb.py
  run-analysis/           # standalone
    SKILL.md
    run_analysis.py
    templates/
      run.py
  transform-data/         # standalone
    SKILL.md
    transform_data.py
    templates/
      run.py
  llm_batch/              # shared module
    __init__.py
    batch.py
  pyproject.toml
  requirements.txt
```

Each skill is self-contained and carries its own templates. Shared code lives in
`llm_batch/`. The catalog is installable as a Python package via `pyproject.toml`
so generated scripts can `import llm_batch`.

## Open questions

None at this point. All major design decisions are settled.

## Migration approach

No backwards compatibility is required. The current `skills/` catalog is only a
prototype. This design replaces it entirely.
