---
name: render-quarto
description: Create and render Quarto deliverables from built-in templates.
---

# render-quarto

Create and render Quarto deliverables from built-in templates.

## Usage

```bash
# Create a deliverable from a template
python skills/render-quarto/scripts/render_quarto.py --create report --out-dir my_report

# Render an existing deliverable
python skills/render-quarto/scripts/render_quarto.py --out-dir my_report
```

## Inputs

- `--out-dir`: directory containing or receiving the Quarto project. Always required.
- `--create` (optional): template to instantiate (`report`, `report-brief`, `slides`, `dashboard`).

## Behavior

- With `--create`: copy the chosen template into `--out-dir` only if the target files do not already exist. Never overwrite an existing `_quarto.yml`, `.qmd`, or supporting file. Every template ships a `_quarto.yml` project file plus one or more `.qmd` files.
- Without `--create`: require a `_quarto.yml` in `--out-dir` and run `quarto render <out-dir>` as a Quarto project.
- Fail fast if `--create` is not passed and `--out-dir` does not contain `_quarto.yml`.

## Templates

- `report`: long PDF report with chapters and appendices.
- `report-brief`: short PDF report without table of contents.
- `slides`: Beamer presentation.
- `dashboard`: HTML dashboard.

## When invoked by the skeleton

Use `0_plan/plan.md` and `3_analyses/*/results.json` to decide which deliverables to create and what they should contain. The skeleton orchestrator wires the deliverable to load values and figures from `results.json` via `skeleton_helpers.loaders`. Scaffold with `--create`, edit the `.qmd` files, then render with the skill.

## When invoked standalone

Choose a template, scaffold it with `--create`, edit the `.qmd` files and `_quarto.yml` as needed, then render with the skill.
