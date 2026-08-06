# From Skeleton Repo to Skills Catalog

## Context and Goal

This document is for whoever implements the migration from the current `data-analysis-skeleton` repository to a system of OpenCode skills.

The current skeleton is a repository you clone for every new data analysis project. It enforces a five-stage pipeline through folder structure, `AGENTS.md`, and `Makefile` targets. The goal is to keep the same pipeline behavior and the same conventions, but deliver them through an OpenCode skills catalog rather than a cloneable template.

An OpenCode skill is a directory containing a `SKILL.md` file with instructions and optional resources such as scripts, templates, or helpers. Skills are loaded once by the assistant and can be invoked in any working directory. They do not need to be part of the project itself.

In the new model, a user creates or opens any directory and invokes a skill explicitly, for example by saying "continue" or "run data-analysis-status". The assistant inspects the directory, reports the current pipeline stage, and proposes or executes the next step.

This note records the design decisions made so far, the alternatives considered, and the questions still open.

---

## Why Move Away From a Skeleton Repo

Cloning the skeleton for each analysis has several drawbacks:

- The project directory inherits the skeleton's git history, README, and management files (`SKELETON.md`, `skeleton-sync` logic).
- Improvements to the skeleton are hard to propagate without polluting the project's own history.
- The assistant has to absorb `AGENTS.md` on every project, even though the conventions it contains are the same each time.
- Starting a project feels heavy: the directory is already opinionated before any analysis question exists.

Skills, by contrast, live outside any single project. They are installed once and invoked in whatever directory the user is working in. The project directory contains only the analysis artifacts, not the tooling conventions.

---

## Core Design Principle: Status-Driven, Assistant-Mediated

The most important decision is to replace `AGENTS.md` with focused skills, and to keep state inspection as close as possible to the current `status.py`.

In the skeleton, the rule "do not build the database before data is documented" is written in `AGENTS.md`. The assistant is supposed to know and enforce it. In the skills model, `data-analysis-status` runs a deterministic script that reports the project's pipeline state in plain text. Each stage skill validates its own inputs before doing work and fails fast with a clear message if prerequisites are missing.

This means:

- State is explicit: the status skill says what it sees.
- Stage gates are declared in skill instructions, and each skill checks its own prerequisites when invoked.
- Enforcement is assistant-mediated, not mechanical. The assistant is expected to consult `data-analysis-status` and follow the stage order, but nothing prevents it from acting on its own.

This is functionally equivalent to the current skeleton. `status.py` already reports state; the assistant already decides what to do next. The skills model just packages those responsibilities more cleanly.

---

## Mapping the Current Skeleton to the New Catalog

### `AGENTS.md`

Currently a 214-line instruction document that the assistant reads before any work. In the new model, its contents are split:

- Stage-specific instructions go into the corresponding skill's `SKILL.md`.
- Cross-cutting rules (Python style, no hardcoded secrets, writing style, use `utils.llm` for LLM calls) go into `shared/conventions.md` and are referenced by the skills.
- The pipeline flow and stage-order logic go into the thin orchestrator; `data-analysis-status` only reports state.

### `.cursor/rules/pipeline.mdc`

This Cursor rule file now just points to `AGENTS.md`. In the skills model it disappears; its content moves into `shared/conventions.md` and the per-stage `SKILL.md` instructions. The orchestrator itself does not inspect files or validate contracts; it only acts on the status summary.

### `Makefile`

The Makefile provides commands like `make status`, `make db`, `make analyses`, `make render`, `make outputs`, `make venv`, and `make clean`. In the new model each command becomes a skill invocation:

- `make status` becomes invoking `data-analysis-status`.
- `make db` becomes invoking `data-analysis-build-db`.
- `make analyses` becomes invoking `data-analysis-analyze` over all pending analyses.
- `make render` and `make outputs` become invoking `data-analysis-output`.
- `make venv` becomes part of `data-analysis-init`, which creates a local `.venv/`, installs the catalog dependencies, and creates a project-level `requirements.txt` template.
- `make clean` becomes invoking `data-analysis-clean`, which removes generated files (`2_db/project.duckdb`, `3_analyses/*/results.json`, figures, rendered outputs) while leaving raw data, plans, scripts, and deliverable sources intact.

