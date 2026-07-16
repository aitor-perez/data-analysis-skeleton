# From Skeleton Repo to Skills Catalog: Summary

This note summarizes the proposal to move from the current `data-analysis-skeleton` repository to an OpenCode skills catalog. The pipeline, conventions, and durable artifacts would stay the same; only the delivery mechanism would change.

## Current situation

Every new analysis project starts by cloning the skeleton repo. That leaves the project with the skeleton's git history, README, and management files. The assistant must read a long `AGENTS.md` at the start of each conversation, and progress is driven by `Makefile` targets such as `make status`, `make db`, `make analyses`, and `make render`. Updates to the skeleton are pushed back through `make skeleton-sync`, which can pollute the project's own history.

## Proposed approach

The skeleton would become a catalog of OpenCode skills that users install once and invoke inside any project directory. A thin orchestrator skill, `data-analysis`, would coordinate a session: it would call `data-analysis-status` to inspect the directory, then decide whether to run the next step, propose options, or ask for confirmation. Stage-specific work would be handled by focused skills rather than by a single long instruction document.

This keeps analysis projects light. The project directory would contain only the analysis artifacts, not the tooling conventions. Improvements would be made directly in the skills catalog and would reach users when they update the plugin.

## Mapping skeleton commands to skills

| Skeleton command | Skill invocation |
|---|---|
| Cloning the repo | `data-analysis-init` |
| `make status` | `data-analysis-status` |
| `make db` | `data-analysis-build-db` |
| `make analyses` | `data-analysis-analyze` |
| `make render` | `data-analysis-output` |

`data-analysis-plan` and `data-analysis-collect` replace the corresponding sections of `AGENTS.md`: planning and data documentation.

## Preserved conventions

- The five-stage pipeline remains: `0_plan → 1_data → 2_db → 3_analyses → 4_output`.
- The folder structure and durable artifacts stay the same, including `plan.md`, `sources.yaml`, `project.duckdb`, `schema.md`, `results.json`, and rendered reports or slides.
- Stage gates remain: a skill checks its own prerequisites and refuses to run if they are missing.
- Raw data in `1_data/` is never modified by later stages.
- Quarto deliverables still load every number from `results.json`; no hardcoded statistics.

## Skill catalog overview

The catalog would contain one skill per responsibility:

- `data-analysis-init`: bootstrap a new project with the standard folders.
- `data-analysis-plan`: help fill `0_plan/plan.md` and maintain `0_plan/decisions.md`.
- `data-analysis-collect`: collect raw files into `1_data/` and document them in `sources.yaml`.
- `data-analysis-build-db`: build `2_db/project.duckdb` and generate `schema.md`.
- `data-analysis-analyze`: propose, create, and run analyses in `3_analyses/`.
- `data-analysis-output`: render Quarto reports, slides, or dashboards in `4_output/`.
- `data-analysis-status`: inspect the directory and print a plain-text pipeline summary.
- `data-analysis`: the orchestrator that reads the status summary and decides what to do next.

## Suggested next steps

1. Create a new `data-analysis-skills` repository for the catalog.
2. Implement `data-analysis-status` so it can inspect an empty directory and report stage 0.
3. Implement `data-analysis-init` and the `data-analysis` orchestrator.
4. Implement one stage skill end to end, such as `data-analysis-plan` or `data-analysis-build-db`.
5. Run a complete sample pipeline and compare the resulting artifacts with those from the current skeleton.
