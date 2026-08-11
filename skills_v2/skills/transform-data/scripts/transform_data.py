# transform_data.py — Scaffold and run a data transformation
#
# Create transformation:
#   python transform_data.py --create --input path/to/file.csv --out-dir 1_data/transformed/x
# Run transformation:
#   python transform_data.py --input path/to/file.csv --out-dir 1_data/transformed/x

import argparse
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
    """Check if out_dir contains any output data files."""
    skip = {"README.md", ".gitkeep", "run.py"}
    for f in out_dir.iterdir():
        if f.is_file() and f.name not in skip:
            return True
    return False


def format_input_paths(paths: list[Path]) -> str:
    """Return a Python list-of-Paths literal for insertion into the template."""
    lines = ",\n    ".join(f"Path({str(p.resolve())!r})" for p in paths)
    return f"[\n    {lines}\n]"


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
    template_text = (
        template_path.read_text()
        .replace("__INPUT_PATHS__", format_input_paths(inputs))
        .replace("__OUTPUT_DIR__", str(out_dir))
    )
    run_script.write_text(template_text)
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
