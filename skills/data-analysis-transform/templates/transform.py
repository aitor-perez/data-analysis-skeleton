# transform.py — Heavy enrichment for __NAME__
# Run from this folder:
#   python __NAME__.py
#
# This template uses utils.llm for structured LLM calls. Adapt it to your task:
# classification, extraction, summarization, geocoding, OCR, etc.

import json
import sys
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from utils.llm import call_llm, call_llm_batch

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INPUT_FILE = Path("../../1_data/original/input.csv")  # adapt
OUTPUT_FILE = Path("output.csv")

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

if not INPUT_FILE.exists():
    print(f"✗ Input file not found: {INPUT_FILE}")
    sys.exit(1)

df = pd.read_csv(INPUT_FILE)
rows = df.to_dict(orient="records")

print(f"▶ Processing {len(rows)} rows...")
call_llm_batch(
    items=rows,
    system_prompt=SYSTEM_PROMPT,
    response_model=EnrichmentResult,
    build_payload=build_payload,
    save_result=save_result,
    out_dir=".",
    file_pattern="item_{i:04d}.json",
    parallel=5,
)

# Combine individual outputs into a single CSV
output_files = sorted(Path(".").glob("item_*.json"))
records = []
for f in output_files:
    records.append(json.loads(f.read_text(encoding="utf-8")))

out_df = pd.DataFrame(records)
out_df.to_csv(OUTPUT_FILE, index=False)
print(f"✓ Wrote {len(out_df)} rows to {OUTPUT_FILE}")
