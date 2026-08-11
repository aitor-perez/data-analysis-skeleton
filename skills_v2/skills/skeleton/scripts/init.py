# init.py — Bootstrap a new data-analysis project
# Run from the project root:
#   python3 <path-to-catalog>/skills/skeleton/scripts/init.py
# Or point to a project directory:
#   python3 <path-to-catalog>/skills/skeleton/scripts/init.py --project-dir /path/to/project

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Bootstrap a data-analysis project.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory to initialize (default: current working directory).",
    )
    return parser.parse_args()


args = parse_args()
project_dir = args.project_dir.resolve()
skill_dir = Path(__file__).resolve().parent.parent
assets_dir = skill_dir / "assets"
catalog_dir = skill_dir.parent.parent

# Directories to create
DIRECTORIES = [
    project_dir / "0_plan",
    project_dir / "1_data" / "original",
    project_dir / "1_data" / "transformed",
    project_dir / "2_db",
    project_dir / "3_analyses",
    project_dir / "4_output",
]

# Template files to copy: (source relative to assets_dir, destination relative to project_dir)
FILES = [
    ("README.md", "README.md"),
    (".env.example", ".env.example"),
    (".gitignore", ".gitignore"),
]

print(f"▶ Initializing project at {project_dir}", flush=True)
project_dir.mkdir(parents=True, exist_ok=True)

# Create directories
for d in DIRECTORIES:
    d.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {d.relative_to(project_dir)}", flush=True)

# Copy template files, skipping existing
for src_rel, dst_rel in FILES:
    src = assets_dir / src_rel
    dst = project_dir / dst_rel
    if dst.exists():
        print(f"  ⚠ skipped existing {dst_rel}", flush=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text())
        print(f"  ✓ created {dst_rel}", flush=True)

# Create .venv if it doesn't exist
venv_dir = project_dir / ".venv"
if venv_dir.exists():
    print(f"  ⚠ .venv already exists, skipping creation", flush=True)
else:
    print("\n▶ Creating virtual environment...", flush=True)
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    print(f"  ✓ .venv created", flush=True)

    print("\n▶ Installing skeleton_helpers package...", flush=True)
    pip = venv_dir / "bin" / "pip"
    subprocess.run([str(pip), "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip), "install", "-e", str(catalog_dir)], check=True)
    print("  ✓ skeleton_helpers installed", flush=True)

print("\n✓ Project initialized", flush=True)
