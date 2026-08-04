---
name: data-analysis
description: Use when the user explicitly asks to run, continue, or get the next step for a data-analysis pipeline project.
---

# data-analysis (orchestrator)

Coordinate the data-analysis pipeline in the current project directory.

## Responsibility

1. Inspect the project state by running the bundled `status.py` script.
2. Report the pipeline state to the user.
3. Propose the next step.
4. Wait for explicit confirmation before invoking another skill.

This skill does not do stage work itself. It delegates to the stage skills.

## How to use

1. Run the status script from the project root:

   ```bash
   python <path-to-skills>/data-analysis/status.py
   ```

2. Read the output and report it to the user in a concise form.
3. Decide the next step using the mapping below.
4. Propose the next step and wait for the user to confirm.
5. Once confirmed, invoke the appropriate stage skill.

## Next-step mapping

Use the earliest rule that matches:

| Current stage state | Proposed next skill | Proposed action |
|---|---|---|
| `0_plan` missing or incomplete | `data-analysis-plan` | Fill in `0_plan/plan.md`. |
| `1_data` empty or partial | `data-analysis-collect` | Collect raw files and document them in `1_data/original/sources.yaml`. |
| `2_db` not built, stale, or partial | `data-analysis-build-db` | Build `2_db/project.duckdb` and `2_db/schema.md`. |
| `3_analyses` empty, incomplete, or partial | `data-analysis-analyze` | Create or run analyses in `3_analyses/`. |
| `4_output` empty or partial | `data-analysis-output` | Render deliverables in `4_output/`. |
| All stages complete | none | Report that the pipeline is complete. |

## Rules

- Always run `status.py` first.
- Always propose, never auto-run.
- Wait for the user to confirm before invoking a stage skill.
- If multiple stage skills look runnable, prefer the earliest incomplete stage.
- Do not modify files directly; delegate to the appropriate stage skill.
