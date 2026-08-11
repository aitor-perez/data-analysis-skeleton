# document_sources.py — Validate and document raw data files
#
# Usage:
#   python document_sources.py --data-dir 1_data/original

import argparse
import re
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Validate raw data files and sources.yaml.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        required=True,
        help="Directory containing raw data files. A sources.yaml file is created/validated in this directory.",
    )
    return parser.parse_args()


def parse_sources_yaml(path):
    """Parse sources.yaml, trying PyYAML first, then a regex fallback."""
    if not path.exists():
        return None, []
    text = path.read_text()
    try:
        import yaml
        entries = yaml.safe_load(text)
        if entries is None:
            return [], []
        if isinstance(entries, list):
            return entries, []
        return [], ["sources.yaml is not a list"]
    except ImportError:
        files = re.findall(r"^-\s+file:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE)
        return [{"file": f} for f in files], []
    except Exception as exc:
        return [], [f"sources.yaml could not be parsed: {exc}"]


def collect_data_files(directory):
    """Collect data files from a directory, returning paths relative to that directory."""
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


def suggest_entry(filename):
    suffix = Path(filename).suffix.lower()
    format_map = {
        ".csv": "CSV",
        ".json": "JSON",
        ".xlsx": "XLSX",
        ".xls": "XLS",
        ".parquet": "Parquet",
        ".tsv": "TSV",
        ".txt": "TXT",
    }
    fmt = format_map.get(suffix, suffix.lstrip(".").upper() if suffix else "")
    return {
        "file": filename,
        "origin": "",
        "url": "",
        "accessed": "",
        "description": "",
        "format": fmt,
        "encoding": "",
        "confidential": False,
        "notes": "",
    }


def format_entry(entry):
    lines = ["- file: " + entry["file"]]
    for key in ["origin", "url", "accessed", "description", "format", "encoding", "confidential", "notes"]:
        value = entry.get(key, "")
        if isinstance(value, bool):
            lines.append(f"  {key}: {str(value).lower()}")
        elif value:
            lines.append(f"  {key}: \"{value}\"")
        else:
            lines.append(f"  {key}: \"\"")
    return "\n".join(lines)


args = parse_args()
data_dir = args.data_dir.resolve()
sources_path = data_dir / "sources.yaml"
skill_dir = Path(__file__).resolve().parent.parent
assets_dir = skill_dir / "assets"
template_path = assets_dir / "sources.yaml"

# Create sources.yaml from template if missing
if not sources_path.exists():
    if not template_path.exists():
        print(f"✗ Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    data_dir.mkdir(parents=True, exist_ok=True)
    sources_path.write_text(template_path.read_text())
    print(f"✓ Created {sources_path} from template")

entries, parse_issues = parse_sources_yaml(sources_path)
documented_files = [e["file"] for e in entries if isinstance(e, dict) and "file" in e]
disk_files = collect_data_files(data_dir)

for issue in parse_issues:
    print(f"✗ {issue}")

undocumented = [f for f in disk_files if f not in documented_files]
missing = [f for f in documented_files if f not in disk_files]
confidential = [e["file"] for e in entries if isinstance(e, dict) and e.get("confidential") is True]

if not disk_files and not documented_files:
    print(f"⚠ No raw data files found in {data_dir}.")
else:
    print(f"✓ {len(disk_files)} file(s) in {data_dir}")
    print(f"✓ {len(documented_files)} file(s) documented in {sources_path.name}")

if undocumented:
    print(f"\n⚠ Undocumented files ({len(undocumented)}):")
    for f in undocumented:
        print(f"  - {f}")
    print("\nSuggested entries:\n")
    for f in undocumented:
        print(format_entry(suggest_entry(f)))
        print()

if missing:
    print(f"\n⚠ Documented but missing on disk ({len(missing)}):")
    for f in missing:
        print(f"  - {f}")

if confidential:
    print(f"\n⚠ Confidential files ({len(confidential)}):")
    for f in confidential:
        print(f"  - {f}")
    print("  Make sure these are listed in .gitignore.")

if not undocumented and not missing and not parse_issues:
    print("\n✓ All raw data files are documented.")
