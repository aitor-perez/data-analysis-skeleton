# analyze.py — Create and run analyses
# Run from the project root:
#   .venv/bin/python <path-to-skills>/data-analysis-analyze/analyze.py
#
# Create a new analysis:
#   .venv/bin/python <path-to-skills>/data-analysis-analyze/analyze.py --create value_frequency
#
# Run all analyses:
#   .venv/bin/python <path-to-skills>/data-analysis-analyze/analyze.py

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED_RESULT_KEYS = {"query", "n_results", "results", "description", "interpretation", "figures"}


def parse_args():
    parser = argparse.ArgumentParser(description="Create and run analyses.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current working directory).",
    )
    parser.add_argument(
        "--create",
        type=str,
        help="Name of a new analysis subfolder to create.",
    )
    return parser.parse_args()


def find_python(project_dir):
    """Return .venv/bin/python if it exists, otherwise python3."""
    venv_python = project_dir / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return "python3"


def validate_results_json(path):
    """Validate a results.json file. Returns list of issues (empty = valid)."""
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
project_dir = args.project_dir.resolve()
analyses_dir = project_dir / "3_analyses"
skill_dir = Path(__file__).parent.resolve()
template_path = skill_dir / "templates" / "run.py"
python = find_python(project_dir)

# Create a new analysis
if args.create:
    analysis_dir = analyses_dir / args.create
    run_script = analysis_dir / "run.py"
    if run_script.exists():
        print(f"✗ Analysis already exists: {run_script.relative_to(project_dir)}")
        sys.exit(1)
    if not template_path.exists():
        print(f"✗ Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    template_text = template_path.read_text().replace("__NAME__", args.create)
    run_script.write_text(template_text)
    print(f"✓ Created analysis: {analysis_dir.relative_to(project_dir)}")
    print(f"→ Edit {run_script.relative_to(project_dir)} to answer your question.")
    sys.exit(0)

# Run all analyses
if not analyses_dir.is_dir():
    print("⚠ No 3_analyses/ directory found.")
    sys.exit(0)

run_scripts = sorted(
    d / "run.py"
    for d in analyses_dir.iterdir()
    if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("_deprecated_")
    if (d / "run.py").exists()
)

if not run_scripts:
    print("⚠ No analyses found in 3_analyses/. Use --create <name> to add one.")
    sys.exit(0)

all_ok = True
for run_script in run_scripts:
    analysis_dir = run_script.parent
    print(f"\n▶ Running {analysis_dir.name}...")
    result = subprocess.run(
        [python, str(run_script.name)],
        cwd=str(analysis_dir),
        capture_output=True,
        text=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        print(f"✗ {analysis_dir.name} failed")
        all_ok = False
        continue

    results_json = analysis_dir / "results.json"
    if not results_json.exists():
        print(f"✗ {analysis_dir.name} did not produce results.json")
        all_ok = False
        continue

    issues = validate_results_json(results_json)
    if issues:
        print(f"✗ {analysis_dir.name}/results.json invalid:")
        for issue in issues:
            print(f"  - {issue}")
        all_ok = False
    else:
        print(f"✓ {analysis_dir.name}/results.json valid")

print()
if all_ok:
    print("✓ All analyses completed successfully")
else:
    print("⚠ Some analyses failed or produced invalid results.json")
    sys.exit(1)
