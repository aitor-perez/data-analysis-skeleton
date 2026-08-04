# Data Analysis Skills Catalog

OpenCode skills for running the data-analysis pipeline in any project directory.

This catalog replaces the `data-analysis-skeleton` repository as a cloneable template. Instead of cloning the skeleton for every project, users install the catalog once and invoke individual skills inside the project they are working on.

## Skills

| Skill | Responsibility |
|---|---|
| `data-analysis` | Orchestrator. Inspects pipeline state and proposes the next step. |
| `data-analysis-init` | Bootstrap a new project and create `.venv/`. |
| `data-analysis-plan` | Create and fill `0_plan/plan.md`. |
| `data-analysis-collect` | Document raw files in `1_data/original/sources.yaml`. |
| `data-analysis-transform` | Run heavy enrichment in `1_data/transformed/<name>/`. |
| `data-analysis-build-db` | Build `2_db/project.duckdb` and generate `schema.md`. |
| `data-analysis-analyze` | Create and run analyses in `3_analyses/`. |
| `data-analysis-output` | Render deliverables in `4_output/` from analyses. |
| `data-analysis-clean` | Remove generated files while preserving raw data and scripts. |

## Installation (development)

For now, copy or symlink this directory into `~/.config/opencode/skills/` so OpenCode can discover the skills. Plugin packaging will come later.

## Pipeline

```
0_plan -> 1_data -> 2_db -> 3_analyses -> 4_output
```

See each skill's `SKILL.md` for usage instructions.
