# Agent Instructions

You are assisting with a data analysis project that follows a structured pipeline. Read this document carefully before doing any work.

## Pipeline Overview

The project is organized into 5 stages. Data flows forward only — never skip a stage or create backward dependencies.

```
0_plan  →  1_data  →  2_db  →  3_analyses  →  4_output
```

| Stage | Reads from | Produces | Format |
|-------|-----------|----------|--------|
| `0_plan/` | (nothing) | plan.md, decisions.md | Markdown |
| `1_data/` | External sources | Raw data files + sources.yaml | CSV, JSON, XLSX, etc. |
| `2_db/` | `1_data/*` | `project.duckdb` + `schema.md` | DuckDB + Markdown |
| `3_analyses/` | `2_db/project.duckdb` | `results.json` + optional figures per subfolder | JSON + PDF/PNG |
| `4_output/` | `3_analyses/*/results.json` | Report, slides, dashboard, or data export | Quarto → PDF/HTML, or Python → CSV/XLSX/JSON |

## General Rules

- **Language**: Python. Use Pandas unless instructed otherwise.
- **Coding style**: Write concise, flat scripts. No `if __name__ == "__main__"`. Minimize functions — use them only when they genuinely reduce repetition. Top-level procedural code is preferred.
- **API keys**: Never hardcode API keys. Use a `.env` file with `python-dotenv`. See `.env.example` for the template.
- **Dependencies**: All Python dependencies go in `requirements.txt` at the root.
- **Skeleton improvements**: When you modify a generic file that could benefit future projects (agents.md, Makefile, helpers.py, templates, READMEs), stage the files and run `make skeleton-sync msg="description"`. This commits with a `[skeleton]` prefix and automatically pushes the change to the skeleton remote (if configured). Example: `git add agents.md && make skeleton-sync msg="improve JSON schema documentation"`.
- **Pipeline status**: Run `make status` (or `python status.py`) at the start of any conversation to instantly see which stages are complete, which have issues, and what the next action should be. This is faster and more reliable than manually checking files.
- **Stage gates**: Before starting work in any stage, verify that prerequisite stages are complete (use `make status`). If `plan.md` still has placeholders, don't start collecting data. If `sources.yaml` is missing entries for files in `1_data/`, don't build the DB or run analyses. If documentation or provenance is unclear, **stop and ask the user to fill the gaps before proceeding**. Never skip a stage just because the user is eager to move forward.
- **Writing style**: Never use em dashes (--) in reports, slides, or any written output. Use commas, parentheses, colons, or separate sentences instead.
- **When in doubt, ask.** You are a collaborator, not an autopilot. If something is ambiguous, if you need to make a judgment call that could go either way, or if you're about to silently discard or transform data, stop and ask the user. It is always better to ask one question too many than to make a wrong assumption that propagates through the pipeline. Never guess on decisions that affect data quality, analysis scope, or interpretation.

### Shared Utilities

- Reusable helpers live in `utils/` at the project root. See `utils/README.md` for available modules and usage examples.
- When calling the RCP LLM endpoint, use `utils.rcp` rather than writing raw `requests` calls in each project script.
- Keep utilities generic and small. Move only reusable code there, keep dataset-specific schemas, payload construction, and output shaping in the script that uses the utility.
- When adding a new utility, document it in `utils/README.md` and add any new dependencies to `requirements.txt`.
- Import from stage scripts by adding the project root to `sys.path`, based on `__file__` rather than the current working directory. Examples: from `2_db/build_db.py`, use `from pathlib import Path; import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))`; from `3_analyses/my_analysis/run.py`, use `from pathlib import Path; import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[2]))`.

---

## Stage 0: Plan (`0_plan/`)

**Goal**: Define the project before writing any code.

**How to detect you're in Stage 0**: Check `0_plan/plan.md`. If it still contains placeholder text (italicized prompts like _What question are we answering?_), the plan is incomplete. Also check whether `2_db/project.duckdb` exists — if not, the project hasn't moved past planning.

