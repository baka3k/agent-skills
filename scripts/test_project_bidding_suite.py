#!/usr/bin/env python3
"""Basic integration tests for Project Bidding Suite."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "bidding-orchestrator" / "scripts" / "generate_bid_package.py"
BRIEF = REPO_ROOT / "bidding-orchestrator" / "examples" / "bid_brief.sample.yaml"
RATE_CARD = REPO_ROOT / "bidding-orchestrator" / "examples" / "rate_card.sample.yaml"
EVIDENCE = REPO_ROOT / "bidding-orchestrator" / "examples" / "evidence_config.sample.yaml"


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO_ROOT, check=True, capture_output=True, text=True)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_golden_path() -> None:
    with tempfile.TemporaryDirectory(prefix="bid-suite-golden-") as tmp:
        out_dir = Path(tmp) / "outputs"
        run_cmd(
            [
                "python",
                str(SCRIPT),
                "--bid-brief",
                str(BRIEF),
                "--evidence-config",
                str(EVIDENCE),
                "--rate-card",
                str(RATE_CARD),
                "--output-dir",
                str(out_dir),
            ]
        )

        assert (out_dir / "proposal" / "proposal.md").exists()
        assert (out_dir / "estimate" / "estimate_summary.json").exists()
        assert (out_dir / "staffing" / "staffing_plan.md").exists()
        assert (out_dir / "quality" / "quality_gates.md").exists()
        assert (out_dir / "evidence" / "evidence_log.json").exists()

        slide_pptx = out_dir / "slides" / "bid_deck.pptx"
        slide_md = out_dir / "slides" / "bid_deck.md"
        assert slide_pptx.exists() or slide_md.exists()

        estimate = read_json(out_dir / "estimate" / "estimate_summary.json")
        assert estimate["effort_pm"]["base"] > 0
        assert estimate["cost"]["fixed_price"] is not None
        assert estimate["cost"]["tm"] is not None


def test_missing_rate_card() -> None:
    with tempfile.TemporaryDirectory(prefix="bid-suite-no-rate-") as tmp:
        out_dir = Path(tmp) / "outputs"
        run_cmd(
            [
                "python",
                str(SCRIPT),
                "--bid-brief",
                str(BRIEF),
                "--evidence-config",
                str(EVIDENCE),
                "--output-dir",
                str(out_dir),
                "--skip-slides",
            ]
        )

        estimate = read_json(out_dir / "estimate" / "estimate_summary.json")
        assert estimate["cost"]["fixed_price"] is None
        assert estimate["cost"]["tm"] is None
        assumptions = "\n".join(estimate.get("assumptions") or [])
        assert "pending" in assumptions.lower()


def test_retrieval_quality_downgrade() -> None:
    with tempfile.TemporaryDirectory(prefix="bid-suite-confidence-") as tmp:
        tmp_root = Path(tmp)
        full_cfg = tmp_root / "full.yaml"
        web_only_cfg = tmp_root / "web_only.yaml"

        full_cfg.write_text(EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")
        web_only_cfg.write_text(
            "\n".join(
                [
                    "mind_source_ids: []",
                    "graph_project_ids: []",
                    "internet_domains_allowlist:",
                    "  - ai.google.dev",
                    "recency_days: 30",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        out_full = tmp_root / "full"
        out_web = tmp_root / "web"

        run_cmd(
            [
                "python",
                str(SCRIPT),
                "--bid-brief",
                str(BRIEF),
                "--evidence-config",
                str(full_cfg),
                "--rate-card",
                str(RATE_CARD),
                "--output-dir",
                str(out_full),
                "--skip-slides",
            ]
        )
        run_cmd(
            [
                "python",
                str(SCRIPT),
                "--bid-brief",
                str(BRIEF),
                "--evidence-config",
                str(web_only_cfg),
                "--rate-card",
                str(RATE_CARD),
                "--output-dir",
                str(out_web),
                "--skip-slides",
            ]
        )

        full_tier = read_json(out_full / "estimate" / "estimate_summary.json")["confidence"]["tier"]
        web_tier = read_json(out_web / "estimate" / "estimate_summary.json")["confidence"]["tier"]
        order = {"Low": 0, "Medium": 1, "High": 2}
        assert order[full_tier] >= order[web_tier]


def test_estimate_consistency() -> None:
    with tempfile.TemporaryDirectory(prefix="bid-suite-consistency-") as tmp:
        out_base = Path(tmp)
        base_values = []
        for idx in range(3):
            out_dir = out_base / f"run_{idx}"
            run_cmd(
                [
                    "python",
                    str(SCRIPT),
                    "--bid-brief",
                    str(BRIEF),
                    "--evidence-config",
                    str(EVIDENCE),
                    "--rate-card",
                    str(RATE_CARD),
                    "--output-dir",
                    str(out_dir),
                    "--skip-slides",
                ]
            )
            base_values.append(read_json(out_dir / "estimate" / "estimate_summary.json")["effort_pm"]["base"])

        avg = sum(base_values) / len(base_values)
        for value in base_values:
            diff = abs(value - avg) / avg if avg else 0
            assert diff <= 0.05


def run_all() -> None:
    test_golden_path()
    test_missing_rate_card()
    test_retrieval_quality_downgrade()
    test_estimate_consistency()
    print("All Project Bidding Suite tests passed.")


if __name__ == "__main__":
    run_all()
