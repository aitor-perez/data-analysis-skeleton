"""Helpers for calling the EPFL RCP inference endpoint."""

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
RCP_ENDPOINT = "https://inference.rcp.epfl.ch/v1/chat/completions"

load_dotenv(PROJECT_ROOT / ".env")

TModel = TypeVar("TModel", bound=BaseModel)


def _get_api_key(api_key_env: str) -> str:
    api_key = (os.getenv(api_key_env) or "").strip()
    if not api_key:
        raise RuntimeError(f"Missing {api_key_env} in .env")
    return api_key


def _parse_response(response: requests.Response, response_model: type[TModel]) -> TModel:
    try:
        data = response.json()
    except Exception as exc:
        body_preview = (response.text or "")[:500]
        raise ValueError(
            f"Invalid HTTP JSON response from RCP endpoint: {exc}; "
            f"body preview: {body_preview}"
        ) from exc

    choices = data.get("choices") or []
    if not choices:
        raise ValueError(f"RCP response missing choices: {json.dumps(data)[:500]}")

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
            raise ValueError(f"RCP refused response: {refusal}")
        raise ValueError(
            "RCP response missing parsable message content. "
            f"message keys: {list(message.keys())}"
        )

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        content_preview = content[:500]
        raise ValueError(
            f"RCP returned invalid JSON content: {exc}; "
            f"content preview: {content_preview}"
        ) from exc

    try:
        return response_model.model_validate(parsed)
    except Exception as exc:
        raise ValueError(
            f"RCP JSON could not be validated against {response_model.__name__}: {exc}"
        ) from exc


def call_rcp(
    system_prompt: str,
    user_content: str,
    response_model: type[TModel],
    *,
    model: str = "Qwen/Qwen3-VL-235B-A22B-Thinking",
    temperature: float = 0.1,
    max_tokens: int = 16000,
    timeout: int = 600,
    max_retries: int = 3,
    retry_wait: float = 2.0,
    api_key_env: str = "RCP_1",
) -> TModel:
    """Call the RCP endpoint and return a validated Pydantic model."""
    api_key = _get_api_key(api_key_env)
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                RCP_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
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
            )
            response.raise_for_status()
            return _parse_response(response, response_model)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                time.sleep(retry_wait * attempt)
                continue
            raise ValueError(
                f"RCP call failed after {max_retries} attempts: {last_error}"
            ) from exc

    raise ValueError(f"RCP call failed after {max_retries} attempts: {last_error}")


def call_rcp_batch(
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
    model: str = "Qwen/Qwen3-VL-235B-A22B-Thinking",
    temperature: float = 0.1,
    max_tokens: int = 16000,
    timeout: int = 600,
    max_retries: int = 3,
    retry_wait: float = 2.0,
    api_key_env: str = "RCP_1",
) -> list[str]:
    """Call the RCP endpoint in parallel over a list of items.

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

            print(f"[{index}] calling RCP...", flush=True)
            started = time.time()
            result = call_rcp(
                system_prompt,
                build_payload(item, index),
                response_model,
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
        f"Processing {total} items (parallel={parallel}, skip_existing={skip_existing})",
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