### Two phases

#### Phase 1: Brainstorming (free-form)

The user may open multiple conversations to explore ideas. During this phase:

- Engage naturally. Help the user think through their project idea.
- Ask clarifying questions, suggest approaches, challenge assumptions.
- **Don't pressure to fill in `plan.md`** — the user is still thinking.
- **Don't try to record everything** — conversations are ephemeral by design. The user will start fresh sessions and that's fine.

#### Phase 2: Consolidation (structured)

When the user signals they're ready — or when you sense the idea is mature enough — switch to consolidation:

1. **Summarize** your understanding of the project in a few sentences.
2. **Ask for confirmation**: "Does this overall direction look right?"
3. **Once confirmed**, read `0_plan/plan.md` and systematically identify which sections are still empty or placeholder.
4. **Ask targeted questions** for each gap — don't ask everything at once, go section by section.
5. **Fill in `plan.md`** with the agreed answers.

The user can trigger consolidation explicitly (e.g., "let's finalize the plan") or you can suggest it when the conversation has covered enough ground.

### Files

- `plan.md` — The project plan. Starts as a template; complete it during Phase 2.
- `decisions.md` — Decision log. Update throughout the project (not just Stage 0).

**When to update the plan**: If later stages reveal that the original plan doesn't work (wrong data, unexpected results), update `plan.md` and log the decision in `decisions.md`.

---

## Stage 1: Data Collection (`1_data/`)

**Goal**: Gather all raw data needed for the project.

**How to detect you're in Stage 1**: `0_plan/plan.md` is complete (no placeholder text), but `1_data/` has no actual data files yet — or has some but not all files listed in the plan's "Input Data" section.

### What the agent should do

1. **Read the plan**: Start by reading `0_plan/plan.md`, especially the "Input Data" section, to know what data is needed.
2. **Help collect**: Depending on the situation:
   - If the user drops files into `1_data/` manually, help document them in `sources.yaml`.
   - If data comes from an API, write a collection script in `1_data/` (e.g., `fetch_*.py`).
   - If the user needs help finding data, suggest sources based on the plan.
3. **Document everything**: After each file is added, update `sources.yaml` with its provenance.
4. **Check completeness**: Cross-reference the plan's "Input Data" table with what's actually in `1_data/`. Flag anything missing.

### Rules

- Every data file must be documented in `sources.yaml` with: filename, origin, URL (if applicable), date accessed, description, format, and `confidential` flag.
- **Confidentiality**: All data is public by default (`confidential: false`). If a file is confidential (`confidential: true`), it must be added to both `.gitignore` (so it is never committed) and `.cursorignore` (so the AI agent cannot read it). The `sources.yaml` entry itself is still committed — only the data file is excluded and hidden from the agent.
- Raw data is committed to git (unless too large or confidential — in either case, document how to obtain it and add a download script in `1_data/`).
- Never modify raw data files after collection. All transformations happen in `2_db/`.
- If data comes from an API or database, write a collection script in `1_data/` and document it in `sources.yaml`.

### When is Stage 1 done?

Every data source listed in the plan has a corresponding file in `1_data/` and an entry in `sources.yaml`. This is enforced — the agent will refuse to proceed to later stages if documentation is incomplete. Then move to `2_db/`.

---

## Stage 2: Database (`2_db/`)

**Goal**: Transform raw data into a clean, queryable DuckDB database.

### What the agent should do

1. **Read the plan and data**: Start by reading `0_plan/plan.md` and inspecting the files in `1_data/` to understand what's expected.
2. **Flag data quality issues**: If you notice duplicates, missing values, encoding problems, or unexpected formats, report them to the user before silently cleaning them. Ask how they want to handle each issue.
3. **Confirm naming and structure**: If column names in the raw data are ambiguous, or if you need to decide how to normalize or split tables, propose your approach and ask for confirmation.
4. **Document decisions**: Log any non-trivial transformation choices in `0_plan/decisions.md`.

