# From Skeleton Repo to Skills Catalog

## Context and Goal

This document is for whoever implements the migration from the current `data-analysis-skeleton` repository to a system of OpenCode skills.

The current skeleton is a repository you clone for every new data analysis project. It enforces a five-stage pipeline through folder structure, a long `AGENTS.md`, and `Makefile` targets. The goal is to keep the same pipeline behavior, the same conventions, and the same reproducibility, but deliver it through an OpenCode skills catalog rather than a cloneable template.

An OpenCode skill is a directory containing a `SKILL.md` file with instructions and optional resources such as scripts, templates, or helpers. Skills are loaded once by the assistant and can be invoked in any working directory. They do not need to be part of the project itself.

In the new model, a user creates or opens any directory and says "continue". The assistant inspects the directory, finds the current pipeline stage by running small check scripts, and proposes or executes the next runnable step.

This note records the design decisions made so far, the alternatives considered, and the questions still open.

---

## Why Move Away From a Skeleton Repo

Cloning the skeleton for each analysis has several drawbacks:

- The project directory inherits the skeleton's git history, README, and management files (`SKELETON.md`, `skeleton-sync` logic).
- Improvements to the skeleton are hard to propagate without polluting the project's own history.
- The assistant has to absorb a very long `AGENTS.md` that mixes general conventions with project-specific state.
- Starting a project feels heavy: the directory is already opinionated before any analysis question exists.

Skills, by contrast, live outside any single project. They are installed once and invoked in whatever directory the user is working in. The project directory contains only the analysis artifacts, not the tooling conventions.

---

## Core Design Principle: Explicit Runtime Contracts

The most important decision is to replace implicit folder conventions with explicit contracts that are checked at runtime.

In the skeleton, the rule "do not build the database before data is documented" is written in `AGENTS.md`. The assistant is supposed to know and enforce it. In the skills model, each skill declares what input files it requires, ships a small check script, and refuses to run if the inputs are missing.

This means:

- Contracts are explicit: a skill says what it needs.
- Contracts are enforced: a skill runs its check before doing work.
- Contracts are discoverable: `data-analysis-status` can run all checks and report which skills are currently runnable.

This is functionally equivalent to `make` targets and dependencies, but interpreted conversationally. Each skill is like a Makefile target; its check script is like a dependency check.

---

## Mapping the Current Skeleton to the New Catalog

### `AGENTS.md`

Currently a 435-line instruction document that the assistant must read before any work. In the new model, its contents are split:

- Stage-specific instructions go into the corresponding skill's `SKILL.md`.
- Cross-cutting rules (Python style, no hardcoded secrets, writing style) go into `shared/conventions.md` and are referenced by the bootstrap context.
- The pipeline flow and stage-gate logic go into `data-analysis-status`; the thin orchestrator only acts on its output.

### `.cursor/rules/pipeline.mdc`

This Cursor rule file lists the ten critical pipeline rules. It maps to a combination of `data-analysis-status` (state inspection and stage-order logic), the per-stage `check.py` scripts (prerequisite enforcement), and the thin `data-analysis` orchestrator (action policy). The orchestrator itself does not inspect files or validate contracts; it only invokes the skill recommended by `data-analysis-status`.

### `Makefile`

The Makefile provides commands like `make status`, `make db`, `make analyses`, `make render`. In the new model:

- `make status` becomes invoking `data-analysis-status`.
- `make db` becomes invoking `data-analysis-build-db`.
- `make analyses` becomes invoking `data-analysis-analyze` over all pending analyses.
- `make render` becomes invoking `data-analysis-output` for a specific deliverable.

A thin `Makefile` could still exist as a convenience wrapper around the skills, but the primary interface is the orchestrator skill `data-analysis`.

### `status.py`

This script currently does two things: it checks the state of each stage, and it suggests the next action. In the skills model, these responsibilities split:

- The per-stage checks move into each skill's `check.py`. Each skill knows its own prerequisites.
- The state-inspection and next-action logic move into `data-analysis-status`. It runs the per-stage checks, determines the current stage, and recommends the next skill to run.
- The orchestrator skill consumes the output of `data-analysis-status` and decides whether to run, propose, or ask.

So `status.py` is not directly transplanted. It is a reference implementation that shows what each skill should check. `data-analysis-status` will reuse some of the same filesystem inspection patterns, but it should not duplicate the detailed validation logic of individual stages.

### `0_plan/`

