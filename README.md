# Data Analysis Skeleton

A structured pipeline for data analysis projects.

```
0_plan  ->  1_data  ->  2_db  ->  3_analyses  ->  4_output
```

## Getting Started

```bash
pip install -r requirements.txt
cp .env.example .env       # fill in your API keys
```

## Stage Docs

- [`0_plan/README.md`](0_plan/README.md)
- [`1_data/README.md`](1_data/README.md)
- [`2_db/README.md`](2_db/README.md)
- [`3_analyses/README.md`](3_analyses/README.md)
- [`4_output/README.md`](4_output/README.md)

## Make Commands

```bash
make status                     # Show pipeline status and validation
make db                         # Build the DuckDB from 1_data/
make analyses                   # Run all analysis scripts
make render d=<folder>          # Render a specific deliverable in 4_output/
make outputs                    # Render all deliverables
make all                        # Full pipeline: db → analyses → outputs
make clean                      # Remove generated files
```

## Prerequisites

- Python 3.10+
- [Quarto](https://quarto.org/docs/get-started/) (for rendering reports/slides)
- LuaLaTeX (e.g., TeX Live or MacTeX)
