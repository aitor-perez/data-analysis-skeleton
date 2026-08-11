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
- **Scaffold with `--create`, run without it.** Skills that generate code from
  templates use an explicit `--create` flag to scaffold and run without it to
  execute. This avoids stateful Makefile-like behavior.

## What stays in the orchestrator

The orchestrator (`skeleton`) keeps skeleton-specific responsibilities:

- Initialize a new project (`init.py`): create directories, generate scaffold
  files (`.env.example`, `.gitignore`) only if they do not already exist, create
  `.venv`, and install the catalog Python package in editable mode so generated
  scripts can import `skeleton_helpers`.
- Report pipeline state (`status.py`).
- Decide the next pipeline step and invoke the appropriate standalone skill with
  skeleton-specific paths.
- Clean generated artifacts (`clean.py`).
- Skeleton-specific report constraints: when invoking `render-quarto`, edit the
  generated `.qmd` files to import `skeleton_helpers.loaders` directly and load
  values and figures from `3_analyses/*/results.json`, ensuring no numbers are
  hardcoded.
- Data collection and provenance: document raw files in `1_data/original/` using
  `document_sources.py`, invoked by the orchestrator with skeleton-specific paths.
- Planning: a two-step, conversational process to fill `0_plan/plan.md` using
  the checklist in `skeleton/SKILL.md`.

### Data collection and provenance

Collection is skeleton-specific because it targets the `1_data/original/`
directory and the `sources.yaml` format. The implementation lives in the
orchestrator as `skeleton/document_sources.py`, but it is written like a
standalone skill: it takes a single `--data-dir` argument and writes or validates
`sources.yaml` inside that directory.

