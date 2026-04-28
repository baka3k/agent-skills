#!/usr/bin/env python3
"""Standalone estimator utility for bid-estimator skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml

COMPLEXITY = {"low": 0.85, "med": 1.0, "medium": 1.0, "high": 1.25}


def load_structured(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def blended_rate(rate_card: Dict[str, Any]) -> float | None:
    policy = (rate_card or {}).get("blended_rate_policy") or {}
    explicit = policy.get("blended_monthly_rate")
    if explicit is not None:
        return float(explicit)

    roles = (rate_card or {}).get("roles") or []
    values = [float(x.get("monthly_rate")) for x in roles if x.get("monthly_rate") is not None]
    if values:
        return sum(values) / len(values)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute bid estimate from WBS.")
    parser.add_argument("--wbs-json", required=True, help="JSON/YAML list of modules with base_pm and complexity")
    parser.add_argument("--rate-card", default=None, help="Optional rate card YAML/JSON")
    args = parser.parse_args()

    wbs = load_structured(Path(args.wbs_json))
    if not isinstance(wbs, list) or not wbs:
        raise SystemExit("WBS must be a non-empty list")

    weighted = []
    base_pm = 0.0
    for row in wbs:
        module = str(row.get("module", "Unnamed"))
        base = float(row.get("base_pm", 1.0))
        complexity = str(row.get("complexity", "medium")).lower()
        multiplier = COMPLEXITY.get(complexity, 1.0)
        value = base * multiplier
        weighted.append({
            "module": module,
            "base_pm": base,
            "complexity": complexity,
            "multiplier": multiplier,
            "weighted_pm": round(value, 3),
        })
        base_pm += value

    best_pm = round(base_pm * 0.85, 2)
    worst_pm = round(base_pm * 1.30, 2)

    payload: Dict[str, Any] = {
        "wbs": weighted,
        "effort_pm": {
            "best": best_pm,
            "base": round(base_pm, 2),
            "worst": worst_pm,
        },
    }

    if args.rate_card:
        card = load_structured(Path(args.rate_card)) or {}
        rate = blended_rate(card)
        if rate is not None:
            payload["fixed_price"] = {
                "blended_monthly_rate": round(rate, 2),
                "best": round(best_pm * rate * 1.15, 2),
                "base": round(base_pm * rate * 1.15, 2),
                "worst": round(worst_pm * rate * 1.15, 2),
            }

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
