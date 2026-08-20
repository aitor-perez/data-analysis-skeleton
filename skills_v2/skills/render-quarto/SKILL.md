---
name: render-quarto
description: Use when the user wants to create or render a Quarto deliverable from a built-in template. Trigger on report, slides, dashboard, quarto, render, PDF, or HTML output.
---

# render-quarto

Create and render Quarto deliverables from built-in templates.

## When to use

Use this skill when the user asks for a new report, slide deck, or dashboard, or when they want to render an existing Quarto project. The skill is template-driven: it copies the template infrastructure and generates the content files, then runs `quarto render`.

## Workflow

1. Read the template-specific README for the chosen template (`assets/<type>/README.md`).
2. Scaffold the deliverable with `render_quarto.py --create <type> --out-dir <dir>`.
3. Infer a sensible structure (sections, pages, or chapters) from the user's request, the template-specific README, and any available context.
4. Present the proposed outline to the user and ask for confirmation or edits:
   - keep, remove, or merge items;
   - rename or reorder items;
   - promote or demote subsections.
5. Confirm the final outline with the user.
6. Fill in `_quarto.yml` with the shared metadata and chosen layout options.
7. Create the content file(s) described in the template-specific README (e.g., `slides.qmd`, `dashboard.qmd`, or `report.qmd` with its `sections/` partials).
8. Add content under the headings; do not hardcode numbers, figures, or tables. Load them dynamically from your analysis outputs.
9. Render with `render_quarto.py --out-dir <dir>`.

## Usage

```bash
# Create a deliverable from a template
python skills/render-quarto/scripts/render_quarto.py --create report --out-dir my_report

# Render an existing deliverable
python skills/render-quarto/scripts/render_quarto.py --out-dir my_report
```

## Inputs

- `--out-dir`: directory containing or receiving the Quarto project. Always required.
- `--create` (optional): template to instantiate (`report`, `slides`, `dashboard`).

## Behavior

- With `--create`: copy the template infrastructure (`_quarto.yml`, preambles, styles, logos) into `--out-dir`. Never overwrite an existing `_quarto.yml` or supporting file. Then, based on the template-specific README, propose a structure and content outline, confirm with the user, and create the content file(s) (e.g., `slides.qmd`, `dashboard.qmd`, or `report.qmd` with its `sections/` partials).
- Without `--create`: require a `_quarto.yml` in `--out-dir`, verify that `quarto` is on `PATH`, and run `quarto render <out-dir>` as a Quarto project.
- Fail fast if `--create` is not passed and `--out-dir` does not contain `_quarto.yml`.
- Fail fast if `quarto` is not installed when rendering.

## Templates

Read the template-specific README for the scaffolded template to learn its structure:

- `report` (`assets/report/README.md`): flexible PDF report with configurable layout, TOC, numbering, and chapter set.
- `slides` (`assets/slides/README.md`): Beamer presentation.
- `dashboard` (`assets/dashboard/README.md`): HTML dashboard.

## Deliverable structure

Each template type defines its own deliverable structure. Shared metadata (title, subtitle, author, department, email, date, language, layout options) lives in `_quarto.yml`. The content file(s) and their organization are described in the template-specific README.

## Cross-references

Use chapter-scoped labels so identifiers stay unique once partials are merged. Reference them with `@label`.

- Figures: `{#fig-<chapter-slug>-<name>}`
- Tables: `{#tbl-<chapter-slug>-<name>}`
- Sections: `{#sec-<chapter-slug>-<name>}`

For example, a figure in a chapter whose slug is `results` could be labeled `{#fig-results-accuracy}` and referenced as `@fig-results-accuracy`.