### Rules

- The output is always a single file: `project.duckdb`.
- The build script is `build_db.py`. It reads from `1_data/`, applies all transformations, and writes the DuckDB.
- Transformations include: importing raw files, cleaning text, normalizing values, computing derived columns (embeddings, categories, etc.), creating lookup tables.
- After building, auto-generate `schema.md` documenting all tables, columns, and types.
- The DuckDB is not committed to git (it's in `.gitignore`). It is rebuilt with `make db` or `python 2_db/build_db.py`.

**Important**: `schema.md` is the contract between `2_db/` and `3_analyses/`. Always keep it up to date. When the LLM writes SQL queries in `3_analyses/`, it should reference `schema.md` to know the exact table and column names.

---

## Stage 3: Analyses (`3_analyses/`)

**Goal**: Answer analytical questions by querying the DuckDB and producing structured JSON outputs.

**How to detect you're in Stage 3**: `2_db/project.duckdb` exists and `2_db/schema.md` has real content (not just the placeholder). The plan's "Analyses" section lists questions that haven't been answered yet (no corresponding subfolder in `3_analyses/`, or subfolder exists but has no `results.json`).

### Pre-flight check

Before writing or running any analysis, verify:

1. **Plan exists**: `0_plan/plan.md` is filled in (no placeholder text).
2. **Data is documented**: Every data file in `1_data/` has a corresponding entry in `sources.yaml` with origin, date, and description. If any file is undocumented or provenance is unclear, **stop and ask the user to complete `sources.yaml` before proceeding**.
3. **DB is built**: `2_db/project.duckdb` exists. Read `2_db/schema.md` to understand available tables, columns, and types -- this is your SQL reference for all queries.

Do not skip these checks. Incomplete provenance upstream makes analysis results unreliable and unreproducible.

### What the agent should do

#### First entry (no analyses exist yet)

When `3_analyses/` has no subfolders with `results.json` (only `example_analysis/` or empty), the agent should proactively bootstrap the analysis stage:

1. **Read the inputs**: Read `0_plan/plan.md` (especially the "Analyses" section) and `2_db/schema.md` to understand what questions need answering and what data is available.
2. **Propose a batch of analyses**: Based on the plan and schema, propose a list of analyses to the user: subfolder name, short description, the SQL query, and whether a figure would add value. Present this as a checklist for the user to confirm, adjust, or extend.
3. **Ask when in doubt**: If a question from the plan is ambiguous or doesn't map clearly to the schema, ask the user rather than guessing.
4. **Generate all confirmed analyses**: Create all subfolders with their `run.py` scripts, run them, and produce the `results.json` files. Include figures where they help (distributions, trends, comparisons).
5. **Leave interpretation for review**: Fill in `interpretation` with a first attempt, but flag it for the user to review. Some interpretations require domain knowledge the agent may not have.

This first batch is a starting point. Some analyses will be refined, some discarded, and new ones added through interaction. That is expected.

#### Subsequent visits (some analyses exist)

1. **Check completeness**: Cross-reference the plan's "Analyses" list with existing subfolders. Flag any gaps.
2. **Refine on request**: If the user asks to adjust an existing analysis (new filter, different grouping), update it in place.
3. **Handle schema changes**: If `2_db/schema.md` has changed, check which queries might be affected and re-run them.
4. **New questions**: If the user asks a new question, create a new subfolder.

### Structure

Each analysis lives in its own subfolder:

```
3_analyses/
  value_frequency/
    run.py              # Script: queries DB, writes results.json + optional figures
    results.json        # Output: structured JSON (see schema below)
    figures/            # Optional: figures generated by run.py
      bar_chart.pdf
  schein_levels/
    run.py
    results.json
  ...
```

### The JSON Contract

Every `results.json` must follow this schema:

```json
{
  "query": "SELECT ... FROM ...",
  "n_results": 38,
  "results": [
    {"col1": "value1", "col2": 123},
    {"col1": "value2", "col2": 456}
  ],
  "description": "Short sentence: what this analysis does",
  "interpretation": "Short sentence: what the results mean",
  "figures": [
    {
      "file": "figures/bar_chart.pdf",
      "caption": "What this figure shows"
    }
  ]
}
```

Fields:
- `query`: The exact SQL query used. Must be valid against the current `schema.md`.
- `n_results`: Number of rows in `results`.
- `results`: Array of objects — the raw query output in JSON format.
- `description`: One sentence explaining what we tried to do (in English).
- `interpretation`: One sentence interpreting the results (in English). Can be left empty initially and filled after reviewing.
- `figures`: Array of figure references (empty `[]` if no figures). Each entry has `file` (relative path) and `caption`.

### Rules for Analysis Scripts (`run.py`)

- Always connect to the DuckDB with `read_only=True`: `con = duckdb.connect("../../2_db/project.duckdb", read_only=True)`
- The script should be runnable from its own subfolder: `cd 3_analyses/my_analysis && python run.py`
- Output `results.json` in the same subfolder.
- If the DB schema changes, the query may break or return different results. In that case, update the query and re-run the script.
- Keep scripts concise and flat. No `if __name__ == "__main__"`.

### Rules for Figures

- Figures go in a `figures/` subfolder within the analysis folder.
- A figure must use the same data as the JSON results (or a subset). Never fetch additional data for a figure that isn't in the JSON.
- Every figure must be referenced in the `figures` array of `results.json`.
- Prefer PDF for vector graphics, PNG for raster.

### When to Create a New Analysis vs. Update an Existing One

- **New subfolder**: when answering a new question. Use descriptive `snake_case` names.
- **Update existing**: when refining the same question (adding a filter, changing a grouping).
- **Never delete**: if an analysis is superseded, rename the folder with a `_deprecated_` prefix.

### When is Stage 3 done?

Every analysis question listed in the plan has a corresponding subfolder with a valid `results.json`. Interpretations have been reviewed (either filled by the agent and confirmed by the user, or filled by the user directly). Then move to `4_output/`.

---

## Stage 4: Output (`4_output/`)

**Goal**: Produce final deliverables (reports, slides, dashboards, or data exports).

A single project may have multiple deliverables (e.g. a short report, a full report, preliminary slides, final slides, a data export for another system). Each deliverable lives in its own **dated subfolder** inside `4_output/`.

There are two types of deliverables:
- **Quarto documents** (report, slides, dashboard): rendered from `.qmd` files into PDF or HTML.
- **Data exports** (CSV, Excel, JSON): generated by `export.py` scripts when the final output is just processed data.

**How to detect you're in Stage 4**: The user signals that analyses are sufficient and they want to produce a deliverable (e.g., "let's create the report", "I think we have enough data for the slides"). `3_analyses/` has subfolders with valid `results.json` files.

### Directory Structure

```
4_output/
  helpers.py                        # shared Python helper (at root)
  templates/
    report.qmd                      # starter Quarto template for reports
    slides.qmd                      # starter Quarto template for slides
    dashboard.qmd                   # starter Quarto template for dashboards
    export.py                       # starter Python template for data exports
    report/                         # shared LaTeX files for reports
      preamble.tex
      titlepage.tex                 # default title page (copied into each deliverable)
      epfl_logo.png
    slides/                         # shared LaTeX files for slides
      preamble.tex
      epfl_logo.png
    dashboard/                      # shared assets for dashboards
      style.css                     # modern colorful theme (indigo navbar, tinted accents, clean cards)
      epfl_logo.png
  2026-02-18-short-report/          # ← Quarto deliverable (example)
    report.qmd
    titlepage.tex                   # customized copy
    report.pdf
  2026-03-01-final-slides/          # ← another Quarto deliverable
    slides.qmd
    slides.pdf
  2026-03-05-overview-dashboard/    # ← another Quarto deliverable
    dashboard.qmd
    dashboard.html
  2026-03-10-client-export/         # ← data export deliverable
    export.py
    README.md                       # documents the export contents
    data_export.csv
```

### What the agent should do

1. **Ask which deliverable**: Report, slides, dashboard, or data export? Don't create multiple at once. Start with what the user asks for.
2. **Ask for the folder name**: Propose a name like `YYYY-MM-DD-short-description` (e.g. `2026-02-18-short-report`). If unsure, **ask the user** what to call it. Do not guess.
3. **Create the subfolder**: Copy the appropriate template into the new subfolder:
   - Report: `templates/report.qmd` + `templates/report/titlepage.tex`
   - Slides: `templates/slides.qmd`
   - Dashboard: `templates/dashboard.qmd` + `templates/dashboard/epfl_logo.png`
   - Data export: `templates/export.py`
4. **Review available data**: Read all `results.json` files in `3_analyses/` to understand what data is available. Also read `0_plan/plan.md` for context (objective, audience, output format).
5. **Propose a structure**: Based on the available analyses and the plan, propose an outline (for Quarto) or describe what the export will contain (for data exports). Present it to the user for confirmation.
6. **Write the deliverable**: Fill in the `.qmd` or `export.py` file using `load_analysis()` and `load_figure()` to pull data from `3_analyses/`. Never hardcode numbers.
7. **Fill gaps autonomously**: If while writing you notice simple data is missing (a count, a percentage, a breakdown derivable from the existing schema), go create a new analysis in `3_analyses/` (subfolder + `run.py`), run it, and use the results. No need to ask permission for straightforward queries. For complex or ambiguous questions, ask the user first.
8. **Customize the title page**: For reports, edit the local `titlepage.tex` with the project's title, author, and branding.
9. **Add README for exports**: For data exports, create a `README.md` documenting the output file contents (columns, source analyses, how to regenerate).

### Creating a New Deliverable (step by step)

**Report:**
```bash
mkdir -p 4_output/2026-02-18-short-report
cp 4_output/templates/report.qmd 4_output/2026-02-18-short-report/report.qmd
cp 4_output/templates/report/titlepage.tex 4_output/2026-02-18-short-report/titlepage.tex
make render d=2026-02-18-short-report
```

**Slides:**
```bash
mkdir -p 4_output/2026-03-01-final-slides
cp 4_output/templates/slides.qmd 4_output/2026-03-01-final-slides/slides.qmd
make render d=2026-03-01-final-slides
```

**Dashboard:**
```bash
mkdir -p 4_output/2026-03-05-overview-dashboard
cp 4_output/templates/dashboard.qmd 4_output/2026-03-05-overview-dashboard/dashboard.qmd
cp 4_output/templates/dashboard/epfl_logo.png 4_output/2026-03-05-overview-dashboard/epfl_logo.png
make render d=2026-03-05-overview-dashboard
```

**Data Export:**
```bash
mkdir -p 4_output/2026-03-10-client-export
cp 4_output/templates/export.py 4_output/2026-03-10-client-export/export.py
# Edit export.py to load and combine analyses
make render d=2026-03-10-client-export
```

### The Golden Rule

**Never write a number directly in a Quarto document.** Every number, count, percentage, or statistic must be loaded from a `results.json` in `3_analyses/`. If the data you need doesn't exist as a JSON, go back to `3_analyses/` and create a new analysis first. For simple, obvious queries you can do this autonomously without asking.

### Loading Data

`helpers.py` lives at the root of `4_output/`. Since each deliverable runs from a subfolder, the first Python chunk must add the parent to `sys.path`:

```python
import sys; sys.path.insert(0, "..")
from helpers import load_analysis, load_figure, load_value

data = load_analysis("value_frequency")
# data["results"] → list of dicts
# data["n_results"] → int
# data["interpretation"] → string

fig_path = load_figure("value_frequency", "bar_chart.pdf")

# For dashboards: extract a single scalar for value boxes
total = load_value("value_frequency", "count", agg="sum")
```

### Path Conventions

All paths in `.qmd` files are **relative to the deliverable subfolder**:

- Shared LaTeX preambles: `../templates/report/preamble.tex` or `../templates/slides/preamble.tex`
- Local title page: `titlepage.tex` (in the same subfolder)
- `\graphicspath` is set via `header-includes` in each `.qmd` to resolve images from `../templates/report/` (or `../templates/slides/`) and `./`.
- Python helper: `sys.path.insert(0, "..")` then `from helpers import ...`

### Report Structure and Conventions

The `templates/report.qmd` template provides a standard structure. Follow these conventions:

1. **Disclaimer box** (`disclaimerbox`): Start every report with an orange disclaimer box flagging data limitations, AI usage, methodological choices, and scope. Adapt the items to the project.
2. **Executive Summary** (unnumbered): A short overview with a `reportbox` highlighting key findings.
3. **Body sections** (numbered): Introduction, Methodology, Results, Discussion, Conclusion.
4. **Appendices** (unnumbered): Put detailed or large data tables in appendices. Reference them from the main text with `\mbox{Table~\ref{tab:label}}`. The main text should tell the story; the appendix holds the evidence.
5. **Document quotes** (`docquote`): When quoting source documents, use the `docquote` environment with the exact quote in italics, followed by attribution (document name, year) and an optional category label.
6. **Tables**: Use booktabs style (`\toprule`, `\midrule`, `\bottomrule`). Always include `\caption` and `\label`. Use `[H]` placement.
7. **Figures**: Generated in `3_analyses/`, referenced via `load_figure()`. Always `[H]` placement with caption and label. Prefer PDF for vector graphics.

### Slides Structure and Conventions

The `templates/slides.qmd` template provides a standard starting point. Follow these conventions:

1. **Disclaimer slide** (`disclaimerbox`): Include a disclaimer slide near the beginning of every presentation (typically right after the context/introduction slide). Use the orange `disclaimerbox` environment to flag data limitations, AI usage, methodological choices, and scope. Keep bullet points short and adapted to the project.
2. **One idea per slide**: Each slide should communicate a single point. Avoid dense text.
3. **Figures**: Generated in `3_analyses/`, referenced via `load_figure()`. Always include a caption or descriptive subtitle.
4. **Tables**: Use booktabs style (`\toprule`, `\midrule`, `\bottomrule`). Keep tables small (max 5-6 rows) to fit on a slide.

### Dashboard Structure and Conventions

The `templates/dashboard.qmd` template produces an interactive HTML dashboard. Follow these conventions:

1. **Pages** (`#` headings): Each top-level heading creates a navigation tab. Use "Overview" for the landing page and "About" for disclaimers and metadata.
2. **Rows and columns** (`##` headings): Organize cards in rows. Use `{height=...}` to control row proportions and `{width=...}` on cards within a row.
3. **Cards** (`###` headings): Each card contains one thing: a value box (KPI), a chart, or a table. Keep cards focused.
4. **Value boxes**: Use `#| content: valuebox` in Python chunks to display large KPI numbers. Use `load_value()` from helpers to extract scalars.
5. **Disclaimer**: Include an "About" page with a `.disclaimer-box` div for data caveats (mirrors the report/slides disclaimer boxes).
6. **No hardcoded numbers**: Same golden rule as reports. Every number comes from `results.json`.
7. **Interactive plots**: Since dashboards are HTML, prefer interactive libraries (plotly, altair) over static matplotlib when it adds value.
8. **CSS theme**: The `templates/dashboard/style.css` provides a modern, colorful theme (indigo navbar, tinted accents, clean cards). The theme path in the YAML uses `templates/dashboard/style.css` (relative to `4_output/`, resolved at render time from the deliverable subfolder).

When creating a dashboard deliverable, update the theme path in the YAML to point correctly from the subfolder:
```yaml
theme: [default, ../templates/dashboard/style.css]
```

### Data Export Structure and Conventions

Use data exports when the final deliverable is a data file (CSV, Excel, JSON) rather than a formatted document. Common use cases:
- Feeding processed data into another system or pipeline
- Providing a clean dataset for stakeholders who will do their own analysis
- Creating a machine-readable output alongside a human-readable report

Each data export subfolder contains:

1. **`export.py`**: The script that loads analyses and writes the output file. Same golden rule applies: never hardcode data, load everything from `3_analyses/*/results.json`.
2. **`README.md`**: Documents what the export contains (columns, source analyses, how to regenerate). Since there's no rendered document with context, this README is essential.
3. **Output file(s)**: The generated CSV, Excel, or JSON file(s).

Example `README.md` for a data export:

```markdown
# Client Data Export - 2026-03-10

## Contents
- `data_export.csv`: Processed frequency analysis for client integration

## Columns
- `category`: The value category
- `count`: Number of occurrences
- `percentage`: Relative frequency

## Source Analyses
- `3_analyses/value_frequency/`
- `3_analyses/schein_levels/`

## Regenerate
Run `python export.py` from this folder, or `make render d=2026-03-10-client-export` from root.
```

### Shared Templates

- `templates/report.qmd` — Starter Quarto template for PDF reports.
- `templates/report/preamble.tex` — LaTeX preamble with colors, tcolorbox environments (`disclaimerbox`, `reportbox`, `docquote`), and package imports.
- `templates/report/titlepage.tex` — Default title page (copy into each report deliverable subfolder and customize).
- `templates/slides.qmd` — Starter Quarto template for PDF slides.
- `templates/slides/preamble.tex` — Beamer preamble with modern minimal theme, plus `disclaimerbox` environment.
- `templates/dashboard.qmd` — Starter Quarto template for HTML dashboards.
- `templates/dashboard/style.css` — CSS theme for dashboards with a modern, colorful design (indigo navbar, tinted value box accents, clean card layout).
- `templates/dashboard/epfl_logo.png` — Logo for the dashboard navbar.
- `templates/export.py` — Starter Python template for data exports (CSV, Excel, JSON).

Reusable template improvements should be committed with `make skeleton-sync`.

### Rendering

```bash
# Render a specific deliverable
make render d=2026-02-18-short-report

# Render all deliverables
make outputs

# Or manually
cd 4_output/2026-02-18-short-report && quarto render report.qmd
```

---

## Orchestration (Makefile)

The `Makefile` at the root provides shortcuts:

```bash
make status                          # Show pipeline status and validation
make db                              # Rebuild DuckDB from 1_data/
make analyses                        # Run all run.py scripts in 3_analyses/
make render d=2026-02-18-report      # Render a specific deliverable in 4_output/
make outputs                         # Render all deliverables in 4_output/
make all                             # Run the full pipeline: db → analyses → outputs
make clean                           # Remove generated files
make skeleton-sync msg="description" # Commit + push skeleton improvements
```

---

## Troubleshooting Checklist

If something breaks, check in this order:

1. **Report shows wrong numbers?** → Re-run the analysis (`make analyses`), then re-render (`make render d=<folder>`).
2. **Analysis query fails?** → Check `2_db/schema.md` — did the DB schema change? Update the query in `run.py`.
3. **DB build fails?** → Check that raw data in `1_data/` hasn't changed format. Update `build_db.py`.
4. **Missing data for the report?** → Create a new analysis subfolder in `3_analyses/`. Never hardcode.
5. **API key error?** → Check `.env` file exists and has the right keys. See `.env.example`.
6. **Can't find helpers.py?** → Make sure the first Python chunk has `import sys; sys.path.insert(0, "..")`.