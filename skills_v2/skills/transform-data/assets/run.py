# run.py — Heavy enrichment transformation
# Run from this folder:
#   python run.py
#
# This template uses skeleton_helpers.llm for structured LLM calls. Adapt it to
# your task: classification, extraction, summarization, geocoding, OCR, etc.

import json
import sys
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

from skeleton_helpers.llm import call_llm, call_llm_batch
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INPUT_PATHS = __INPUT_PATHS__
OUTPUT_DIR = Path("__OUTPUT_DIR__")
OUTPUT_FILE = OUTPUT_DIR / "output.csv"

# ---------------------------------------------------------------------------
# Pydantic output schema
# ---------------------------------------------------------------------------

class EnrichmentResult(BaseModel):
    # Define the fields the LLM should return
    label: str
    confidence: float
    explanation: str


# ---------------------------------------------------------------------------
# LLM prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You classify items into categories."""


def build_payload(row: dict, index: int) -> str:
    return json.dumps({
        "id": index,
        "text": row.get("text", ""),
    }, ensure_ascii=False)


def save_result(row: dict, result: EnrichmentResult | None, index: int, out_path: Path):
    if result is None:
        enriched = {"label": None, "confidence": None, "explanation": None}
    else:
        enriched = {
            "label": result.label,
            "confidence": result.confidence,
            "explanation": result.explanation,
        }
    out_path.write_text(
        json.dumps({**row, **enriched}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT_PATHS:
    print("✗ No input paths configured")
    sys.exit(1)

# Adapt this to your input files. The template assumes a single CSV.
input_file = INPUT_PATHS[0]
if not input_file.exists():
    print(f"✗ Input file not found: {input_file}")
    sys.exit(1)

df = pd.read_csv(input_file)
rows = df.to_dict(orient="records")

print(f"▶ Processing {len(rows)} rows...")
call_llm_batch(
    items=rows,
    system_prompt=SYSTEM_PROMPT,
    response_model=EnrichmentResult,
    build_payload=build_payload,
    save_result=save_result,
    out_dir=OUTPUT_DIR,
    file_pattern="item_{i:04d}.json",
    parallel=5,
)

# Combine individual outputs into a single CSV
output_files = sorted(OUTPUT_DIR.glob("item_*.json"))
records = []
for f in output_files:
    records.append(json.loads(f.read_text(encoding="utf-8")))

out_df = pd.DataFrame(records)
out_df.to_csv(OUTPUT_FILE, index=False)
print(f"✓ Wrote {len(out_df)} rows to {OUTPUT_FILE}")
