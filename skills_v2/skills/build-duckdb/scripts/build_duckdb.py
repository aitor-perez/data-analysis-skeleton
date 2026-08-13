# build_duckdb.py — Scaffold and run a DuckDB database build
#
# Create build script:
#   python build_duckdb.py --create --data-dir data --out-dir db
# Run build:
#   python build_duckdb.py --data-dir data --out-dir db

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Build a DuckDB database from raw data.")
    parser.add_argument(
        "--create",
        action="store_true",
        help="Copy the build_db.py template into --out-dir and exit.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory containing the raw data files to load.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where build_db.py, the database, and schema.md are written.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"✗ {message}", file=sys.stderr)
    sys.exit(1)


args = parse_args()
data_dir = args.data_dir.resolve()
out_dir = args.out_dir.resolve()

if not data_dir.exists():
    fail(f"data-dir not found: {data_dir}")

out_dir.mkdir(parents=True, exist_ok=True)

skill_dir = Path(__file__).resolve().parent.parent
template_path = skill_dir / "assets" / "build_db.py"
build_script = out_dir / "build_db.py"

if args.create:
    if build_script.exists():
        fail(f"build script already exists: {build_script}")
    if not template_path.exists():
        fail(f"template not found: {template_path}")
    shutil.copy2(template_path, build_script)
    print(f"✓ Created {build_script}")
    sys.exit(0)

if not build_script.exists():
    fail(f"build script not found; use --create to scaffold it: {build_script}")

python = sys.executable
print(f"▶ Running {build_script} ...")
result = subprocess.run(
    [python, str(build_script)],
    cwd=str(out_dir),
    capture_output=True,
    text=True,
)

print(result.stdout, end="")
if result.stderr:
    print(result.stderr, file=sys.stderr, end="")
if result.returncode != 0:
    sys.exit(result.returncode)

db_files = sorted(out_dir.glob("*.duckdb"))
if not db_files:
    fail(f"no .duckdb file found in {out_dir}")
if len(db_files) > 1:
    fail(f"multiple .duckdb files found in {out_dir}: {[f.name for f in db_files]}")

db_path = db_files[0]
schema_path = out_dir / "schema.md"
if not schema_path.exists():
    fail(f"schema.md not found in {out_dir}")

schema_text = schema_path.read_text()
tables = re.findall(r"^## `(\w+)`", schema_text, re.MULTILINE)
if not tables:
    fail(f"schema.md has no tables; database may be empty")

print(f"✓ Database built: {db_path.name}")
print(f"✓ Schema written: {schema_path.name}")
print(f"✓ Tables: {', '.join(tables)}")