There is no project-level Makefile in the skills model. The catalog is skills-only.

### `status.py`

This script currently inspects the state of each stage and prints a human-readable summary. In the skills model:

- The inspection logic moves into `data-analysis-status` as an internal script.
- The script prints a text summary of the pipeline state: which stages are complete, which are missing, and which skills could run.
- It does not output JSON and it does not recommend a single next action.
- The orchestrator skill consumes the summary and decides whether to run, propose, or ask.

One deliberate change: the current `status.py` prints a single next-action suggestion (for example, "Document all original files in 1_data/original/sources.yaml"). In the skills model, that recommendation moves into the orchestrator. `data-analysis-status` only reports state and runnable skills; it does not pick the next step. The pipeline state itself is unchanged.

### `0_plan/`

The planning stage remains unchanged in purpose. The `data-analysis-plan` skill reads and helps fill `0_plan/plan.md`, updating it when later stages reveal that the plan must change.

Equivalence with the skeleton: the same file and the same placeholder detection.

### `1_data/`

Data collection remains the same. The `data-analysis-collect` skill:

- Helps collect raw files into `1_data/original/`.
- Documents every original file in `1_data/original/sources.yaml`.
- Cross-references actual files against the sources log.
- Flags confidential files in `sources.yaml`.

Heavy enrichment that produces new data (LLM classification, OCR, geocoding) belongs in `1_data/transformed/<name>/` and is handled by the `data-analysis-transform` skill.

The skill does not enforce `.gitignore` or `.cursorignore` entries. The user is responsible for making sure confidential files are ignored by git and by the agent through their own OpenCode configuration.

### `2_db/`

The database build remains the same. The `data-analysis-build-db` skill:

- Reads `1_data/original/sources.yaml` and the files in `1_data/original/` and `1_data/transformed/`.
- Runs a build script to produce `2_db/project.duckdb`.
- Auto-generates `2_db/schema.md`.
- Can optionally warn if the database looks older than the raw or transformed data, using the same mtime heuristic as the current `status.py`.

No fingerprint files or stored state are introduced. The user decides when to rebuild.

### `3_analyses/`

Analyses remain one subfolder per question, each with `run.py`, `results.json`, and optional figures. The `data-analysis-analyze` skill:

- Reads `2_db/schema.md` and `0_plan/plan.md`.
- Proposes analyses for unanswered questions.
- Creates subfolders, writes `run.py`, runs it, validates `results.json`.

The skeleton does not automatically detect analyses invalidated by schema changes, so the skills model does not either. The user re-runs analyses when needed.

### `4_output/`

Output generation remains the same. The `data-analysis-output` skill:

- Reads `3_analyses/*/results.json`.
- Creates dated deliverable subfolders.
- Copies templates (report, report-brief, slides, dashboard, export) from internal resources.
- Uses a shared `helpers.py` for loading analysis results into Quarto.
- Renders PDF or HTML, or runs `export.py` for data exports.

Equivalence with the skeleton: same deliverable structure, same templates, same rule that no numbers are hardcoded.

### `4_output/helpers.py`

This helper module is used by Quarto deliverables to load `results.json`. It belongs to the `data-analysis-output` skill, but it is copied into the project at `4_output/helpers.py`, just as the skeleton does.

Reasons to copy:

- Deliverables can be rendered without the skills installed.
- Old projects keep working even if the catalog changes later.
- It preserves equivalence with the current skeleton.

The downside is that improvements to the helper do not propagate to existing deliverables. Since the rendered PDF/HTML is the final artifact and old deliverables are rarely re-rendered, this is acceptable for v1.

Some functions may be useful to multiple skills. These should live in a shared utility directory inside the catalog, imported by the skills internally using relative paths. They are not exposed to the project directory and they are not installed into the user's Python environment. Examples include:

- Reading and parsing `sources.yaml`.
- Validating the `results.json` schema.
- Reading `schema.md` and extracting table/column names.
- Loading analysis results for inspection or rendering.
- Common path constants (e.g., the locations of `0_plan/`, `2_db/project.duckdb`).

