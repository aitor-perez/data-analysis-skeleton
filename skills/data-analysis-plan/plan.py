# plan.py — Create and validate the project plan
# Run from the project root:
#   .venv/bin/python <path-to-skills>/data-analysis-plan/plan.py
# Or point to a project directory:
#   .venv/bin/python <path-to-skills>/data-analysis-plan/plan.py --project-dir /path/to/project

import argparse
import re
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Create and validate the project plan.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory to inspect (default: current working directory).",
    )
    return parser.parse_args()


args = parse_args()
project_dir = args.project_dir.resolve()
plan_path = project_dir / "0_plan" / "plan.md"
skill_dir = Path(__file__).parent.resolve()
template_path = skill_dir / "templates" / "plan.md"

# Create plan.md from template if missing
if not plan_path.exists():
    if not template_path.exists():
        print(f"✗ Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(template_path.read_text())
    print(f"✓ Created {plan_path.relative_to(project_dir)} from template")

# Read and validate
plan_text = plan_path.read_text()
lines = plan_text.splitlines()

placeholders = []
current_section = None

for line in lines:
    header_match = re.match(r"^##\s+(.+)\s*$", line)
    if header_match:
        current_section = header_match.group(1).strip()
    if re.match(r"^_[^_]*\?[^_]*_\s*$", line):
        prompt = line.strip().strip("_")
        placeholders.append((current_section or "Unknown", prompt))

if not placeholders:
    print("✓ Plan is complete. No placeholders found.")
else:
    print(f"⚠ Plan is incomplete. {len(placeholders)} placeholder(s) found:\n")
    for section, prompt in placeholders:
        print(f"  [{section}] {prompt}")
    print(f"\n→ Edit {plan_path.relative_to(project_dir)} to replace placeholders with real content.")
