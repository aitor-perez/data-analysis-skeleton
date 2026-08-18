---
name: skeleton
description: Orchestrate the data-analysis pipeline in the current project directory.
---

# skeleton (orchestrator)

Coordinate the data-analysis pipeline in the current project directory.

## Responsibility

1. Check whether the project has been initialized.
2. If not initialized, propose running the bundled `init.py` script and wait for confirmation.
3. Run the bundled `status.py` script with the project's `.venv/bin/python`.
4. Report the pipeline state to the user.
5. Propose the next step.
6. Wait for explicit confirmation before invoking another stage skill.

This skill does not do stage work itself. It delegates to the standalone skills.

## How to use

1. Check whether the project has been initialized by looking for `.venv/bin/python` and the stage directories (`0_plan/`, `1_data/`, `2_db/`, `3_analyses/`, `4_output/`).
2. If the project is not initialized:
   - Report that the project needs initialization.
   - Propose running the init script with the system Python:

     ```bash
     python3 <path-to-catalog>/skills/skeleton/scripts/init.py
     ```

   - Wait for the user to confirm before running it.
3. If initialized, run the status script from the project root using `.venv/bin/python`:

   ```bash
   .venv/bin/python <path-to-catalog>/skills/skeleton/scripts/status.py
   ```

4. Read the output and report it to the user in a concise form.
5. Decide the next step using the mapping below.
6. Propose the next step and wait for the user to confirm.
7. Once confirmed, invoke the appropriate standalone skill with skeleton-specific paths.

## Next-step mapping

Use the earliest rule that matches:

| Condition | Proposed next skill | Proposed action |
|---|---|---|
| Project not initialized (`.venv/` or stage directories missing) | `skeleton` (init step) | Run `skills/skeleton/scripts/init.py` to bootstrap the project. |
| `0_plan/plan.md` missing or incomplete | `skeleton` (plan step) | Fill in `0_plan/plan.md`. |
| `1_data` empty or partial | `skeleton` (collect step) | Collect raw files and document them with `skills/skeleton/scripts/document_sources.py --data-dir 1_data/original`. |
| `2_db` not built, stale, or partial | `build-duckdb` | Run `skills/build-duckdb/scripts/build_duckdb.py --data-dir 1_data --out-dir 2_db`. |
| `3_analyses` empty, incomplete, or partial | `run-analysis` | Create or run analyses with `skills/run-analysis/scripts/run_analysis.py --db-dir 2_db --out-dir 3_analyses/<name>`. |
| `4_output` empty or partial | `render-quarto` | Render deliverables with `skills/render-quarto/scripts/render_quarto.py --out-dir 4_output/<name>`. |
| All stages complete | none | Report that the pipeline is complete. |

## Skeleton-specific wiring for render-quarto

When the pipeline reaches `4_output`, use the `render-quarto` skill to scaffold deliverables and then wire them to the analysis outputs.

1. Scaffold the deliverable:

   ```bash
   skills/render-quarto/scripts/render_quarto.py --create <type> --out-dir 4_output/<name>
   ```

2. Add a hidden setup cell near the top of the master `.qmd` file (e.g., `report.qmd`):

   ```python
   from pathlib import Path
   from skill_helpers.loaders import load_analysis, load_value, load_figure

   # Assumes the deliverable is rendered from its own Quarto project under 4_output/<name>/.
   ANALYSES_DIR = Path.cwd().parents[1] / "3_analyses"
   ```

3. Replace placeholder text, value boxes, tables, and figures in the master and included partials with calls to `load_analysis`, `load_value`, and `load_figure` using `ANALYSES_DIR`.

4. Render the deliverable:

   ```bash
   skills/render-quarto/scripts/render_quarto.py --out-dir 4_output/<name>
   ```

## Rules

- If the project is not initialized, propose running `init.py` before anything else.
- Always run `status.py` using `.venv/bin/python` after initialization.
- Always propose, never auto-run.
- Wait for the user to confirm before invoking a stage skill.
- If multiple stage skills look runnable, prefer the earliest incomplete stage.
- Do not modify files directly; delegate to the appropriate standalone skill.