### `4_output/templates/`

The Quarto, LaTeX, and Python templates are bundled with the `data-analysis-output` skill as internal resources. When the user asks for a report, report-brief, slides, dashboard, or data export, the skill copies the relevant files into the new deliverable subfolder.

### `utils/`

The skeleton ships a `utils/` directory with shared Python helpers, including `utils.llm` for OpenAI-compatible LLM calls. The `AGENTS.md` rule "use `utils.llm` for LLM calls instead of ad hoc `requests` code" becomes a cross-cutting convention in `shared/conventions.md`.

In the skills model, `data-analysis-init` copies a minimal `utils/` scaffold (including `utils.llm`) into the project. `data-analysis-transform` and any analysis script that needs LLM calls use that project-local `utils.llm`. Improvements to the helper can be backported by updating the catalog, but existing projects keep the copied version unless the user replaces it.

### `SKELETON.md`

This file documents how to keep the skeleton in sync across projects. It disappears entirely. The catalog is versioned as its own repository. Improvements are made to the catalog directly and propagate when users update their skills.

### `.env.example` and secrets handling

The rule "API keys live in `.env`" remains. The catalog can ship an `.env.example` template, but the responsibility for creating and protecting `.env` belongs to the user. Skills should not write secrets.

### `requirements.txt`

The skeleton uses a single project-level `requirements.txt` for all Python dependencies. The skills model splits this into two files:

- A catalog-level `requirements.txt` at the catalog root for the packages the skills themselves need (`duckdb`, `pandas`, `python-dotenv`, `pyyaml`, `pydantic`, `requests`, `jupyter`, etc.).
- A project-level `requirements.txt` for analysis-specific dependencies (whatever `3_analyses/*/run.py` and `2_db/build_db.py` need).

`data-analysis-init` creates a local `.venv/` in the project and installs the catalog-level dependencies from the catalog's `requirements.txt`. The project-level `requirements.txt` is created as an empty or minimal template; the user or the assistant adds analysis-specific packages to it as needed.

#### Dependency handling at runtime

Catalog dependencies are installed once by `data-analysis-init`. After that, skills do not install packages automatically at runtime. A practical pattern for all skills except init is:

1. Each skill documents its required packages in its `SKILL.md`.
2. The Python code the assistant runs on the skill's behalf checks imports at startup and fails fast with a clear `ImportError` if something is missing.
3. The assistant, on seeing the error, can offer to install the missing package into the project's `.venv/`. The skill itself does not silently install dependencies.

Project-specific analysis dependencies live in the project's own `requirements.txt` and are managed separately from the catalog dependencies. This avoids surprising side effects while still making it easy to recover.

### `.cursorignore` and `.gitignore`

The current skeleton has a strong rule: confidential files must be added to both `.gitignore` (so they are never committed) and `.cursorignore` (so the AI agent cannot read them).

In the skills model, `.cursorignore` is not used. The agent's read access is governed by the user's OpenCode permissions. `data-analysis-collect` still flags confidential files in `sources.yaml`, but it does not try to prevent the agent from reading them. That responsibility lies outside the catalog.

### `3_analyses/example_analysis/`

The skeleton no longer ships this folder; the `run.py` template now lives in `AGENTS.md`. The `data-analysis-analyze` skill ships its own internal `run.py` template and uses it as a starting point when creating a new analysis.

---

## Proposed Skill Catalog Architecture

The catalog is a single repository containing multiple skills. It is distributed as an OpenCode plugin and does not need to be cloned into a project directory.

Proposed catalog layout:

```
data-analysis-skills/
  .opencode/                  # Plugin registration for OpenCode
  skills/
    data-analysis-init/
    data-analysis-plan/
    data-analysis-collect/
    data-analysis-transform/
    data-analysis-build-db/
    data-analysis-analyze/
    data-analysis-output/
    data-analysis-status/
    data-analysis-clean/
    data-analysis/
  shared/                     # Internal utilities and shared conventions
    conventions.md            # Cross-cutting rules (Python style, secrets, writing style)
  requirements.txt            # Dependencies for the skills themselves
  README.md                   # Installation and usage instructions
```

