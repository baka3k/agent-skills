#!/usr/bin/env python3
"""Resolve an image-capable Gemini model without hardcoding one model id."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List

GEMINI_MODELS_API = "https://generativelanguage.googleapis.com/v1beta/models"
DOC_MODEL_URL = "https://ai.google.dev/gemini-api/docs/models"
DOC_CHANGELOG_URL = "https://ai.google.dev/gemini-api/docs/changelog"

MODEL_PATTERN = re.compile(r"gemini-[a-z0-9.-]+", re.IGNORECASE)


def fetch_json(url: str, timeout: int = 10) -> Dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = 10) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def rank_models(candidates: List[str]) -> List[str]:
    def score(model: str) -> tuple[int, int, str]:
        lower = model.lower()
        image_bias = 0
        if "image" in lower:
            image_bias -= 50
        if "preview" in lower:
            image_bias -= 10
        if "exp" in lower:
            image_bias += 5
        return (image_bias, len(model), model)

    return sorted(set(candidates), key=score)


def resolve_from_api(api_key: str, timeout: int = 10) -> Dict[str, Any]:
    url = f"{GEMINI_MODELS_API}?key={api_key}"
    payload = fetch_json(url, timeout=timeout)
    models = payload.get("models", [])

    candidates = []
    for item in models:
        name = str(item.get("name", ""))
        if not name:
            continue
        model_id = name.split("/")[-1]
        methods = item.get("supportedGenerationMethods", [])
        text = json.dumps(item).lower()
        if "image" in model_id.lower() or "image" in text or "generatecontent" in [m.lower() for m in methods]:
            candidates.append(model_id)

    ranked = rank_models(candidates)
    if not ranked:
        raise RuntimeError("No candidate Gemini models found from API listing")

    return {
        "source": "api",
        "chosen_model": ranked[0],
        "candidates": ranked,
        "degraded": False,
    }


def resolve_from_docs(timeout: int = 10) -> Dict[str, Any]:
    text = fetch_text(DOC_MODEL_URL, timeout=timeout) + "\n" + fetch_text(DOC_CHANGELOG_URL, timeout=timeout)
    candidates = [m.lower() for m in MODEL_PATTERN.findall(text)]
    ranked = rank_models(candidates)
    if not ranked:
        raise RuntimeError("No Gemini model names found in docs/changelog")

    return {
        "source": "docs",
        "chosen_model": ranked[0],
        "candidates": ranked,
        "degraded": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a Gemini model dynamically")
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY", help="Environment variable for Gemini API key")
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env, "").strip()

    errors: List[str] = []
    if api_key:
        try:
            result = resolve_from_api(api_key, timeout=args.timeout)
            print(json.dumps(result, indent=2))
            return 0
        except Exception as exc:
            errors.append(f"API resolution failed: {exc}")

    try:
        result = resolve_from_docs(timeout=args.timeout)
        if errors:
            result["notes"] = errors
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        errors.append(f"Docs fallback failed: {exc}")
        print(
            json.dumps(
                {
                    "source": "none",
                    "chosen_model": None,
                    "candidates": [],
                    "degraded": True,
                    "errors": errors,
                },
                indent=2,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
