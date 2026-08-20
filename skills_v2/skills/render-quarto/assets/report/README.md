# Report template guidance

This is a single, flexible PDF report template. It can produce anything from a one-page memo to a long formal report by adjusting the layout flags, the table of contents, section numbering, and the set of chapter partials.

## Layout options

Set these in `_quarto.yml` under `metadata`:

- `inline-title: true` renders a compact title block at the top of the first page and uses a logo running header. `inline-title: false` (default) renders a standalone title page and uses the report title in the running header.
- `section-newpage: true` (default) starts each top-level section on a new page. Set to `false` for a continuous, memo-like flow.
- `toc` under `format: pdf:` turns the table of contents on or off.
- `number-sections` under `format: pdf:` turns section numbering on or off.

Other `format: pdf:` options (`geometry`, `fontsize`, etc.) can be tuned as needed.

## Choosing a configuration

Select layout options and sections based on the content, the audience, and how much navigation the reader needs. The section catalog below offers common building blocks; include only sections that carry meaningful content.

## Section catalog

Common building blocks:

- **Disclaimer** — caveats about data, AI assistance, methodology, and scope. Keep this as a standalone box, not a numbered section.
- **Executive Summary** — high-level overview and key takeaways. Use `{.unnumbered}`.
- **Context / Introduction** — objective, scope, and background.
- **Methodology** — data sources and analytical approach.
- **Results** — findings, figures, and tables loaded from analysis outputs.
- **Key Findings** — a concise findings section for short reports.
- **Discussion** — interpretation, implications, and limitations.
- **Conclusion** — summary and next steps.
- **Appendix** — detailed tables or extra material. Use `{.unnumbered}` and place a raw `\appendix` line in `report.qmd` before the include.

## Structure

The report is built from chapter partials under `sections/`, included by a root `report.qmd`:

```markdown
{{< include sections/_01_disclaimer.qmd >}}

{{< include sections/_02_executive_summary.qmd >}}

{{< include sections/_03_introduction.qmd >}}
```

Use leading underscores on partial file names so Quarto ignores them.

If an appendix is included, add `\appendix` before its include:

```markdown
\appendix

{{< include sections/_08_appendix.qmd >}}
```

## Building the report

1. Propose a set of chapters and subsections based on the section catalog above and the user's request. Confirm the final outline before writing files.
2. Create one partial under `sections/` for each chapter, named `_01_<slug>.qmd`, `_02_<slug>.qmd`, and so on. The leading underscore tells Quarto to ignore the file so it is not rendered on its own.
3. Write the chapter heading (`# Heading`) and any subsections (`## Subsection`) inside the partial. Preserve attributes such as `{.unnumbered}`.
4. The disclaimer partial should contain only the disclaimer box (no heading), since it is not a section.
5. Create a root-level `report.qmd` that includes the partials in order. The `render:` list under `project:` in `_quarto.yml` already points to `report.qmd`; do not change it.

## Cross-references

Use chapter-scoped labels so identifiers stay unique once partials are merged:

- Figures: `{#fig-<chapter-slug>-<name>}`
- Tables: `{#tbl-<chapter-slug>-<name>}`
- Sections: `{#sec-<chapter-slug>-<name>}`

Reference them with `@label`, e.g. `@fig-results-accuracy`.

## Example configurations

### Compact report

```yaml
metadata:
  inline-title: true
  section-newpage: false

format:
  pdf:
    toc: false
    number-sections: false
    geometry:
      - top=20mm
      - bottom=20mm
      - left=22mm
      - right=22mm
```

Sections: Context, Key Findings, Discussion, optional Disclaimer.

### Expanded report

```yaml
metadata:
  inline-title: false
  section-newpage: true

format:
  pdf:
    toc: true
    number-sections: true
    geometry:
      - top=25mm
      - bottom=25mm
      - left=25mm
      - right=25mm
```

Sections: Disclaimer, Executive Summary, Introduction, Methodology, Results, Discussion, Conclusion, optional Appendix.

## Shared files

- `_quarto.yml` holds shared metadata and PDF options.
- `preamble.tex` is included in the LaTeX header; it defines fonts, colors, boxes, and the `\brieftitle` command.
- `before-body.tex` is a template partial that renders either the inline title block or the full title page.
- `epfl_logo.png` is the logo used in the inline-title running header.