The planning stage remains unchanged in purpose. The `data-analysis-plan` skill:

- Reads `0_plan/plan.md` if it exists.
- Helps fill it when it is missing or incomplete.
- Updates `0_plan/decisions.md` when later stages reveal that the plan must change.

Equivalence with the skeleton: the same files, the same placeholder detection, the same two-phase approach.

### `1_data/`

Data collection remains the same. The `data-analysis-collect` skill:

- Helps collect files into `1_data/`.
- Documents every file in `1_data/sources.yaml`.
- Cross-references actual files against the sources log.

Equivalence with the skeleton: the same input/output, the same provenance requirements, the same confidentiality warning.

### `2_db/`

The database build remains the same. The `data-analysis-build-db` skill:

- Reads `1_data/sources.yaml`.
- Runs a build script to produce `2_db/project.duckdb`.
- Auto-generates `2_db/schema.md`.
- Flags stale databases when raw data changes.

Equivalence with the skeleton: same DuckDB target, same schema contract, same rebuild rule.

### `3_analyses/`

Analyses remain one subfolder per question, each with `run.py`, `results.json`, and optional figures. The `data-analysis-analyze` skill:

- Reads `2_db/schema.md` and `0_plan/plan.md`.
- Proposes analyses for unanswered questions.
- Creates subfolders, writes `run.py`, runs it, validates `results.json`.
- Flags analyses affected by schema changes.

Equivalence with the skeleton: same JSON contract, same figure rules, same deprecation convention.

### `4_output/`

Output generation remains the same. The `data-analysis-output` skill:

- Reads `3_analyses/*/results.json`.
- Creates dated deliverable subfolders.
- Copies templates (report, slides, dashboard) from internal resources.
- Uses a shared `helpers.py` for loading analysis results into Quarto.
- Renders PDF or HTML.

Equivalence with the skeleton: same deliverable structure, same templates, same rule that no numbers are hardcoded.

### `4_output/helpers.py`

This helper module is used by Quarto deliverables to load `results.json`. It belongs to the `data-analysis-output` skill. There are two ways to make it available to Quarto:

- **Copy into the project**: `data-analysis-output` places a `helpers.py` inside each deliverable subfolder or at the root of `4_output/`. The deliverable is then self-contained and will render even if the skills are not installed. The downside is that improvements to the helper do not propagate to existing deliverables.
- **Keep internal to the skill**: `data-analysis-output` adds its own helper directory to Python's path during rendering. Existing deliverables benefit from updates automatically, but they depend on the skill being installed. Archived projects may not render cleanly in the future.

The current skeleton copies helpers into the project. Keeping that behavior preserves equivalence, but the internal approach is cleaner long-term. A reasonable compromise is to copy helpers into the project by default and provide an option to use the internal version during active development.

Some functions may be useful to multiple skills. These should live in a shared utility directory inside the catalog, imported by the skills internally using relative paths. They are not exposed to the project directory and they are not installed into the user's Python environment. Examples include:

- Reading and parsing `sources.yaml`.
- Validating the `results.json` schema.
- Reading `schema.md` and extracting table/column names.
- Loading analysis results for inspection or rendering.
- Common path constants (e.g., the locations of `0_plan/`, `2_db/project.duckdb`).

### `4_output/templates/`

The Quarto and LaTeX templates are bundled with the `data-analysis-output` skill as internal resources. When the user asks for a report, slides, or dashboard, the skill copies the relevant files into the new deliverable subfolder.

### `SKELETON.md`

This file documents how to keep the skeleton in sync across projects. It disappears entirely. The catalog is versioned as its own repository. Improvements are made to the catalog directly and propagate when users update their skills.

### `.env.example` and secrets handling

The rule "API keys live in `.env`" remains. The catalog can ship an `.env.example` template, but the responsibility for creating and protecting `.env` belongs to the user. Skills should not write secrets.

### `requirements.txt`

The skeleton uses `requirements.txt` for Python dependencies. The catalog will use a single `pyproject.toml` at the root instead. This is the recommended approach because it is the modern Python standard, supports optional dependency groups per skill, and avoids the sprawl of multiple requirements files.

A possible structure:

```toml
[project]
name = "data-analysis-skills"
dependencies = [
    "duckdb",
    "pandas",
    "python-dotenv",
    "pyyaml",
]

[project.optional-dependencies]
output = ["quarto", "matplotlib", "plotly", "altair"]
collect = ["requests"]
```

