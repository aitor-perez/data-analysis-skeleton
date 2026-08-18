# Dashboard template guidance

## Structure

- HTML dashboard using Quarto's dashboard format.
- Pages: Overview, Details, About.
- Overview contains value boxes, a main chart, and a summary table.
- Details contains a detailed table and a distribution chart.
- About contains disclaimers and metadata.

## Placeholders to replace

- Dashboard title in the YAML front matter.
- Value boxes currently show hardcoded placeholder numbers; replace them with values loaded from analysis outputs.
- Summary table and distribution chart placeholders.
- Disclaimer text.

## Notes

- Uses Plotly's connected renderer (`notebook_connected`) to avoid embedding the full library inline.
- Uses `style.css` and `epfl_logo.png`.
- Each top-level `#` heading becomes a navigation tab.
