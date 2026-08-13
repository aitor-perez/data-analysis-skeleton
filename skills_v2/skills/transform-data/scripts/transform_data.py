# transform_data.py — Scaffold and run a data transformation
#
# Create transformation:
#   python transform_data.py --create --input data/file.csv --out-dir transformed/x
# Run transformation:
#   python transform_data.py --input data/file.csv --out-dir transformed/x

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Scaffold and run a data transformation.")
    parser.add_argument(
        "--create",
        action="store_true",
        help="Copy the run.py template into --out-dir and exit.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        action="append",
        required=True,
        help="Input file or directory. Repeat for multiple inputs.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where run.py and output files are written.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"✗ {message}", file=sys.stderr)
    sys.exit(1)


def has_output_files(out_dir: Path) -> bool:
    """Check if out_dir or any subdirectory contains output data files."""
    skip = {"README.md", ".gitkeep", "run.py"}
    for f in out_dir.rglob("*"):
        if f.is_file() and f.name not in skip and not f.name.startswith("."):
            return True
    return False


args = parse_args()
inputs = [p.resolve() for p in args.input]
out_dir = args.out_dir.resolve()

for p in inputs:
    if not p.exists():
        fail(f"input not found: {p}")

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

if not has_output_files(out_dir):
    fail(f"no output files produced in {out_dir}")

print(f"✓ Transformation completed and produced output files")
