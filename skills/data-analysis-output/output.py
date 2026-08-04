# output.py — Create and render deliverables
# Run from the project root:
#   python <path-to-skills>/data-analysis-output/output.py --type report --name my-report
#
# Supported types: report, report-brief, slides, dashboard, export

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SUPPORTED_TYPES = {"report", "report-brief", "slides", "dashboard", "export"}


def parse_args():
    parser = argparse.ArgumentParser(description="Create and render deliverables.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current working directory).",
    )
    parser.add_argument(
        "--type",
        type=str,
        required=True,
        choices=sorted(SUPPORTED_TYPES),
        help="Type of deliverable to create.",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the deliverable subfolder (e.g. 'short-report').",
    )
    return parser.parse_args()


def copytree(src, dst):
    """Copy a directory tree, overwriting existing files."""
    if not src.is_dir():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        dst_item = dst / item.name
        if item.is_dir():
            copytree(item, dst_item)
        else:
            shutil.copy2(item, dst_item)


args = parse_args()
project_dir = args.project_dir.resolve()
skill_dir = Path(__file__).parent.resolve()
templates_src = skill_dir / "templates"
output_dir = project_dir / "4_output"
deliverable_dir = output_dir / args.name
helpers_dst = output_dir / "helpers.py"

if deliverable_dir.exists():
    print(f"✗ Deliverable already exists: {deliverable_dir.relative_to(project_dir)}")
    sys.exit(1)

# Ensure at least one analysis result exists
analyses_dir = project_dir / "3_analyses"
results_files = list(analyses_dir.rglob("results.json")) if analyses_dir.is_dir() else []
if not results_files:
    print("⚠ No analysis results found. Run analyses before creating deliverables.")
    sys.exit(0)

output_dir.mkdir(parents=True, exist_ok=True)

# Copy helpers.py to 4_output/helpers.py if missing
helpers_src = templates_src / "helpers.py"
if helpers_src.exists() and not helpers_dst.exists():
    shutil.copy2(helpers_src, helpers_dst)
    print(f"✓ Created {helpers_dst.relative_to(project_dir)}")

# Copy the template folder into the deliverable folder
type_template_dir = templates_src / args.type
if not type_template_dir.is_dir():
    print(f"✗ Template not found: {type_template_dir}", file=sys.stderr)
    sys.exit(1)
copytree(type_template_dir, deliverable_dir)
print(f"✓ Created deliverable: {deliverable_dir.relative_to(project_dir)}")

# Export deliverables need editing before running
if args.type == "export":
    print(f"→ Edit {deliverable_dir.relative_to(project_dir)}/export.py to load analyses and export data.")
    sys.exit(0)

# Find the qmd file in the deliverable folder
qmd_files = list(deliverable_dir.glob("*.qmd"))
if not qmd_files:
    print(f"✗ No .qmd file found in {deliverable_dir.relative_to(project_dir)}", file=sys.stderr)
    sys.exit(1)
qmd_file = qmd_files[0]

# Render with Quarto
print(f"▶ Rendering {qmd_file.relative_to(project_dir)}...")
result = subprocess.run(
    ["quarto", "render", qmd_file.name],
    cwd=str(deliverable_dir),
    capture_output=True,
    text=True,
)
print(result.stdout, end="")
if result.stderr:
    print(result.stderr, file=sys.stderr, end="")
if result.returncode != 0:
    print(f"✗ Rendering failed for {args.name}", file=sys.stderr)
    sys.exit(result.returncode)

print(f"✓ Rendered {args.name}")