Proposed skill catalog:

| Skill | Responsibility |
|---|---|
| `data-analysis-init` | Bootstraps a new project, creates `.venv/`, and installs the catalog dependencies. |
| `data-analysis-plan` | Helps fill `0_plan/plan.md` and keep it up to date. |
| `data-analysis-collect` | Collects raw files into `1_data/original/` and documents them in `1_data/original/sources.yaml`. |
| `data-analysis-transform` | Runs heavy enrichment in `1_data/transformed/<name>/` (LLM, OCR, geocoding, etc.). |
| `data-analysis-build-db` | Builds `2_db/project.duckdb` and generates `2_db/schema.md`. |
| `data-analysis-analyze` | Proposes, creates, and runs analyses in `3_analyses/`, producing `results.json`. |
| `data-analysis-output` | Renders Quarto deliverables and data exports in `4_output/` from analyses. |
| `data-analysis-status` | Runs a deterministic status script and prints a text summary of the pipeline state. |
| `data-analysis-clean` | Removes generated files so the pipeline can be rebuilt from raw data and scripts. |
| `data-analysis` | Thin policy skill. Reads the status summary and decides whether to run, propose, or ask. |

The descriptions above summarize responsibilities. The actual `SKILL.md` frontmatter must use trigger-style descriptions such as "Use when..." (see the `SKILL.md frontmatter` section below).

Each skill is a directory with at least:

- `SKILL.md`: prose instructions for the assistant, with YAML frontmatter.
- Optional internal resources (templates, helpers, examples, scripts).

#### SKILL.md frontmatter

Every skill should have a YAML frontmatter block with at least `name` and `description`:

```yaml
---
name: data-analysis-collect
description: Use when raw data files exist in 1_data/original/ but are not yet documented in 1_data/original/sources.yaml.
---
```

The description is critical because OpenCode uses it to decide when to load the skill. Follow these rules:

- Start with "Use when...".
- Describe the trigger or symptom, not the workflow.
- Be specific enough that the skill loads when needed, but not so broad that it loads in unrelated conversations.
- Write in third person.

A bad description summarizes the workflow:

```yaml
description: Collects data files and documents them in sources.yaml.
```

A good description describes the trigger:

```yaml
description: Use when raw data files exist in 1_data/original/ but are not yet documented in 1_data/original/sources.yaml.
```

This convention is borrowed from the Superpowers framework, which found that agents sometimes follow a workflow-summary description instead of reading the full skill.

#### Status script output

`data-analysis-status` runs a deterministic script that prints a plain-text summary. The script itself is a resource inside the `data-analysis-status` skill; the skill instructions reference it relative to the skill directory, and OpenCode provides the skill's absolute path at load time. The exact format can evolve, but it should include at least:

- The current pipeline stage.
- Which stages are complete, incomplete, empty, or stale.
- Which stage skills are runnable given the current state.
- Any issues or notes (e.g., undocumented data files, missing results.json).

Example output:

```text
Pipeline Status
===============
Stage 0 — Plan:     Complete
Stage 1 — Data:     Partial (undocumented: raw_2026.csv)
Stage 2 — Database: Not built
Stage 3 — Analyses: Empty
Stage 4 — Output:   Empty

Runnable skills: data-analysis-collect, data-analysis-plan
Notes: Raw data exists but is not fully documented.
```

The orchestrator skill reads this summary and applies a policy. For example, on "continue" it might run the earliest incomplete stage skill that appears runnable. The status skill itself does not recommend a single next action.

#### How the orchestrator discovers skills

The orchestrator contains a small, fixed list of stage skill names. It does not dynamically discover skills. Adding a new stage skill requires updating the orchestrator's instructions, but with only five pipeline stages this is acceptable and keeps the orchestrator simple.

#### Orchestrator responsibilities

`data-analysis` is a thin policy skill. It does not inspect the directory itself. Its job is:

1. Invoke `data-analysis-status` and read its text summary.
2. Decide whether to run the next likely skill, propose a choice, or ask for confirmation.
3. Invoke the chosen skill.

