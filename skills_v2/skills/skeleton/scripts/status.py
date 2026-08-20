# status.py — Pipeline status and validation
# Run from the project root:
#   .venv/bin/python <path-to-skills>/data-analysis/status.py
# Or point to a project directory:
#   .venv/bin/python <path-to-skills>/data-analysis/status.py --project-dir /path/to/project

import argparse
import re
import sys
from pathlib import Path

# ── Colors ───────────────────────────────────────────────────────
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

if not sys.stdout.isatty():
    GREEN = YELLOW = RED = DIM = BOLD = RESET = ""


def ok(msg):
    return f"{GREEN}✓{RESET} {msg}"


def warn(msg):
    return f"{YELLOW}⚠{RESET} {msg}"


def fail(msg):
    return f"{RED}✗{RESET} {msg}"


def dim(msg):
    return f"{DIM}{msg}{RESET}"


def bold(msg):
    return f"{BOLD}{msg}{RESET}"


def parse_args():
    parser = argparse.ArgumentParser(description="Report data-analysis pipeline status.")
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory to inspect (default: current working directory).",
    )
    return parser.parse_args()


# ── Initialization ───────────────────────────────────────────────
def check_init(root):
    """Check whether the project has been initialized by skeleton/init.py."""
    required = {
        ".venv/bin/python": root / ".venv" / "bin" / "python",
        "0_plan/": root / "0_plan",
        "1_data/original/": root / "1_data" / "original",
        "2_db/": root / "2_db",
        "3_analyses/": root / "3_analyses",
        "4_output/": root / "4_output",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    return missing


# ── Stage 0: Plan ────────────────────────────────────────────────
def check_plan(root):
    plan_path = root / "0_plan" / "plan.md"
    issues = []
    details = []

    if not plan_path.exists():
        issues.append("plan.md not found")
        return "missing", issues, details

    return "complete", issues, details


# ── Stage 1: Data ────────────────────────────────────────────────
def parse_sources_yaml(path):
    """Parse sources.yaml, trying PyYAML first, then a regex fallback."""
    text = path.read_text()
    try:
        import yaml
        entries = yaml.safe_load(text)
        if isinstance(entries, list) and entries:
            return [e["file"] for e in entries if isinstance(e, dict) and "file" in e]
        return []
    except ImportError:
        return re.findall(r"^-\s+file:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE)
    except Exception:
        return None


def collect_data_files(directory):
    """Recursively collect data files, returning paths relative to the given directory."""
    skip = {"README.md", "sources.yaml", ".gitkeep"}
    files = []
    if directory.is_dir():
        for f in sorted(directory.rglob("*")):
            if (
                f.is_file()
                and f.name not in skip
                and not f.name.startswith(".")
                and not f.suffix == ".py"
            ):
                files.append(f.relative_to(directory).as_posix())
    return files


def check_data(root):
    data_dir = root / "1_data"
    original_dir = data_dir / "original"
    transformed_dir = data_dir / "transformed"
    sources_path = original_dir / "sources.yaml"

    issues = []
    details = []

    original_files = collect_data_files(original_dir)
    transformed_files = collect_data_files(transformed_dir)
    all_data_files = original_files + transformed_files

    documented = []
    if sources_path.exists():
        result = parse_sources_yaml(sources_path)
        if result is None:
            issues.append("sources.yaml could not be parsed")
        else:
            documented = result
    else:
        issues.append("original/sources.yaml not found")

    if not all_data_files and not documented:
        return "empty", issues, details

    if original_files:
        details.append(f"{len(original_files)} original file(s): {', '.join(original_files)}")
    if transformed_files:
        details.append(f"{len(transformed_files)} transformed file(s)")

    original_names = original_files
    undocumented = [f for f in original_names if f not in documented]
    missing_files = [f for f in documented if f not in original_names]

    if undocumented:
        issues.append(f"Undocumented: {', '.join(undocumented)}")
    if missing_files:
        issues.append(f"In sources.yaml but missing on disk: {', '.join(missing_files)}")

    if documented:
        details.append(f"{len(documented)} documented in sources.yaml")

    if not issues and documented and all_data_files:
        return "complete", issues, details
    elif all_data_files or documented:
        return "partial", issues, details
    return "empty", issues, details


# ── Stage 2: Database ────────────────────────────────────────────
def check_db(root):
    db_path = root / "2_db" / "project.duckdb"
    schema_path = root / "2_db" / "schema.md"
    data_dir = root / "1_data"

    issues = []
    details = []

    if not db_path.exists():
        return "not_built", issues, details

    has_tables = False
    if schema_path.exists():
        schema_text = schema_path.read_text()
        tables = re.findall(r"^## `(\w+)`", schema_text, re.MULTILINE)
        if tables:
            has_tables = True
            details.append(f"{len(tables)} table(s): {', '.join(tables)}")

    if not has_tables:
        issues.append("schema.md has no tables (DB may be empty)")

    db_mtime = db_path.stat().st_mtime
    skip = {"README.md", "sources.yaml", ".gitkeep"}
    stale_files = []
    for subdir in [data_dir / "original", data_dir / "transformed"]:
        if subdir.is_dir():
            for f in subdir.rglob("*"):
                if f.is_file() and f.name not in skip and not f.name.startswith("."):
                    if f.stat().st_mtime > db_mtime:
                        stale_files.append(str(f.relative_to(data_dir)))

    if stale_files:
        issues.append(f"DB older than: {', '.join(stale_files)}")
        if has_tables:
            return "stale", issues, details

    if not issues:
        return "complete", issues, details
    return "partial", issues, details


# ── Stage 3: Analyses ────────────────────────────────────────────
def check_analyses(root):
    analyses_dir = root / "3_analyses"
    issues = []
    details = []

    subfolders = sorted(
        d
        for d in analyses_dir.iterdir()
        if d.is_dir()
        and d.name != "example_analysis"
        and not d.name.startswith(".")
        and not d.name.startswith("_deprecated_")
    ) if analyses_dir.is_dir() else []

    if not subfolders:
        return "empty", issues, details

    with_results = []
    without_results = []

    for d in subfolders:
        rj = d / "results.json"
        if rj.exists():
            with_results.append(d.name)
        else:
            without_results.append(d.name)

    details.append(f"{len(subfolders)} analysis folder(s)")
    if with_results:
        details.append(f"{len(with_results)} with results.json")

    if without_results:
        issues.append(f"Missing results.json: {', '.join(without_results)}")

    if not issues and with_results:
        return "complete", issues, details
    elif with_results:
        return "partial", issues, details
    elif without_results:
        return "incomplete", issues, details
    return "empty", issues, details


# ── Stage 4: Output ──────────────────────────────────────────────
def check_output(root):
    output_dir = root / "4_output"
    skip = {"__pycache__"}

    issues = []
    details = []

    deliverables = sorted(
        d
        for d in output_dir.iterdir()
        if d.is_dir() and d.name not in skip and not d.name.startswith(".")
    ) if output_dir.is_dir() else []

    if not deliverables:
        return "empty", issues, details

    rendered = []
    unrendered = []

    for d in deliverables:
        outputs = list(d.glob("*.pdf")) + list(d.glob("*.html"))
        if outputs:
            formats = set(o.suffix for o in outputs)
            rendered.append(f"{d.name} ({', '.join(formats)})")
        else:
            unrendered.append(d.name)

    details.append(f"{len(deliverables)} deliverable(s)")
    if rendered:
        details.append(f"Rendered: {', '.join(rendered)}")
    if unrendered:
        issues.append(f"Not yet rendered: {', '.join(unrendered)}")

    if not issues:
        return "complete", issues, details
    return "partial", issues, details


# ── Main ─────────────────────────────────────────────────────────
STATUS_DISPLAY = {
    "complete": lambda: ok("Complete"),
    "incomplete": lambda: fail("Incomplete"),
    "partial": lambda: warn("Partial"),
    "empty": lambda: dim("Empty"),
    "not_built": lambda: dim("Not built"),
    "missing": lambda: fail("Missing"),
    "stale": lambda: warn("Stale"),
}

args = parse_args()
root = args.project_dir.resolve()

STAGES = [
    ("Stage 0 — Plan", check_plan),
    ("Stage 1 — Data", check_data),
    ("Stage 2 — Database", check_db),
    ("Stage 3 — Analyses", check_analyses),
    ("Stage 4 — Output", check_output),
]

missing_init = check_init(root)

print(f"\n{bold('Pipeline Status')}")
print("═" * 50)

if missing_init:
    print(f"\n{bold('Project initialized:')}  {fail('No')}")
    for item in missing_init:
        print(f"  {fail('Missing: ' + item)}")
else:
    print(f"\n{bold('Project initialized:')}  {ok('Yes')}")

first_incomplete = None

for i, (label, check_fn) in enumerate(STAGES):
    status, issues, details = check_fn(root)
    status_str = STATUS_DISPLAY.get(status, lambda: status)()

    print(f"\n{bold(label + ':')}  {status_str}")
    for d in details:
        print(f"  {dim(d)}")
    for issue in issues:
        print(f"  {fail(issue)}")

    if status != "complete" and first_incomplete is None:
        first_incomplete = (i, status)

print("\n" + "─" * 50)

if first_incomplete is None:
    print(ok("All stages complete!"))
else:
    stage_name = STAGES[first_incomplete[0]][0]
    print(f"→ Current stage: {bold(stage_name)}")

print()
