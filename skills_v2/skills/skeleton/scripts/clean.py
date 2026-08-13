# clean.py — Remove generated pipeline artifacts
# Run from the project root:
#   .venv/bin/python <path-to-catalog>/skills/skeleton/scripts/clean.py
# Use --yes to actually delete:
#   .venv/bin/python <path-to-catalog>/skills/skeleton/scripts/clean.py --yes

import argparse
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Remove generated pipeline artifacts.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current working directory).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Actually delete files. Without this flag, only list what would be deleted.",
    )
    return parser.parse_args()


def remove(path):
    """Remove a file or directory tree."""
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        for child in path.iterdir():
            remove(child)
        path.rmdir()


def collect_targets(project_dir):
    """Collect generated files and directories to remove."""
    targets = []

    # 2_db: database files
    db_dir = project_dir / "2_db"
    if db_dir.is_dir():
        for f in db_dir.iterdir():
            if f.name == "project.duckdb" or f.suffix == ".wal":
                targets.append(f)

    # 3_analyses: results.json and figures directories
    analyses_dir = project_dir / "3_analyses"
    if analyses_dir.is_dir():
        for d in analyses_dir.iterdir():
            if d.is_dir():
                results_json = d / "results.json"
                if results_json.exists():
                    targets.append(results_json)
                figures_dir = d / "figures"
                if figures_dir.is_dir():
                    targets.append(figures_dir)

    # 4_output: rendered outputs and intermediates, but keep source files
    output_dir = project_dir / "4_output"
    if output_dir.is_dir():
        for d in output_dir.iterdir():
            if not d.is_dir():
                continue
            # Find qmd stems so we only delete generated .tex files (e.g. report.tex)
            qmd_stems = {f.stem for f in d.glob("*.qmd")}
            for f in d.rglob("*"):
                if not f.is_file():
                    continue
                if f.suffix in {".pdf", ".html", ".log", ".csv", ".xlsx"}:
                    targets.append(f)
                elif f.suffix == ".tex" and f.stem in qmd_stems:
                    targets.append(f)
                elif f.name == "export.json":
                    targets.append(f)
            # Remove _files directories created by Quarto
            for subdir in d.rglob("*_files"):
                if subdir.is_dir():
                    targets.append(subdir)

    return sorted(targets, key=lambda p: str(p))


args = parse_args()
project_dir = args.project_dir.resolve()
targets = collect_targets(project_dir)

if not targets:
    print("✓ No generated files to clean.")
    sys.exit(0)

print(f"{'Would remove' if not args.yes else 'Removing'} {len(targets)} item(s):\n")
for target in targets:
    print(f"  {target.relative_to(project_dir)}")

if not args.yes:
    print("\nThis was a dry run. Use --yes to actually delete.")
    sys.exit(0)

for target in targets:
    remove(target)

print("\n✓ Cleaned generated files.")
