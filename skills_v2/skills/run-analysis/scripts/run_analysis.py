# run_analysis.py — Scaffold and run a single analysis against a DuckDB database
#
# Create analysis:
#   python run_analysis.py --create --db-dir 2_db --out-dir 3_analyses/q1
# Run analysis:
#   python run_analysis.py --db-dir 2_db --out-dir 3_analyses/q1

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_RESULT_KEYS = {"query", "n_results", "results", "description", "interpretation", "figures"}


def parse_args():
    parser = argparse.ArgumentParser(description="Scaffold and run an analysis against a DuckDB database.")
    parser.add_argument(
        "--create",
        action="store_true",
        help="Copy the run.py template into --out-dir and exit.",
    )
    parser.add_argument(
        "--db-dir",
        type=Path,
        required=True,
        help="Directory containing exactly one .duckdb file and a schema.md.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where run.py and results.json are written.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"✗ {message}", file=sys.stderr)
    sys.exit(1)


def validate_results_json(path: Path) -> list[str]:
    issues = []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    missing = REQUIRED_RESULT_KEYS - set(data.keys())
    if missing:
        issues.append(f"Missing keys: {missing}")
        return issues

    if not isinstance(data["results"], list):
        issues.append("'results' is not a list")
    elif data["n_results"] != len(data["results"]):
        issues.append(
            f"n_results={data['n_results']} but results has {len(data['results'])} items"
        )

    if not isinstance(data["figures"], list):
        issues.append("'figures' is not a list")
    else:
        for i, fig in enumerate(data["figures"]):
            if "file" not in fig:
                issues.append(f"figures[{i}] missing 'file'")
            elif not (path.parent / fig["file"]).exists():
                issues.append(f"figures[{i}] file not found: {fig['file']}")
            if "caption" not in fig:
                issues.append(f"figures[{i}] missing 'caption'")

    return issues


args = parse_args()
db_dir = args.db_dir.resolve()
out_dir = args.out_dir.resolve()

if not db_dir.exists():
    fail(f"db-dir not found: {db_dir}")

duckdb_files = sorted(db_dir.glob("*.duckdb"))
if not duckdb_files:
    fail(f"no .duckdb file found in {db_dir}")
if len(duckdb_files) > 1:
    fail(f"multiple .duckdb files found in {db_dir}: {[f.name for f in duckdb_files]}")
db_path = duckdb_files[0]

schema_path = db_dir / "schema.md"
if not schema_path.exists():
    fail(f"schema.md not found in {db_dir}")

out_dir.mkdir(parents=True, exist_ok=True)

skill_dir = Path(__file__).resolve().parent.parent
template_path = skill_dir / "assets" / "run.py"
run_script = out_dir / "run.py"

if args.create:
    if run_script.exists():
        fail(f"run script already exists: {run_script}")
    if not template_path.exists():
        fail(f"template not found: {template_path}")
    shutil.copy2(template_path, run_script)
    print(f"✓ Created {run_script}")
    sys.exit(0)

if not run_script.exists():
    fail(f"run script not found; use --create to scaffold it: {run_script}")

python = sys.executable
print(f"▶ Running {run_script} ...")
result = subprocess.run(
    [python, str(run_script)],
    cwd=str(out_dir),
    capture_output=True,
    text=True,
)

print(result.stdout, end="")
if result.stderr:
    print(result.stderr, file=sys.stderr, end="")
if result.returncode != 0:
    sys.exit(result.returncode)

results_json = out_dir / "results.json"
if not results_json.exists():
    fail(f"results.json not found in {out_dir}")

issues = validate_results_json(results_json)
if issues:
    print("✗ results.json invalid:")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)

print("✓ results.json valid")