All state inspection lives in `data-analysis-status`. The orchestrator only translates the status summary into action. If no skill is clearly runnable, the orchestrator reports that to the user instead of doing nothing. This keeps the policy small and easy to test.

#### No automatic bootstrap

The catalog does not inject a bootstrap prompt when a data-analysis directory is opened. Skills are invoked explicitly by the user. OpenCode loads skills based on their `SKILL.md` descriptions, so natural language like "continue" or "what should I do next" can still trigger the orchestrator skill if its description is well written.

This avoids dependencies on OpenCode plugin trigger APIs and keeps unrelated conversations free of pipeline context.

The entry point for a brand-new project is `data-analysis-init`. Once the project scaffold exists, the user invokes stage skills or the orchestrator directly.

#### How the catalog is distributed

The recommended distribution mechanism is an **OpenCode plugin**. Users add the catalog to their `opencode.json`:

```json
{
  "plugin": ["data-analysis-skills@git+https://github.com/<org>/data-analysis-skills.git"]
}
```

The plugin registers the `skills/` directory so OpenCode discovers all `data-analysis-*` skills automatically. Updates are pulled by restarting OpenCode or reinstalling the plugin.

For development and testing, a manual clone or symlink into `~/.config/opencode/skills/` can still be used. But the plugin approach is the default for end users because it is simpler, versionable, and does not require manual file management.

Packaging the catalog as a Python package is not recommended. The skills must be visible to OpenCode's skill loader, and a pip-installed package would still need a post-install step to expose skill files.

---

## Relationship to Superpowers

