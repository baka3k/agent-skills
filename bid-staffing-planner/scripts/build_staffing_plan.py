#!/usr/bin/env python3
"""Standalone staffing planner utility for bid-staffing-planner skill."""

from __future__ import annotations

import argparse
import json
import re

PHASES = {
    "Discovery": 0.12,
    "Foundation/Architecture": 0.18,
    "Build": 0.50,
    "Stabilize/UAT": 0.15,
    "Go-live/Hypercare": 0.05,
}


def parse_months(timeline: str, base_pm: float) -> float:
    text = (timeline or "").lower()
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if not m:
        return max(base_pm / 6.0, 1.0)
    value = float(m.group(1))
    if "week" in text:
        return max(value / 4.33, 0.5)
    return max(value, 0.5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build staffing phase plan from base PM")
    parser.add_argument("--base-pm", required=True, type=float)
    parser.add_argument("--timeline", default="6 months")
    args = parser.parse_args()

    months = parse_months(args.timeline, args.base_pm)
    phase_pm = {name: round(args.base_pm * ratio, 2) for name, ratio in PHASES.items()}

    payload = {
        "base_pm": args.base_pm,
        "duration_months": round(months, 2),
        "phase_pm": phase_pm,
        "avg_team_size": round(args.base_pm / months, 2),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
