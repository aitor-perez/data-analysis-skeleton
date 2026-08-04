---
name: data-analysis-plan
description: Use when 0_plan/plan.md is missing or still contains placeholder text.
---

# data-analysis-plan

Create and fill `0_plan/plan.md` for the current project.

## Responsibility

- Create `0_plan/plan.md` from the template if it does not exist.
- Validate the plan and identify any remaining placeholder sections.
- Guide the user through each placeholder section and write their answers into `plan.md`.
- Re-validate until the plan is complete.

## How to use

1. Run the plan script from the project root using the project's Python:

   ```bash
   .venv/bin/python <path-to-skills>/data-analysis-plan/plan.py
   ```

2. Read the output.
   - If the plan is complete, report that to the user.
   - If placeholders remain, ask the user for content section by section.
3. For each placeholder section, ask the user a focused question based on the placeholder prompt.
4. Rewrite the section in `0_plan/plan.md` with the user's answer, replacing the placeholder line.
5. Re-run `plan.py` to confirm all placeholders are resolved.

## Placeholder rule

A placeholder is any line that:
- Starts and ends with underscores (`_`).
- Ends with a question mark (`?`).

Example from the template:

```markdown
*What question are we answering? What is the goal of this analysis?*
```

## Sections in the template

- **Objective**: What question are we answering? What is the goal?
- **Audience**: Who will read the output?
- **Input Data**: What data do we need, where does it come from, and in what format?
- **Transformations**: What cleaning, normalization, or enrichment is needed?
- **Analyses**: What questions will we answer and what calculations are needed?
- **Output Format**: Report, slides, dashboard, export?
- **Scientific Framework**: Is there a theoretical framework?
- **Known Risks & Limitations**: What could go wrong?

## Rules

- Do not use LLM to draft content unless the user explicitly asks.
- Ask one section at a time.
- Preserve the markdown structure and section headers.
- Do not proceed to `data-analysis-collect` until the plan is complete.
