#!/usr/bin/env python3
"""Generate a phased migration plan from analyze_cpp_scope JSON output."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def _select_targets(functions: list, min_lines: int, max_functions: int) -> list:
    targets = [f for f in functions if f["lines"] >= min_lines]
    targets.sort(key=lambda x: (x["risk_score"], x["lines"]), reverse=True)
    return targets[:max_functions]


def _slice_count(lines: int, slice_size: int, max_slices: int) -> int:
    return max(1, min(max_slices, math.ceil(lines / float(slice_size))))


def build_plan_markdown(
    analysis: dict,
    target_name: str,
    min_lines: int,
    max_functions: int,
    slice_size: int,
    max_slices: int,
) -> str:
    targets = _select_targets(analysis["functions"], min_lines, max_functions)

    lines = []
    lines.append(f"# Port Plan: {target_name}")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Source file: `{analysis['file_path']}`")
    lines.append(f"- Total lines: `{analysis['total_lines']}`")
    lines.append(f"- Functions discovered: `{analysis['function_count']}`")
    lines.append(f"- Target functions in this plan: `{len(targets)}`")
    lines.append("")
    lines.append("## Phase 0 - Baseline")
    lines.append("")
    lines.append("- Freeze legacy behavior before edits.")
    lines.append("- Build minimal golden cases for every selected function.")
    lines.append("- Record return codes, side effects, and output format.")
    lines.append("")
    lines.append("## Phase 1 - Behavior Contracts")
    lines.append("")
    lines.append("- Create one contract per selected function.")
    lines.append("- Capture edge cases and state dependencies.")
    lines.append("- Mark unknown logic as explicit open risks.")
    lines.append("")
    lines.append("## Phase 2 - Slice Migration Order")
    lines.append("")
    lines.append("| Priority | Function | Lines | Risk | Suggested Slices | High-risk Signals |")
    lines.append("| ---: | --- | ---: | ---: | ---: | --- |")

    for idx, f in enumerate(targets, start=1):
        high_risk = []
        if f["file_io_calls"] > 0:
            high_risk.append("file_io")
        if f["crypto_calls"] > 0:
            high_risk.append("crypto_io")
        if f["c_buffer_calls"] > 0:
            high_risk.append("c_buffer")
        if f["status_code_tokens"] > 0:
            high_risk.append("status_codes")
        if not high_risk:
            high_risk.append("control_flow")

        lines.append(
            f"| {idx} | `{f['name']}` | {f['lines']} | {f['risk_score']} | "
            f"{_slice_count(f['lines'], slice_size, max_slices)} | {', '.join(high_risk)} |"
        )

    lines.append("")
    lines.append("## Phase 3 - Per-slice Execution Checklist")
    lines.append("")
    lines.append("1. Implement one slice only.")
    lines.append("2. Run parity cases for touched behavior.")
    lines.append("3. Confirm return codes and side effects match.")
    lines.append("4. Update migration ledger.")
    lines.append("5. Proceed to next slice only if all checks pass.")
    lines.append("")
    lines.append("## Phase 4 - Stabilize and Refactor")
    lines.append("")
    lines.append("- Keep parity green while extracting helpers and cleanup.")
    lines.append("- Add regression tests for previously unknown edge cases.")
    lines.append("- Remove temporary compatibility shims only after test proof.")
    lines.append("")
    lines.append("## Exit Criteria")
    lines.append("")
    lines.append("- Full parity pass on selected migration scope.")
    lines.append("- No unresolved high-severity behavior gaps.")
    lines.append("- Regression suite covers all converted slices.")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate migration plan markdown.")
    parser.add_argument("--analysis-json", type=Path, required=True, help="Input JSON from analyze_cpp_scope.py")
    parser.add_argument("--target", default="LegacyModule", help="Target module/class name")
    parser.add_argument("--min-lines", type=int, default=120, help="Minimum lines for target function")
    parser.add_argument("--max-functions", type=int, default=15, help="Max functions to include")
    parser.add_argument("--slice-size", type=int, default=250, help="Approx lines per migration slice")
    parser.add_argument("--max-slices", type=int, default=8, help="Upper bound for suggested slices")
    parser.add_argument("--out", type=Path, help="Output markdown path")
    args = parser.parse_args()

    analysis = json.loads(args.analysis_json.read_text(encoding="utf-8"))
    content = build_plan_markdown(
        analysis=analysis,
        target_name=args.target,
        min_lines=args.min_lines,
        max_functions=args.max_functions,
        slice_size=args.slice_size,
        max_slices=args.max_slices,
    )

    if args.out:
        args.out.write_text(content + "\n", encoding="utf-8")
    else:
        print(content)


if __name__ == "__main__":
    main()
