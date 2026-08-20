# Slides template guidance

## Structure

- Quarto Beamer project. Metadata and format options live in `_quarto.yml`; `slides.qmd` has no YAML frontmatter.
- Output: PDF slides via `pdf-engine: lualatex`.
- Top-level `##` headings define frame groups/sections: Context, Disclaimer, Data, Key Findings, Details, Conclusion.
- The title page is rendered by the custom Beamer template in `preamble.tex`.

## Layout and metadata

Set shared metadata in `_quarto.yml` under `metadata:`:

- `title`: presentation title.
- `subtitle`: optional subtitle.
- `author`: presenter name.
- `institute`: department or unit.
- `date`: defaults to `today`.
- `lang`: language code, e.g. `en`.

Format options (theme, aspect ratio, fonts, etc.) live under `format: beamer:` in the same file.

## Sections

`slides.qmd` is divided into `##` sections. The default sections are:

- **Context** — what the project is about and which question it answers.
- **Disclaimer** — caveats about data, AI assistance, and scope, rendered in a `disclaimerbox`.
- **Data** — data sources and transformations.
- **Key Findings** — main results loaded from analysis outputs.
- **Details** — supporting tables, figures, or additional results.
- **Conclusion** — summary and next steps.

## Placeholders to replace

- Title, subtitle, author, and institute in `_quarto.yml`.
- Bullet placeholder text in each section.
- Disclaimer items.
- Commented Python code that loads analysis results.

## Notes

- Uses `preamble.tex` for Beamer formatting, fonts, colors, and the title page layout.
- The logo path is set by `\graphicspath{{./}}` in `_quarto.yml`; replace `epfl_logo.png` if needed.
- Figures and tables can be included from analysis outputs.
