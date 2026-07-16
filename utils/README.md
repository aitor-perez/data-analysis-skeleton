# Shared Utilities

Reusable helpers for the data analysis skeleton. Keep modules here small,
generic, and importable from multiple pipeline stages.

## `llm.py`

Helpers for calling OpenAI-compatible LLM endpoints. Supports multiple
providers (RCP, OpenAI) via a `provider` parameter that defaults to `"rcp"`.

### `call_llm()`

Use `call_llm()` when you need one structured LLM call with retries and
Pydantic validation.

```python
import json
import sys
from pathlib import Path

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from utils.llm import call_llm


class EvidenceResponse(BaseModel):
    evidences: list[dict]


system_prompt = Path("0_plan/prompt.txt").read_text(encoding="utf-8").strip()
payload = {"respondent_id": 1, "text": "Example"}

result = call_llm(
    system_prompt,
    json.dumps(payload, ensure_ascii=False),
    EvidenceResponse,
)

# Use OpenAI instead of RCP:
result = call_llm(
    system_prompt,
    json.dumps(payload, ensure_ascii=False),
    EvidenceResponse,
    provider="openai",
)
```

### `call_llm_batch()`

Use `call_llm_batch()` when you want to fan out calls in parallel while keeping
the payload-building and result-writing logic project-specific.

```python
import json
import sys
from pathlib import Path

from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from utils.llm import call_llm_batch


class EvidenceResponse(BaseModel):
    evidences: list[dict]


def build_payload(row, i):
    return json.dumps({"respondent_id": i, "text": row["text"]}, ensure_ascii=False)


def save_result(row, result, i, out_path):
    evidences = [] if result is None else result.evidences
    out_path.write_text(
        json.dumps(
            {"respondent_id": i, "evidences": evidences},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


call_llm_batch(
    items=rows,
    system_prompt=system_prompt,
    response_model=EvidenceResponse,
    build_payload=build_payload,
    save_result=save_result,
    out_dir="2_db/llm_extract",
    parallel=5,
)
```

If you pass `skip_empty=...`, then `save_result()` receives `result=None` for
those items so your script can write an explicit empty output.

### `get_embeddings()`

Use `get_embeddings()` to fetch embedding vectors for a list of texts. Texts
are sent in batches (default 64) and results are returned in input order.

```python
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from utils.llm import get_embeddings

texts = ["first document", "second document", "third document"]
vectors = get_embeddings(texts)

# Use OpenAI embeddings:
vectors = get_embeddings(texts, provider="openai")
```

## Environment

Add your keys to `.env` (only the providers you use):

```bash
RCP_1=your-rcp-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

`utils/llm.py` loads the project root `.env` automatically.

If your script is nested more deeply, compute the root from `__file__` instead
of relying on the current working directory, for example:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
```

## Backward compatibility

The old names `call_rcp` and `call_rcp_batch` are still available as aliases
for `call_llm` and `call_llm_batch`. Prefer the new names in new code.

## Design rule

Only move code here if it is reusable across projects. Keep dataset-specific
schemas, payload construction, CSV parsing, and output formatting in the script
that uses the utility.