This design was influenced by the [Superpowers](https://github.com/obra/superpowers) framework. We adopt its conventions for skill packaging, `SKILL.md` frontmatter, and plugin distribution. However, our domain requires a deterministic status script and a thin orchestrator, so we keep `data-analysis-status` and `data-analysis` as separate skills.

---

## Equivalence With the Current Skeleton

| Skeleton behavior | Skill behavior |
|---|---|
| Clone the repo to start a project. | Install the catalog once; run `data-analysis-init` to bootstrap a new project and set up `.venv/`. |
| Read `AGENTS.md` at the start of every conversation. | Load the orchestrator skill and let it invoke stage skills as needed. |
| `make status` inspects the pipeline. | `data-analysis-status` inspects the directory and reports stage. |
| `make db` builds the database if data is ready. | `data-analysis-build-db` checks inputs, then builds or refuses. |
| `make analyses` runs all pending analyses. | `data-analysis-analyze` scans the plan and existing results, then fills gaps. |
| `make render` / `make outputs` produce deliverables. | `data-analysis-output` creates the deliverable from templates and analyses. |
| `make clean` removes generated files. | `data-analysis-clean` removes generated files while preserving raw data, plans, and scripts. |
| `sources.yaml`, `schema.md`, `results.json`, and rendered files are the durable artifacts. | Exactly the same files remain the durable artifacts. |
| Stage gates are enforced by `AGENTS.md`. | Stage gates are declared in skill instructions; status reports state and stage skills validate their own inputs. |
| Improvements are backported via `make skeleton-sync`. | Improvements are made directly to the catalog repo. |

The key equivalence is: the analysis artifacts (`plan.md`, `sources.yaml`, `project.duckdb`, `schema.md`, `results.json`, rendered reports) should be the same after a sequence of skill invocations as they would be after running the corresponding `make` commands in the skeleton. The difference is how the assistant knows what to do next.

Some auxiliary files may differ depending on implementation choices. For example, `data-analysis-output` copies `helpers.py` into the project. Deliverable templates are copied from skill resources. The behavior that matters is the resulting analysis artifacts, not byte-for-byte identity of helper files.

---

## Alternatives Considered

### One monolithic skill vs. several composable skills

A single `data-analysis-pipeline` skill could handle all stages. This would simplify orchestration but reduce flexibility and reusability. We lean toward multiple skills plus a thin orchestrator.

### Auto-run vs. propose vs. ask

We have not decided how aggressive the orchestrator should be. Options include:

- Auto-run the next runnable skill without asking.
- Propose the next step and wait for confirmation.
- Always present a menu of currently runnable skills.

The likely default is to propose and confirm, at least for the first few interactions.

### Keeping the skeleton as a hybrid

We considered keeping the skeleton repo and adding skills on top. This was rejected because it gives the worst of both worlds: users still clone a template, and the assistant still has to reason about both the repo and the skill layer.

### Orchestrator as skill vs. system prompt

The orchestrator could be implemented in two ways:

- **As a regular skill**: the user invokes it explicitly, for example by saying "continue". This keeps the logic scoped and avoids loading pipeline rules into unrelated conversations. The downside is that the user must remember to invoke it.
- **As a system prompt rule**: the assistant always knows about the pipeline and can propose the next step automatically. This makes "continue" feel seamless, but it loads pipeline context into every conversation, even those that have nothing to do with data analysis.

A regular skill is the chosen approach, but it is kept thin. All state inspection is delegated to `data-analysis-status`, so the orchestrator remains a small policy layer. The system prompt approach is not needed for now because the user can invoke the orchestrator skill directly.

### Forward flow vs. iteration

The current skeleton says "data flows forward only — never skip a stage or create backward dependencies." This is a rule about artifact purity, not a prohibition on iteration. It means:

- Raw data files in `1_data/original/` are never modified by later stages.
- The database in `2_db/` is only written by the database build step.
- Analyses in `3_analyses/` are only written by the analysis step.
- Reports in `4_output/` are only produced from analyses.

Going back and re-running earlier stages is normal and expected. If the user changes raw data, `data-analysis-build-db` can rebuild `project.duckdb`. If the user wants to refine an analysis, `data-analysis-analyze` can overwrite an existing `results.json`. The orchestrator should support this by allowing any skill to run whenever its prerequisites are satisfied, not just the next forward stage.

In practice, "continue" means "run the next forward step that is not yet complete," but the user can always ask for a specific skill directly. This is analogous to `make`: the default target moves forward, but you can invoke any target at any time.

---

## Deliberately Undecided

The following are design choices we are intentionally leaving open for the first implementer to decide. They are not blockers, but they should be resolved before implementation starts:

- Whether the orchestrator auto-runs, proposes, or asks.
- Whether `data-analysis-status` includes mtime-based staleness warnings or keeps the summary minimal.
- How `data-analysis-init` populates the scaffold (README, `.env.example`, `utils/`, `.gitignore`, example analysis, etc.).
- How `data-analysis-transform` is triggered (automatically after collect, manually by the user, or only when the plan calls for it).

---

## Open Questions

The following are research or verification questions that will be answered by building and testing the catalog:

1. How do we test that a skill-run analysis is equivalent to a skeleton-run analysis? A good candidate is to reproduce one complete pipeline using both approaches and compare artifacts.
2. What is the correct OpenCode plugin manifest format for registering a directory of skills (`.opencode/` vs. `opencode.json`) and how are skill paths resolved at runtime?
3. How should `data-analysis-collect` help the user author and place fetch/download scripts in `1_data/original/`? The current skeleton treats API-based collection as a user-provided script in `1_data/original/`.
4. Should we add an explicit command or skill to re-run all analyses after a schema change, or should that remain a manual user decision as it is in the skeleton?

---

## Recommended First Steps

1. Create a new repository `data-analysis-skills`.
2. Define the catalog layout:
   - `.opencode/` with plugin files so OpenCode can register the skills.
   - `skills/<name>/SKILL.md` for each skill.
   - `shared/` for internal utilities and `conventions.md`.
   - `requirements.txt` for skill dependencies.
3. Implement `data-analysis-status` first. It should be able to inspect an empty directory and report that the project is at stage 0. This validates the state-discovery mechanism before any real work is done.
4. Implement `data-analysis-init` so the catalog can bootstrap a new project.
5. Implement the orchestrator skill `data-analysis`, which uses `data-analysis-status` to decide what to do next.
6. Implement one complete stage skill, probably `data-analysis-plan` or `data-analysis-build-db`, to validate the skill pattern end-to-end.
7. Implement the remaining stage skills one by one.
8. Run a full pipeline on a sample dataset and compare the resulting artifacts with those produced by the current skeleton.
