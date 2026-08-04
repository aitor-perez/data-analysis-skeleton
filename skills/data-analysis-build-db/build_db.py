# build_db.py — Copy build_db.py template and run the database build
# Run from the project root:
#   python <path-to-skills>/data-analysis-build-db/build_db.py
# Or point to a project directory:
#   python <path-to-skills>/data-analysis-build-db/build_db.py --project-dir /path/to/project

import argparse
import re
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Build the DuckDB database.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current working directory).",
    )
    return parser.parse_args()


def find_python(project_dir):
    """Return .venv/bin/python if it exists, otherwise python3."""
    venv_python = project_dir / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return "python3"


args = parse_args()
project_dir = args.project_dir.resolve()
skill_dir = Path(__file__).parent.resolve()
template_path = skill_dir / "templates" / "build_db.py"
db_dir = project_dir / "2_db"
build_script = db_dir / "build_db.py"
db_path = db_dir / "project.duckdb"
schema_path = db_dir / "schema.md"

# Copy template if build_db.py does not exist
if not build_script.exists():
    if not template_path.exists():
        print(f"✗ Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    db_dir.mkdir(parents=True, exist_ok=True)
    build_script.write_text(template_path.read_text())
    print(f"✓ Created {build_script.relative_to(project_dir)} from template")
    print("→ Edit this file to import your data, then re-run this skill.")
    sys.exit(0)

# Run the build script
python = find_python(project_dir)
print(f"▶ Running {build_script.relative_to(project_dir)} with {python}...")
result = subprocess.run(
    [python, str(build_script)],
    cwd=str(project_dir),
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print(f"✗ {build_script.relative_to(project_dir)} failed:", file=sys.stderr)
    print(result.stdout, file=sys.stderr)
    print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)

print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

# Validate outputs
if not db_path.exists():
    print(f"✗ Database not found after build: {db_path.relative_to(project_dir)}", file=sys.stderr)
    sys.exit(1)

has_tables = False
if schema_path.exists():
    schema_text = schema_path.read_text()
    tables = re.findall(r"^## `(\w+)`", schema_text, re.MULTILINE)
    has_tables = bool(tables)

if has_tables:
    print(f"✓ Database built: {db_path.relative_to(project_dir)}")
    print(f"✓ Schema written: {schema_path.relative_to(project_dir)}")
else:
    print(f"⚠ Database built but schema.md has no tables. Edit {build_script.relative_to(project_dir)} to import data.")
