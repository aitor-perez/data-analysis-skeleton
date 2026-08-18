---
name: render-quarto
description: Use when the user wants to create or render a Quarto deliverable from a built-in template. Trigger on report, slides, dashboard, quarto, render, PDF, or HTML output.
---

# render-quarto

Create and render Quarto deliverables from built-in templates.

## When to use

Use this skill when the user asks for a new report, slide deck, or dashboard, or when they want to render an existing Quarto project. The skill is template-driven: it copies the template files, then runs `quarto render`.

## Workflow

1. Read this SKILL.md.
2. Read the reference README for the template you will scaffold (`references/<type>/README.md`).
3. Scaffold the deliverable with `render_quarto.py --create <type> --out-dir <dir>`.
4. For the `report` template, read `references/report/README.md`, infer a sensible configuration from the user's request and available context, propose it, and ask the user to confirm or adjust.
5. Apply the confirmed choices, create the section partials under `sections/` and the master `report.qmd`, then render with `render_quarto.py --out-dir <dir>`.

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

- With `--create`: copy the template infrastructure (`_quarto.yml`, preambles, styles, logos) into `--out-dir`. Never overwrite an existing `_quarto.yml` or supporting file. For the `report` template, propose a structure and layout based on the reference README, confirm with the user, then create the section partials under `sections/` and the master `report.qmd` file.
- Without `--create`: require a `_quarto.yml` in `--out-dir`, verify that `quarto` is on `PATH`, and run `quarto render <out-dir>` as a Quarto project.
- Fail fast if `--create` is not passed and `--out-dir` does not contain `_quarto.yml`.
- Fail fast if `quarto` is not installed when rendering.

## Templates

Read the reference README for the scaffolded template to learn its structure:

- `report` (`references/report/README.md`): flexible PDF report with configurable layout, TOC, numbering, and chapter set.
- `slides` (`references/slides/README.md`): Beamer presentation.
- `dashboard` (`references/dashboard/README.md`): HTML dashboard.

## Deliverable structure

Chapter partials live under `sections/` and are included by a root-level master file (`report.qmd`). Shared metadata (title, subtitle, author, department, email, date, language, layout options) lives in `_quarto.yml`. Chapter partials contain only section headings and content.

## How chapters are generated

The reference README's guidance is a starting proposal, not a rigid template. Always confirm the final outline with the user.

1. Extract the proposed chapters and subsections from the README and the user's request.
2. Present them as a numbered outline and ask the user for edits:
   - keep, remove, or merge chapters;
   - rename or reorder chapters;
   - promote or demote subsections.
3. Apply the user's edits and state the final outline back to them for confirmation.
4. Once confirmed, create a partial under `sections/` for each chapter, named `_01_<slug>.qmd`, `_02_<slug>.qmd`, and so on. The leading underscore tells Quarto to ignore the file so it is not rendered on its own.
5. Write the chapter heading (`# Heading`) and any subsections (`## Subsection`) inside the partial. Preserve attributes such as `{.unnumbered}`.
6. The disclaimer partial should contain only the disclaimer box (no heading), since it is not a section.
7. Create a root-level `report.qmd` that includes the partials in order using Quarto includes:

   ```markdown
   {{< include sections/_01_disclaimer.qmd >}}

   {{< include sections/_02_executive_summary.qmd >}}
   ```

8. If the template has an appendix, add a raw `\appendix` line in `report.qmd` before the appendix include.
9. The `render:` list under `project:` in `_quarto.yml` already points to `report.qmd`; do not change it.

## Cross-references

Use chapter-scoped labels so identifiers stay unique once partials are merged. Reference them with `@label`.

- Figures: `{#fig-<chapter-slug>-<name>}`
- Tables: `{#tbl-<chapter-slug>-<name>}`
- Sections: `{#sec-<chapter-slug>-<name>}`

For example, a figure in a chapter whose slug is `results` could be labeled `{#fig-results-accuracy}` and referenced as `@fig-results-accuracy`.

## Authoring guidance

After scaffolding a `report` template and confirming the outline with the user:

1. Fill in `_quarto.yml` with the shared metadata and the chosen layout options.
2. Create each chapter partial with the agreed headings and subsections.
3. Add content under the headings; do not hardcode numbers, figures, or tables. Load them dynamically from your analysis outputs.
