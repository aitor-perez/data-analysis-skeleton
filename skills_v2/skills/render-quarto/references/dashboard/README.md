# Dashboard template guidance

## Structure

- Quarto dashboard project. Metadata and format options live in `_quarto.yml`; `dashboard.qmd` has no YAML frontmatter.
- Output: HTML dashboard using Quarto's dashboard format.
- Pages are created with top-level `#` headings. Each page becomes a navigation tab.
- Default pages: Overview, Details, About.

## Layout and metadata

Set shared metadata in `_quarto.yml` under `metadata:`:

- `title`: dashboard title.
- `subtitle`: optional subtitle.
- `author`: author name.
- `department`: department or unit.
- `email`: contact email.
- `date`: defaults to `today`.
- `lang`: language code, e.g. `en`.

Format and dashboard options (theme, orientation, logo, nav buttons) live under `format: dashboard:` and `plotly:` in the same file.

## Pages

`dashboard.qmd` is divided into `#` page sections:

- **Overview** — KPI value boxes, a main chart, and a summary table.
  - Value boxes are Python cells with `#| content: valuebox`.
  - The first `## Row {height=...}` contains the value boxes; a second row contains the chart and table.
- **Details** — a detailed table and a distribution or trend chart.
- **About** — disclaimers, data provenance, and refresh instructions.

Rows are created with `## Row {height=...}`; columns are created with `### Column Name {width=...}`.

## Placeholders to replace

- Title and other metadata in `_quarto.yml`.
- Value boxes currently show hardcoded placeholder numbers; replace them with values loaded from analysis outputs.
- Summary table and distribution chart placeholders.
- Disclaimer text.
- Logo (`epfl_logo.png`) and nav-button link if needed.

## Notes

- Uses Plotly's connected renderer (`notebook_connected`) to avoid embedding the full library inline.
- Uses `style.css` for custom theming.
