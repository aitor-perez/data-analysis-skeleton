---
name: data-analysis
description: Use when the user wants to start, run, continue, or get the next step for a data-analysis pipeline project.
---

# data-analysis (orchestrator)

Coordinate the data-analysis pipeline in the current project directory.

## Responsibility

1. Check whether the project has been initialized.
2. If not initialized, propose running the bundled `init.py` script and wait for confirmation.
3. Run the bundled `status.py` script with the project's `.venv/bin/python`.
4. Report the pipeline state to the user.
5. Propose the next step.
6. Wait for explicit confirmation before invoking another stage skill.

This skill does not do stage work itself. It delegates to the stage skills.

## How to use

1. Check whether the project has been initialized by looking for `.venv/bin/python`, `utils/llm.py`, and the stage directories (`0_plan/`, `1_data/`, `2_db/`, `3_analyses/`, `4_output/`).
2. If the project is not initialized:
   - Report that the project needs initialization.
   - Propose running the init script with the system Python:

     ```bash
     python3 <path-to-skills>/data-analysis/init.py
     ```

   - Wait for the user to confirm before running it.
3. If initialized, run the status script from the project root using `.venv/bin/python`:

   ```bash
   .venv/bin/python <path-to-skills>/data-analysis/status.py
   ```

4. Read the output and report it to the user in a concise form.
5. Decide the next step using the mapping below.
6. Propose the next step and wait for the user to confirm.
7. Once confirmed, invoke the appropriate stage skill.

## Next-step mapping

Use the earliest rule that matches:

| Condition | Proposed next skill | Proposed action |
|---|---|---|
| Project not initialized (`.venv/`, `utils/`, or stage directories missing) | `data-analysis` (init step) | Run `init.py` to bootstrap the project scaffold and create `.venv/`. |
| `0_plan` missing or incomplete | `data-analysis-plan` | Fill in `0_plan/plan.md`. |
| `1_data` empty or partial | `data-analysis-collect` | Collect raw files and document them in `1_data/original/sources.yaml`. |
| `2_db` not built, stale, or partial | `data-analysis-build-db` | Build `2_db/project.duckdb` and `2_db/schema.md`. |
| `3_analyses` empty, incomplete, or partial | `data-analysis-analyze` | Create or run analyses in `3_analyses/`. |
| `4_output` empty or partial | `data-analysis-output` | Render deliverables in `4_output/`. |
| All stages complete | none | Report that the pipeline is complete. |

## Rules

- If the project is not initialized, propose running `init.py` before anything else.
- Always run `status.py` using `.venv/bin/python` after initialization.
- Always propose, never auto-run.
- Wait for the user to confirm before invoking a stage skill.
- If multiple stage skills look runnable, prefer the earliest incomplete stage.
- Do not modify files directly; delegate to the appropriate stage skill.
