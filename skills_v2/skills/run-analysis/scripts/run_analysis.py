# run_analysis.py — Scaffold and run a single analysis against a DuckDB database
#
# Create analysis:
#   python run_analysis.py --create --db-dir db --out-dir analyses/q1
# Run analysis:
#   python run_analysis.py --db-dir db --out-dir analyses/q1

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


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

print("✓ results.json created")
