# transform.py — Scaffold and run data transformations
# Run from the project root:
#   .venv/bin/python <path-to-skills>/data-analysis-transform/transform.py --name classify
#
# Scaffold a new transformation:
#   .venv/bin/python <path-to-skills>/data-analysis-transform/transform.py --create classify

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Scaffold and run data transformations.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current working directory).",
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Name of the transformation subfolder in 1_data/transformed/.",
    )
    parser.add_argument(
        "--create",
        type=str,
        help="Scaffold a new transformation with this name.",
    )
    return parser.parse_args()


def find_python(project_dir):
    """Return .venv/bin/python if it exists, otherwise python3."""
    venv_python = project_dir / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return "python3"


def has_output_files(transform_dir):
    """Check if the transformation directory contains any output data files."""
    skip = {"README.md", ".gitkeep"}
    for f in transform_dir.iterdir():
        if f.is_file() and f.name not in skip and f.suffix != ".py":
            return True
    return False


args = parse_args()
project_dir = args.project_dir.resolve()
transformed_dir = project_dir / "1_data" / "transformed"
skill_dir = Path(__file__).parent.resolve()
template_path = skill_dir / "templates" / "transform.py"

# Determine the transformation name and mode
if args.create and args.name:
    print("✗ Use either --create <name> or --name <name>, not both.", file=sys.stderr)
    sys.exit(1)

mode = "create" if args.create else "run"
transform_name = args.create or args.name

if not transform_name:
    print("✗ --name or --create is required", file=sys.stderr)
    sys.exit(1)

transform_dir = transformed_dir / transform_name
script_path = transform_dir / f"{transform_name}.py"

# Scaffold a new transformation
if mode == "create":
    if script_path.exists():
        print(f"✗ Transformation already exists: {script_path.relative_to(project_dir)}")
        sys.exit(1)
    if not template_path.exists():
        print(f"✗ Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    transform_dir.mkdir(parents=True, exist_ok=True)
    template_text = template_path.read_text().replace("__NAME__", transform_name)
    script_path.write_text(template_text)
    print(f"✓ Created transformation: {transform_dir.relative_to(project_dir)}")
    print(f"→ Edit {script_path.relative_to(project_dir)} to implement the enrichment.")
    sys.exit(0)

# Run an existing transformation
if not script_path.exists():
    print(f"✗ Transformation not found: {script_path.relative_to(project_dir)}")
    print("Use --create to scaffold it.")
    sys.exit(1)

python = find_python(project_dir)
print(f"▶ Running {script_path.relative_to(project_dir)}...")
result = subprocess.run(
    [python, str(script_path.name)],
    cwd=str(transform_dir),
    capture_output=True,
    text=True,
)
print(result.stdout, end="")
if result.stderr:
    print(result.stderr, file=sys.stderr, end="")
if result.returncode != 0:
    print(f"✗ Transformation {args.name} failed", file=sys.stderr)
    sys.exit(result.returncode)

if has_output_files(transform_dir):
    print(f"✓ Transformation {transform_name} completed and produced output files")
else:
    print(f"⚠ Transformation {transform_name} ran but produced no output files")