#### Dependency handling at runtime

`pyproject.toml` declares dependencies, but it does not install them automatically. A practical pattern is:

1. Each skill documents its required packages in its `SKILL.md`.
2. The skill's entry scripts check imports at startup and fail fast with a clear `ImportError` if something is missing.
3. The assistant, on seeing the error, can offer to install the missing package. The skill itself does not silently install dependencies.

This avoids surprising side effects while still making it easy to recover. It works with both global and per-project Python environments.

### `.cursorignore` and `.gitignore`

The current skeleton has a strong rule: confidential files must be added to both `.gitignore` (so they are never committed) and `.cursorignore` (so the AI agent cannot read them).

In the skills model, the assistant will not edit `.gitignore` or any equivalent ignore file. The data collection skill can document the rule and warn the user, but enforcement becomes the user's responsibility. This is a deliberate trade-off: skills gain portability and avoid mutating project configuration, but they lose the ability to enforce repository-level privacy automatically.

If this is unacceptable, an alternative is to provide an optional skill or script that audits the project for confidential files and suggests ignore-file entries, but does not apply them without confirmation.

### `3_analyses/example_analysis/`

This template folder becomes an internal resource of the `data-analysis-analyze` skill. When the skill creates a new analysis, it uses the template as a starting point.

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
    data-analysis-build-db/
    data-analysis-analyze/
    data-analysis-output/
    data-analysis-status/
    data-analysis/
  shared/                     # Internal utilities and shared conventions
    conventions.md            # Cross-cutting rules (Python style, secrets, writing style)
  pyproject.toml              # Dependency declarations
  README.md                   # Installation and usage instructions
