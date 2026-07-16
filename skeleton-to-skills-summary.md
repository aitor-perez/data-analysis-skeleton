# From Skeleton Repo to Skills Catalog: Summary

This note summarizes the proposal to move from the current `data-analysis-skeleton` repository to an OpenCode skills catalog. The pipeline, conventions, and durable artifacts would stay the same; only the delivery mechanism would change.

## Current situation

Every new analysis project starts by cloning the skeleton repo. That leaves the project with the skeleton's git history, README, and management files. The assistant must read `AGENTS.md` at the start of each conversation, and progress is driven by `Makefile` targets such as `make status`, `make db`, `make analyses`, `make render`, `make outputs`, `make venv`, and `make clean`. Updates to the skeleton are pushed back through `make skeleton-sync`, which can pollute the project's own history.

## Proposed approach

The skeleton would become a catalog of OpenCode skills that users install once and invoke inside any project directory. A thin orchestrator skill, `data-analysis`, would coordinate a session: it would call `data-analysis-status` to inspect the directory, then decide whether to run the next step, propose options, or ask for confirmation. Stage-specific work would be handled by focused skills rather than by `AGENTS.md`.

`data-analysis-init` would bootstrap the project, create a local `.venv/`, and install the catalog-level dependencies from the catalog's own `requirements.txt`. A separate project-level `requirements.txt` would hold analysis-specific packages.

This keeps analysis projects light. The project directory would contain only the analysis artifacts, not the tooling conventions. Improvements would be made directly in the skills catalog and would reach users when they update the plugin.

## Mapping skeleton commands to skills

| Skeleton command | Skill invocation |
|---|---|
| Cloning the repo / `make venv` | `data-analysis-init` |
| `make status` | `data-analysis-status` |
| `make db` | `data-analysis-build-db` |
| `make analyses` | `data-analysis-analyze` |
| `make render` / `make outputs` | `data-analysis-output` |
| `make clean` | `data-analysis-clean` |

`data-analysis-plan`, `data-analysis-collect`, and `data-analysis-transform` replace the corresponding sections of `AGENTS.md`: planning, raw data collection, and heavy enrichment.

## Preserved conventions

- The five-stage pipeline remains: `0_plan → 1_data → 2_db → 3_analyses → 4_output`.
- Raw data goes into `1_data/original/` and is documented in `1_data/original/sources.yaml`. Heavy enrichment goes into `1_data/transformed/<name>/`.
- The folder structure and durable artifacts stay the same, including `plan.md`, `sources.yaml`, `project.duckdb`, `schema.md`, `results.json`, and rendered reports, slides, dashboards, or exports.
- Stage gates remain: a skill checks its own prerequisites and refuses to run if they are missing.
- Raw data in `1_data/original/` is never modified by later stages.
- Deliverables still load every number from `results.json`; no hardcoded statistics.
- Reusable helpers still live in `utils/`; LLM calls still go through `utils.llm`.

## Skill catalog overview

The catalog would contain one skill per responsibility:

- `data-analysis-init`: bootstrap a new project, create `.venv/`, and install catalog dependencies.
- `data-analysis-plan`: help fill `0_plan/plan.md` and keep it up to date.
- `data-analysis-collect`: collect raw files into `1_data/original/` and document them in `1_data/original/sources.yaml`.
- `data-analysis-transform`: run heavy enrichment in `1_data/transformed/<name>/`.
- `data-analysis-build-db`: build `2_db/project.duckdb` and generate `schema.md`.
- `data-analysis-analyze`: propose, create, and run analyses in `3_analyses/`.
- `data-analysis-output`: render Quarto reports, slides, dashboards, or data exports in `4_output/`.
- `data-analysis-status`: inspect the directory and print a plain-text pipeline summary.
- `data-analysis-clean`: remove generated files so the pipeline can be rebuilt from raw data and scripts.
- `data-analysis`: the orchestrator that reads the status summary and decides what to do next.

## Suggested next steps

1. Create a new `data-analysis-skills` repository for the catalog.
2. Implement `data-analysis-status` so it can inspect an empty directory and report stage 0.
3. Implement `data-analysis-init` and the `data-analysis` orchestrator.
4. Implement one stage skill end to end, such as `data-analysis-plan` or `data-analysis-build-db`.
5. Run a complete sample pipeline and compare the resulting artifacts with those from the current skeleton.
