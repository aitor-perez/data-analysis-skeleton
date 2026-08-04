# Data Analysis Skills Catalog

OpenCode skills for running the data-analysis pipeline in any project directory.

This catalog replaces the `data-analysis-skeleton` repository as a cloneable template. Instead of cloning the skeleton for every project, install the catalog once and invoke individual skills inside the project you are working on.

## Installation

Add the plugin to the `plugin` array in your global or project-level `opencode.json`:

### Global install (recommended)

Edit `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["data-analysis-skills@git+https://github.com/<org>/data-analysis-skills.git"]
}
```

This makes the skills available in every project.

### Project-level install

Create or edit `opencode.json` in a project directory:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["data-analysis-skills@git+https://github.com/<org>/data-analysis-skills.git"]
}
```

This makes the skills available only in that project.

### Development install

For local development, clone or symlink this repository and point `opencode.json` at the absolute local path:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["/path/to/data-analysis-skills"]
}
```

Restart OpenCode after editing the config. The plugin registers the skills directory automatically; no symlinks or manual config are needed.

Verify by listing available skills:

```
use skill tool to list skills
```

## Skills

| Skill | Responsibility |
|---|---|
| `data-analysis` | Orchestrator. Inspects pipeline state, initializes new projects, and proposes the next step. |
| `data-analysis-plan` | Create and fill `0_plan/plan.md`. |
| `data-analysis-collect` | Document raw files in `1_data/original/sources.yaml`. |
| `data-analysis-transform` | Run heavy enrichment in `1_data/transformed/<name>/`. |
| `data-analysis-build-db` | Build `2_db/project.duckdb` and generate `schema.md`. |
| `data-analysis-analyze` | Create and run analyses in `3_analyses/`. |
| `data-analysis-output` | Render deliverables in `4_output/` from analyses. |
| `data-analysis-clean` | Remove generated files while preserving raw data and scripts. |

## Usage

Invoke the orchestrator explicitly with OpenCode's native `skill` tool:

```
use skill tool to load data-analysis
```

The orchestrator will initialize a new project if needed, then guide you through the pipeline. You can also invoke a stage skill directly:

```
use skill tool to load data-analysis-plan
```

## Pipeline

```
0_plan -> 1_data -> 2_db -> 3_analyses -> 4_output
```

See each skill's `SKILL.md` for detailed instructions.
