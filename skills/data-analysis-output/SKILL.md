---
name: data-analysis-output
description: Use when analysis results exist in 3_analyses/*/results.json and the user wants to create a report, slides, dashboard, or data export.
---

# data-analysis-output

Create and render final deliverables from analysis results.

## Responsibility

- Read `3_analyses/*/results.json`.
- Create a dated deliverable subfolder in `4_output/`.
- Copy the appropriate template folder into `4_output/<name>/`.
- Copy `helpers.py` to `4_output/helpers.py`.
- Render Quarto deliverables to PDF or HTML.
- For data exports, copy the `export/` template and wait for the user to edit it.

## How to use

1. Make sure analyses are complete.
2. Run the output script with a deliverable type and name:

   ```bash
   python <path-to-skills>/data-analysis-output/output.py --type report --name short-report
   ```

   Supported types:
   - `report`
   - `report-brief`
   - `slides`
   - `dashboard`
   - `export`

3. For Quarto deliverables, the skill renders automatically if Quarto is installed.
4. For `export`, the skill copies `export.py` and stops. Help the user edit it, then re-run the script manually or via this skill.

## Loading analysis results

Deliverables import shared helpers like this:

```python
import sys
sys.path.insert(0, "..")
from helpers import load_analysis, load_value, load_figure
```

## Rules

- Never hardcode numbers in deliverables. Load everything from `results.json`.
- Create one subfolder per deliverable.
- Copy `helpers.py` to `4_output/helpers.py` once, when creating the first deliverable.
- Copy the entire template folder into the deliverable folder.
- Do not create deliverables if no `results.json` files exist.
- Quarto must be installed for PDF/HTML rendering.
