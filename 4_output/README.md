# Stage 4: Output

## Goal

Create final deliverables from `3_analyses/*/results.json`.

## What Goes Here

- Dated deliverable folders such as `2026-02-18-short-report`
- Quarto files for reports, slides, or dashboards
- Optional export scripts and generated output files
- Shared templates and helpers

## Rules

- Never hardcode numbers in deliverables. Load them from `3_analyses/*/results.json`.
- Each deliverable should live in its own dated subfolder.
- Use the shared helpers from the deliverable folder:

```python
import sys

sys.path.insert(0, "..")
from helpers import load_analysis, load_figure, load_value
```

Render with `make render d=<folder>` or `make outputs`.

## Done When

The deliverable renders successfully and all reported numbers come from analysis outputs.