```

Proposed skill catalog:

| Skill | Responsibility |
|---|---|
| `data-analysis-init` | Bootstraps a new project with the standard folders and optional templates. |
| `data-analysis-plan` | Helps fill `0_plan/plan.md` and keeps `0_plan/decisions.md` up to date. |
| `data-analysis-collect` | Collects raw files into `1_data/` and documents them in `1_data/sources.yaml`. |
| `data-analysis-build-db` | Builds `2_db/project.duckdb` and generates `2_db/schema.md`. |
| `data-analysis-analyze` | Proposes, creates, and runs analyses in `3_analyses/`, producing `results.json`. |
| `data-analysis-output` | Renders Quarto deliverables in `4_output/` from analyses. |
| `data-analysis-status` | Inspects the project, reports the current pipeline stage, and recommends the next runnable skill. |
| `data-analysis` | Thin policy skill. Runs `data-analysis-status`, reads the recommended next step, and invokes it (confirming with the user). |

Each skill is a directory with at least:

- `SKILL.md`: prose instructions for the assistant, with YAML frontmatter.
- `check.py`: a script that returns whether the skill's prerequisites are satisfied in the current directory.
- Optional internal resources (templates, helpers, examples).

#### SKILL.md frontmatter

Every skill should have a YAML frontmatter block with at least `name` and `description`:

```yaml
---
name: data-analysis-collect
description: Use when raw data files exist in 1_data/ but are not yet documented in sources.yaml.
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
description: Use when raw data files exist in 1_data/ but are not yet documented in sources.yaml.
```

This convention is borrowed from the Superpowers framework, which found that agents sometimes follow a workflow-summary description instead of reading the full skill.

#### Check script interface

`data-analysis-status` needs a uniform way to ask every skill whether it can run. The orchestrator consumes the aggregated result. There are several reasonable designs:

- **Exit-code-only**: the script exits `0` if inputs are satisfied and non-zero otherwise. This is simple but gives no explanation for failures.
- **Structured output**: the script prints a small JSON or YAML blob describing whether it can run, what is missing, and whether any inputs are stale. This is richer and easier to explain to the user.
- **Convention over configuration**: the orchestrator knows each skill's required files and checks them itself, without running a per-skill script. This centralizes logic but makes the orchestrator aware of every skill's internals.

A good default is the structured-output approach, because it keeps the contract explicit and lets each skill explain its own prerequisites. The exact format should be chosen by the implementer, but it should be the same for every skill.

#### How the orchestrator discovers skills

The orchestrator must know which skills exist. Options include:

- **Hardcoded list**: the orchestrator skill's instructions contain a fixed list of skill names. This is the simplest to implement, but adding a new skill requires editing the orchestrator.
- **Convention-based discovery**: every subdirectory of a known `skills/` folder is treated as a skill. This is flexible, but it assumes a fixed catalog layout.
- **Manifest file**: a `catalog.yaml` or `skills.yaml` at the catalog root lists the available skills, their order, and their stage. This is a clean middle ground: adding a skill means editing one manifest, not the orchestrator's logic.

The manifest approach is probably the best long-term choice. It separates the "what skills exist" question from the "what should I do next" question. With the thin orchestrator, the manifest is primarily consumed by `data-analysis-status`; the orchestrator itself only needs to know how to invoke the skill named in `next_recommended_skill`.

#### Orchestrator responsibilities

`data-analysis` is a thin policy skill. It does not inspect the directory itself. Its job is:

1. Invoke `data-analysis-status` and read its structured output.
2. If the output contains a `next_recommended_skill`, decide whether to run it automatically, propose it, or ask for confirmation.
3. Invoke the recommended skill.

All state inspection lives in `data-analysis-status`. The orchestrator only translates status output into action. If no skill is recommended (for example, the pipeline is complete or a blocker requires human input), the orchestrator reports that to the user instead of doing nothing. This keeps the policy small and easy to test.

#### Bootstrap context

The plugin should inject a small, conditional prompt into conversations. The prompt triggers when the current directory contains the standard data analysis folders (`0_plan/`, `1_data/`, etc.) or when the user explicitly invokes `data-analysis-init`. It reminds the agent that the data analysis skills are available.

Example bootstrap message:

> This directory is a data analysis project. Follow `shared/conventions.md` for cross-cutting rules. Run `data-analysis-status` to get the current stage and the `next_recommended_skill`. Use `data-analysis` to act on that recommendation, or invoke stage skills such as `data-analysis-plan`, `data-analysis-collect`, and `data-analysis-build-db` directly.

The bootstrap should not appear in unrelated directories. It should also not appear in empty directories unless the user has just invoked `data-analysis-init` or asked to start a data analysis project. This keeps unrelated conversations clean while making ongoing projects aware of the skills.

The entry point for a brand-new project is `data-analysis-init`. Once the project scaffold exists, the bootstrap context and skill descriptions handle the rest.

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

This design was influenced by the [Superpowers](https://github.com/obra/superpowers) framework. We adopt its conventions for skill packaging, `SKILL.md` frontmatter, and plugin distribution. However, our domain requires stronger state inspection and orchestration than Superpowers provides, so we keep the explicit check scripts and the `data-analysis` orchestrator skill.

---

## Equivalence With the Current Skeleton

| Skeleton behavior | Skill behavior |
|---|---|
| Clone the repo to start a project. | Install the catalog once; run `data-analysis-init` to bootstrap a new project. |
| Read `AGENTS.md` at the start of every conversation. | Load only the relevant skill's instructions. |
| `make status` inspects the pipeline. | `data-analysis-status` inspects the directory and reports stage. |
| `make db` builds the database if data is ready. | `data-analysis-build-db` checks inputs, then builds or refuses. |
| `make analyses` runs all pending analyses. | `data-analysis-analyze` scans the plan and existing results, then fills gaps. |
| `make render` produces a deliverable. | `data-analysis-output` creates the deliverable from templates and analyses. |
| `sources.yaml`, `schema.md`, `results.json`, and rendered files are the durable artifacts. | Exactly the same files remain the durable artifacts. |
| Stage gates are enforced by a long instruction document. | Stage gates are enforced by explicit check scripts. |
| Improvements are backported via `make skeleton-sync`. | Improvements are made directly to the catalog repo. |

The key equivalence is: the analysis artifacts (`plan.md`, `sources.yaml`, `project.duckdb`, `schema.md`, `results.json`, rendered reports) should be the same after a sequence of skill invocations as they would be after running the corresponding `make` commands in the skeleton. The difference is how the assistant knows what to do next.

Some auxiliary files may differ depending on implementation choices. For example, `data-analysis-output` might copy `helpers.py` into the project or keep it internal. Deliverable templates might be copied from skill resources or referenced externally. The behavior that matters is reproducibility of the analysis, not byte-for-byte identity of helper files.

---

## Alternatives Considered

### One monolithic skill vs. several composable skills

A single `data-analysis-pipeline` skill could handle all stages. This would simplify orchestration but reduce flexibility and reusability. We lean toward multiple skills plus a thin orchestrator.

### Manifest files vs. check scripts

We considered declaring contracts in a machine-readable file such as `contract.yaml` inside each skill. This would be clean but adds a new format to maintain. We prefer small check scripts, because they reuse the existing Makefile-like intuition and are easy to test independently.

### Lazy vs. eager project initialization

There are two broad approaches to creating the project scaffold.

**Lazy init**: each skill creates the folders it needs when it first runs. `data-analysis-plan` creates `0_plan/` when asked to plan; `data-analysis-collect` creates `1_data/` when asked to document data. This minimizes up-front structure but makes state inspection harder, because the orchestrator has fewer predictable places to look.

**Eager init**: the `data-analysis-init` skill creates the standard folders and optionally a lightweight README or `.env.example` at the very beginning. The orchestrator then has a known layout to inspect, and the user gets a clear signal that the project has been bootstrapped.

A likely default is eager init, because it preserves the same folder structure as the current skeleton and makes "continue" easier to implement. The `data-analysis-init` skill could create:

- `0_plan/`
- `1_data/`
- `2_db/`
- `3_analyses/`
- `4_output/`
- an optional `.env.example`
- an optional short README explaining the pipeline

A state file such as `data-analysis-state.yaml` is optional. The existing artifacts (`plan.md`, `sources.yaml`, `project.duckdb`, etc.) already encode state, so a separate state file may be unnecessary.

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

A regular skill is the chosen approach, but it is kept thin. All state inspection is delegated to `data-analysis-status`, so the orchestrator remains a small policy layer. The system prompt approach is not needed for now because the bootstrap context plus the orchestrator skill handle "continue" cleanly.

### Forward flow vs. iteration

The current skeleton says "data flows forward only — never skip a stage or create backward dependencies." This is a rule about artifact purity, not a prohibition on iteration. It means:

- Raw data files in `1_data/` are never modified by later stages.
- The database in `2_db/` is only written by the database build step.
- Analyses in `3_analyses/` are only written by the analysis step.
- Reports in `4_output/` are only produced from analyses.

Going back and re-running earlier stages is normal and expected. If the user changes raw data, `data-analysis-build-db` can rebuild `project.duckdb`. If the user wants to refine an analysis, `data-analysis-analyze` can overwrite an existing `results.json`. The orchestrator should support this by allowing any skill to run whenever its prerequisites are satisfied, not just the next forward stage.

In practice, "continue" means "run the next forward step that is not yet complete," but the user can always ask for a specific skill directly. This is analogous to `make`: the default target moves forward, but you can invoke any target at any time.

---

## Deliberately Undecided

The following are design choices we are intentionally leaving open for the first implementer to decide. They are not blockers, but they should be resolved before implementation starts:

- Final folder structure convention (likely kept, but not locked).
- Whether the orchestrator auto-runs, proposes, or asks.
- Whether there is a state file beyond the existing artifacts.
- How exactly shared helpers are exposed to the project directory.
- Whether the catalog ships a thin `Makefile` as a fallback for command-line users, or is skills-only.

---

## Open Questions

The following are research or verification questions that will be answered by building and testing the catalog:

1. How do we test that a skill-run analysis is equivalent to a skeleton-run analysis? A good candidate is to reproduce one complete pipeline using both approaches and compare artifacts.
2. How do we handle Python environment creation? Should the catalog assume a global environment, create one per project, or manage its own?
3. Should `data-analysis-collect` support API-based collection directly, or should that remain a user-provided script?
4. How do we handle schema changes that invalidate existing analyses? Should the orchestrator detect them automatically, or should the user trigger re-analysis manually?

---

## Recommended First Steps

1. Create a new repository `data-analysis-skills`.
2. Define the catalog layout:
   - `.opencode/` with plugin files so OpenCode can register the skills.
   - `skills/<name>/SKILL.md` plus check scripts for each skill.
   - `shared/` for internal utilities.
   - `pyproject.toml` for dependencies.
3. Implement `data-analysis-status` first. It should be able to inspect an empty directory and report that the project is at stage 0. This validates the state-discovery mechanism before any real work is done.
4. Implement `data-analysis-init` so the catalog can bootstrap a new project.
5. Implement the orchestrator skill `data-analysis`, which uses `data-analysis-status` to decide what to do next.
6. Implement one complete stage skill, probably `data-analysis-plan` or `data-analysis-build-db`, to validate the contract/check pattern end-to-end.
7. Implement the remaining stage skills one by one.
8. Run a full pipeline on a sample dataset and compare the resulting artifacts with those produced by the current skeleton.
