# render_quarto.py — Copy a Quarto deliverable template and render it
#
# Create deliverable:
#   python render_quarto.py --create report --out-dir my_report
# Render deliverable:
#   python render_quarto.py --out-dir my_report

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SUPPORTED_TYPES = {"report", "slides", "dashboard"}


def parse_args():
    parser = argparse.ArgumentParser(description="Create and render Quarto deliverables.")
    parser.add_argument(
        "--create",
        type=str,
        choices=sorted(SUPPORTED_TYPES),
        help="Template to instantiate in --out-dir.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory containing or receiving the Quarto project.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"✗ {message}", file=sys.stderr)
    sys.exit(1)


def require_command(name: str) -> None:
    """Fail fast if a required executable is not on PATH."""
    if shutil.which(name) is None:
        fail(
            f"'{name}' was not found on PATH. "
            f"Install it and try again (https://quarto.org/docs/get-started/)."
        )


def copy_template(src: Path, dst: Path) -> None:
    """Copy a template directory tree, skipping existing files."""
    if not src.is_dir():
        fail(f"template source is not a directory: {src}")
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if not item.is_file():
            continue
        rel = item.relative_to(src)
        dst_item = dst / rel
        if dst_item.exists():
            print(f"  ⚠ skipped existing {dst_item}")
            continue
        dst_item.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dst_item)
        print(f"  ✓ created {dst_item}")


args = parse_args()
out_dir = args.out_dir.resolve()

if out_dir.exists() and not out_dir.is_dir():
    fail(f"output path exists and is not a directory: {out_dir}")

skill_dir = Path(__file__).resolve().parent.parent
templates_dir = skill_dir / "assets"

if args.create:
    template_dir = templates_dir / args.create
    if not template_dir.is_dir():
        fail(f"template not found: {template_dir}")
    copy_template(template_dir, out_dir)
    common_dir = templates_dir / "common"
    if common_dir.is_dir():
        copy_template(common_dir, out_dir)
    print(f"✓ Created {args.create} template in {out_dir}")
    print("  Edit the scaffolded files, then render with:")
    print(f"    python render_quarto.py --out-dir {out_dir}")
    sys.exit(0)

quarto_yml = out_dir / "_quarto.yml"
if not quarto_yml.exists():
    fail(
        f"_quarto.yml not found in {out_dir}. "
        f"Use --create to scaffold a template, or run this from a Quarto project directory."
    )

require_command("quarto")

print(f"▶ Rendering {out_dir} ...")
result = subprocess.run(
    ["quarto", "render", str(out_dir)],
    capture_output=True,
    text=True,
)

print(result.stdout, end="")
if result.stderr:
    print(result.stderr, file=sys.stderr, end="")
if result.returncode != 0:
    sys.exit(result.returncode)

print(f"✓ Rendered {out_dir}")