```bash
skeleton/document_sources.py --data-dir 1_data/original
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

The skill owns generic deliverable templates (`.qmd`, `_quarto.yml`, `.tex`,
`.css`, images) and guidance for populating them. It is agnostic of the
data-analysis skeleton and can be invoked in any project. Each template declares
its output format in `_quarto.yml` and/or its `.qmd` YAML frontmatter.

```bash
render-quarto --create report --out-dir my_report
render-quarto --out-dir my_report
```

Inputs:
- `--out-dir`: directory containing or receiving the Quarto project. Always
  required.
- `--create` (optional): template to instantiate (`report`,
  `slides`, `dashboard`, ...).

Behavior:
- If `--create` is passed, copy the chosen template into `--out-dir` only if the
  target files do not already exist. Never overwrite an existing `_quarto.yml`,
  `.qmd`, or supporting file. Every template ships a `_quarto.yml` project file
  plus one or more `.qmd` files; output format and project structure are
  declared in `_quarto.yml` and the `.qmd` frontmatter.
- If `--create` is not passed, require a `_quarto.yml` in `--out-dir` and run
  `quarto render <out-dir>` as a Quarto project.
- Fail fast with a clear error if `--create` is not passed and `--out-dir` does
  not contain `_quarto.yml`.
- When creating from a template, propose a structure (chapters, sections,
  appendices) based on the template rules and any available context, then work
  with the user to fill both `_quarto.yml` and the `.qmd` files before rendering.

Templates and guidance:
- Templates live in `render-quarto/assets/`. Every template is a Quarto project
  and includes `_quarto.yml`.
- General guidance applies to all templates (e.g., propose a chapter split and
  ask for confirmation).
- Type-specific guidance applies to one template (e.g., label appendices A, B,
  C and reference them in a regular chapter; create one `.qmd` per chapter).
- The templates contain no analysis-specific logic. When the skeleton
  orchestrator invokes this skill, it edits the generated `.qmd` files to
  import `skeleton_helpers.loaders` directly and enforces skeleton-specific
  report constraints.

Outputs:
- With `--create`: `out-dir/_quarto.yml`, `out-dir/*.qmd`, and supporting files.
- Without `--create`: rendered output in the format declared by the project.

### 2. `build-duckdb`

Build and validate a DuckDB database from raw data files.

```bash
build-duckdb --create --data-dir 1_data --out-dir 2_db
build-duckdb --data-dir 1_data --out-dir 2_db
```

Inputs:
- `--data-dir`: directory containing the raw data files to load into the
  database.
- `--out-dir`: directory where `build_db.py`, the `.duckdb` database, and
  `schema.md` live.
- `--create`: copy the `build_db.py` template into `--out-dir` and exit.

Behavior:
- With `--create`: copy the built-in `build_db.py` template from
  `build-duckdb/assets/` into `--out-dir/build_db.py` only if it does not already
  exist. The template contains commented placeholders that you must edit before
  running. Never overwrite an existing build script.
- Without `--create`: require `build_db.py` in `--out-dir`, run it, and validate
  that exactly one `.duckdb` file and a non-empty `schema.md` were produced.
- The agent edits the scaffolded `build_db.py` to import and transform data,
  using `0_plan/plan.md` for guidance when running from the skeleton.
- Fail fast with a clear error if `build_db.py` is missing and `--create` was not
  passed, or if validation fails.

Outputs:
- `out-dir/build_db.py`
- `out-dir/<name>.duckdb`
- `out-dir/schema.md`

### 3. `run-analysis`

Scaffold and run an analysis against a DuckDB database.

```bash
run-analysis --create --db-dir 2_db --out-dir 3_analyses/q1
run-analysis --db-dir 2_db --out-dir 3_analyses/q1
```

Inputs:
- `--db-dir`: directory containing exactly one `.duckdb` file and a `schema.md`.
- `--out-dir`: directory where `run.py`, `results.json`, and `figures/` are
  written.
- `--create`: copy the `run.py` template into `--out-dir` and exit.

Behavior:
- Fail fast with a clear error if `--db-dir` does not contain exactly one
  `.duckdb` file or a `schema.md`.
- With `--create`: copy the built-in `run.py` template from `run-analysis/assets/`
  into `--out-dir/run.py` only if it does not already exist. The template
  contains commented placeholders that you must edit before running. Never
  overwrite an existing `run.py`.
- Without `--create`: require `run.py` in `--out-dir`, run it, and validate
  `results.json` against the standard schema.
- The agent edits the scaffolded `run.py` to answer the analysis question,
  using `0_plan/plan.md` and `schema.md` for guidance when running from the
  skeleton.
- Fail fast with a clear error if `run.py` is missing and `--create` was not
  passed, or if validation fails.

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

Scaffold and run a data transformation or enrichment.

```bash
transform-data --create \
  --input path/to/file1.csv \
  --input path/to/file2.json \
  --input path/to/pdfs/ \
  --out-dir 1_data/transformed/classify

transform-data \
  --input path/to/file1.csv \
  --out-dir 1_data/transformed/classify
```

Inputs:
- `--input`: one or more input files and/or directories. Repeat the flag for each
  path.
- `--out-dir`: directory where `run.py` and output files are written.
- `--create`: copy the `run.py` template into `--out-dir` and exit.

Behavior:
- With `--create`: copy the minimal `run.py` template from
  `transform-data/assets/` into `--out-dir/run.py` only if it does not already
  exist. The template contains commented placeholders that you must edit before
  running. Never overwrite an existing `run.py`.
- Without `--create`: require `run.py` in `--out-dir`, run it, and validate that
  at least one output file was produced.
- The agent edits the scaffolded `run.py` to implement the transformation,
  using `0_plan/plan.md` for guidance when running from the skeleton.
- Fail fast if any input path does not exist, or if no output files are produced.

Template contents (minimal):
```python
from pathlib import Path

# TODO: list the input files or directories for this transformation, then uncomment.
# INPUT_PATHS = [Path("...")]

# TODO: point OUTPUT_DIR at the directory where outputs should be written, then uncomment.
# OUTPUT_DIR = Path("...")

# Generated transformation code goes here.
```

The generated code imports only the libraries it needs (no unused imports).

Outputs:
- `out-dir/run.py`
- one or more output files in `out-dir`

## Shared Python package: `skeleton_helpers`

`skeleton_helpers` is a shared Python package installed into project virtual
environments. It is not a skill. Generated `run.py` scripts import
`skeleton_helpers.llm` for structured LLM calls; Quarto deliverables import
`skeleton_helpers.loaders` (typically through a skeleton-generated wrapper) to
load `results.json`.

The package provides:
- `llm`: structured single and batch LLM calls with Pydantic validation, retry
  logic, and support for multiple providers (RCP, OpenAI, ...).
- `loaders`: output helpers for loading analysis results into reports.

Location: `skills_v2/src/skeleton_helpers/`. The skill catalog root contains a
`pyproject.toml` that packages `skeleton_helpers` so it can be installed into
project virtual environments. `init.py` installs it in editable mode into the
project `.venv`.

For standalone use outside a skeleton project, install the package once from the
catalog root (`pip install -e .`).

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
  README.md
  pyproject.toml
  src/                       # shared Python package source
    skeleton_helpers/
      __init__.py
      llm.py
      loaders.py
```

Each skill is self-contained and carries its own `scripts/`, `assets/`, and
`references/`. Shared code lives in `src/skeleton_helpers/`. The catalog is
installable as a Python package via `pyproject.toml` so generated scripts can
`import skeleton_helpers`.

## Migration approach

No backwards compatibility is required. The current `skills/` catalog is only a
prototype. This design replaces it entirely.
