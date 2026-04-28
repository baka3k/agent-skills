#!/usr/bin/env python3
"""Build a slide brief from generated bid artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build markdown slide brief for bid deck generation")
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--estimate", required=True)
    parser.add_argument("--staffing", required=True)
    parser.add_argument("--quality", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--output", default="outputs/slides/slide_brief.md")
    args = parser.parse_args()

    estimate = load_json(Path(args.estimate))
    evidence = load_json(Path(args.evidence))

    citations = sorted(
        {
            e.get("citation", "")
            for e in evidence
            if e.get("source_type") in {"internet", "mind_mcp", "graph_mcp"}
        }
    )

    brief = "\n".join(
        [
            "# Bid Deck Brief",
            "",
            "## Slide Order",
            "1. Executive summary",
            "2. Scope in/out",
            "3. Baseline vs optimized solution",
            "4. Estimate and cost ranges",
            "5. Staffing plan",
            "6. Quality gates",
            "7. Citations and assumptions",
            "",
            "## Key Metrics",
            f"- Effort PM best/base/worst: {estimate['effort_pm']['best']} / {estimate['effort_pm']['base']} / {estimate['effort_pm']['worst']}",
            f"- Confidence tier: {estimate['confidence']['tier']}",
            "",
            "## Gemini Visual Guidance",
            "- Resolve model availability from official models/changelog before generation.",
            "- Do not hardcode one model id.",
            "- If image generation fails, use placeholder visual and continue deck generation.",
            "",
            "## Citations",
            *(f"- {c}" for c in citations if c),
            "",
            "## Source Artifact Paths",
            f"- Proposal: {args.proposal}",
            f"- Estimate: {args.estimate}",
            f"- Staffing: {args.staffing}",
            f"- Quality: {args.quality}",
            f"- Evidence: {args.evidence}",
        ]
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(brief + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
