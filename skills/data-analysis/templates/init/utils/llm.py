"""Helpers for calling OpenAI-compatible LLM endpoints (RCP, OpenAI)."""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, TypeVar

import requests
from dotenv import load_dotenv
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TModel = TypeVar("TModel", bound=BaseModel)

PROVIDERS: dict[str, dict[str, str]] = {
    "rcp": {
        "base_url": "https://inference.rcp.epfl.ch/v1",
        "api_key_env": "RCP_1",
        "default_chat_model": "Qwen/Qwen3-VL-235B-A22B-Thinking",
        "default_embedding_model": "nvidia/NV-Embed-v2",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_chat_model": "gpt-4o",
        "default_embedding_model": "text-embedding-3-small",
    },
}


def _get_provider(provider: str) -> dict[str, str]:
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider {provider!r}. "
            f"Available: {', '.join(PROVIDERS)}"
        )
    return PROVIDERS[provider]


def _get_api_key(api_key_env: str) -> str:
    api_key = (os.getenv(api_key_env) or "").strip()
    if not api_key:
        raise RuntimeError(f"Missing {api_key_env} in .env")
    return api_key


def _request_with_retries(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    json_body: dict[str, Any],
    timeout: int,
    max_retries: int,
    retry_wait: float,
    label: str = "LLM",
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.request(
                method, url,
                headers=headers,
                json=json_body,
                timeout=timeout,
            )
            response.raise_for_status()
            return response
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(retry_wait * attempt)
                continue
            raise ValueError(
                f"{label} call failed after {max_retries} attempts: {last_error}"
            ) from exc
    raise ValueError(f"{label} call failed after {max_retries} attempts: {last_error}")


def _parse_chat_response(
    response: requests.Response, response_model: type[TModel],
) -> TModel:
    try:
        data = response.json()
    except Exception as exc:
        body_preview = (response.text or "")[:500]
        raise ValueError(
            f"Invalid JSON from endpoint: {exc}; body preview: {body_preview}"
        ) from exc

    choices = data.get("choices") or []
    if not choices:
        raise ValueError(f"Response missing choices: {json.dumps(data)[:500]}")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, list):
        content = "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    if not isinstance(content, str) or not content.strip():
        refusal = message.get("refusal")
        if refusal:
            raise ValueError(f"Model refused response: {refusal}")
        raise ValueError(
            f"Response missing parsable content. message keys: {list(message.keys())}"
        )

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in content: {exc}; preview: {content[:500]}"
        ) from exc

    try:
        return response_model.model_validate(parsed)
    except Exception as exc:
        raise ValueError(
            f"JSON could not be validated against {response_model.__name__}: {exc}"
        ) from exc


# ---------------------------------------------------------------------------
# Chat completions
# ---------------------------------------------------------------------------

def call_llm(
    system_prompt: str,
    user_content: str,
    response_model: type[TModel],
    *,
    provider: str = "rcp",
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 16000,
    timeout: int = 600,
    max_retries: int = 3,
    retry_wait: float = 2.0,
    api_key_env: str | None = None,
) -> TModel:
    """Call an OpenAI-compatible chat endpoint and return a validated Pydantic model."""
    prov = _get_provider(provider)
    api_key = _get_api_key(api_key_env or prov["api_key_env"])
    model = model or prov["default_chat_model"]

    response = _request_with_retries(
        "POST",
        f"{prov['base_url']}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json_body={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": response_model.model_json_schema(),
                },
            },
        },
        timeout=timeout,
        max_retries=max_retries,
        retry_wait=retry_wait,
        label=f"LLM({provider})",
    )
    return _parse_chat_response(response, response_model)


def call_llm_batch(
    items: list[Any],
    system_prompt: str,
    response_model: type[TModel],
    *,
    build_payload: Callable[[Any, int], str],
    save_result: Callable[[Any, TModel | None, int, Path], None],
    out_dir: str | Path,
    file_pattern: str = "item_{i:04d}.json",
    skip_existing: bool = True,
    skip_empty: Callable[[Any, int], bool] | None = None,
    parallel: int = 5,
    provider: str = "rcp",
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 16000,
    timeout: int = 600,
    max_retries: int = 3,
    retry_wait: float = 2.0,
    api_key_env: str | None = None,
) -> list[str]:
    """Call the LLM endpoint in parallel over a list of items.

    `save_result()` receives `None` when `skip_empty()` returns True, which lets
    project scripts decide what an empty output should look like.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    def process_one(index: int, item: Any) -> str:
        out_path = out_dir / file_pattern.format(i=index)
        try:
            if skip_existing and out_path.exists():
                return f"[{index}] skip"

            if skip_empty and skip_empty(item, index):
                save_result(item, None, index, out_path)
                return f"[{index}] empty"

            print(f"[{index}] calling {provider}...", flush=True)
            started = time.time()
            result = call_llm(
                system_prompt,
                build_payload(item, index),
                response_model,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                max_retries=max_retries,
                retry_wait=retry_wait,
                api_key_env=api_key_env,
            )
            elapsed = time.time() - started
            save_result(item, result, index, out_path)
            return f"[{index}] ok ({elapsed:.1f}s)"
        except Exception as exc:
            return f"[{index}] ERROR: {exc}"

    total = len(items)
    print(
        f"Processing {total} items (provider={provider}, parallel={parallel}, "
        f"skip_existing={skip_existing})",
        flush=True,
    )

    messages: list[str] = []
    done = 0
    started = time.time()
    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = [
            executor.submit(process_one, index, item)
            for index, item in enumerate(items, start=1)
        ]
        for future in as_completed(futures):
            done += 1
            try:
                message = future.result()
            except Exception as exc:
                message = f"[fatal-worker-error] {exc}"
            messages.append(message)
            elapsed = time.time() - started
            print(f"  ({done}/{total}, {elapsed:.0f}s) {message}", flush=True)

    return messages


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

def get_embeddings(
    texts: list[str],
    *,
    provider: str = "rcp",
    model: str | None = None,
    batch_size: int = 64,
    timeout: int = 120,
    max_retries: int = 3,
    retry_wait: float = 2.0,
    api_key_env: str | None = None,
) -> list[list[float]]:
    """Fetch embeddings for a list of texts in batches.

    Returns one embedding vector per input text, in the same order.
    """
    prov = _get_provider(provider)
    api_key = _get_api_key(api_key_env or prov["api_key_env"])
    model = model or prov["default_embedding_model"]
    url = f"{prov['base_url']}/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    all_embeddings: list[list[float]] = [[] for _ in texts]

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        response = _request_with_retries(
            "POST", url,
            headers=headers,
            json_body={"model": model, "input": batch},
            timeout=timeout,
            max_retries=max_retries,
            retry_wait=retry_wait,
            label=f"Embeddings({provider})",
        )
        try:
            data = response.json()
        except Exception as exc:
            raise ValueError(
                f"Invalid JSON from embeddings endpoint: {exc}"
            ) from exc

        items = data.get("data") or []
        if len(items) != len(batch):
            raise ValueError(
                f"Expected {len(batch)} embeddings, got {len(items)}"
            )
        for item in items:
            all_embeddings[start + item["index"]] = item["embedding"]

    return all_embeddings


# ---------------------------------------------------------------------------
# Backward-compatible aliases
# ---------------------------------------------------------------------------

call_rcp = call_llm
call_rcp_batch = call_llm_batch
