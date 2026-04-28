#!/usr/bin/env python3
"""Analyze large C/C++ source files for migration planning."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple


INLINE_SIG_RE = re.compile(
    r"^\s*(?:[A-Za-z_~][\w:<>,~\s*&]+?)\s+([A-Za-z_~][\w:<>~]*)\s*\([^;]*\)\s*\{\s*$"
)
NOBRACE_SIG_RE = re.compile(
    r"^\s*(?:[A-Za-z_~][\w:<>,~\s*&]+?)\s+([A-Za-z_~][\w:<>~]*)\s*\([^;]*\)\s*$"
)
CONTROL_NAMES = {"if", "for", "while", "switch", "catch"}

PATTERNS = {
    "branch_count": re.compile(r"\b(if|else|for|while|switch|case)\b"),
    "file_io_calls": re.compile(r"\b(fopen|fclose|fseek|fread|fwrite)\b"),
    "crypto_calls": re.compile(r"\b(encryptWrite|decryptRead|calcEncryptLength)\b"),
    "c_buffer_calls": re.compile(r"\b(strcpy|strncpy|strcat|memcpy|memset|strcmp|strncmp)\b"),
    "status_code_tokens": re.compile(r"\b(HHC_TRUE|HHC_FALT|TRUE|FALSE)\b"),
}


@dataclass
class FunctionInfo:
    name: str
    start_line: int
    end_line: int
    lines: int
    branch_count: int
    file_io_calls: int
    crypto_calls: int
    c_buffer_calls: int
    status_code_tokens: int
    risk_score: float


def _sanitize_code_line(line: str, in_block_comment: bool) -> Tuple[str, bool]:
    out = []
    i = 0
    n = len(line)

    while i < n:
        ch = line[i]
        nxt = line[i + 1] if i + 1 < n else ""

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
            else:
                i += 1
            continue

        if ch == "/" and nxt == "/":
            break
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue

        if ch in ('"', "'"):
            quote = ch
            i += 1
            while i < n:
                if line[i] == "\\":
                    i += 2
                    continue
                if line[i] == quote:
                    i += 1
                    break
                i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out), in_block_comment


def _find_function_starts(lines: List[str]) -> List[Tuple[int, int, str]]:
    starts: List[Tuple[int, int, str]] = []
    pending: Tuple[int, str] | None = None
    in_block_comment = False

    for idx, line in enumerate(lines, start=1):
        clean, in_block_comment = _sanitize_code_line(line, in_block_comment)
        stripped = clean.strip()

        if pending and stripped.startswith("{"):
            sig_line, name = pending
            starts.append((sig_line, idx, name))
            pending = None
            continue
        if pending and stripped:
            pending = None

        match_inline = INLINE_SIG_RE.match(stripped)
        if match_inline:
            name = match_inline.group(1).split("::")[-1]
            if name not in CONTROL_NAMES:
                starts.append((idx, idx, match_inline.group(1)))
            continue

        match_no_brace = NOBRACE_SIG_RE.match(stripped)
        if match_no_brace and not stripped.endswith(";"):
            name = match_no_brace.group(1).split("::")[-1]
            if name not in CONTROL_NAMES:
                pending = (idx, match_no_brace.group(1))

    return starts


def _find_end_line(lines: List[str], brace_line: int) -> int:
    depth = 0
    in_block_comment = False

    for idx in range(brace_line, len(lines) + 1):
        clean, in_block_comment = _sanitize_code_line(lines[idx - 1], in_block_comment)
        depth += clean.count("{")
        depth -= clean.count("}")

        if depth == 0 and idx > brace_line:
            return idx

    return len(lines)


def _metrics_for_text(text: str) -> dict:
    values = {key: len(regex.findall(text)) for key, regex in PATTERNS.items()}
    return values


def _risk_score(lines: int, metrics: dict) -> float:
    score = 0.0
    score += lines / 120.0
    score += metrics["branch_count"] * 0.4
    score += metrics["file_io_calls"] * 1.2
    score += metrics["crypto_calls"] * 1.5
    score += metrics["c_buffer_calls"] * 0.2
    score += metrics["status_code_tokens"] * 0.3
    return round(score, 2)


def analyze_cpp_file(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    starts = _find_function_starts(lines)
    functions: List[FunctionInfo] = []

    for i, (start_line, brace_line, name) in enumerate(starts):
        next_start = starts[i + 1][0] if i + 1 < len(starts) else len(lines) + 1
        end_line = _find_end_line(lines, brace_line)
        if end_line >= next_start:
            end_line = next_start - 1
        if end_line < start_line:
            end_line = start_line
        body = "\n".join(lines[start_line - 1 : end_line])
        metrics = _metrics_for_text(body)
        info = FunctionInfo(
            name=name,
            start_line=start_line,
            end_line=end_line,
            lines=end_line - start_line + 1,
            risk_score=_risk_score(end_line - start_line + 1, metrics),
            **metrics,
        )
        functions.append(info)

    file_text = "\n".join(lines)
    whole_file_metrics = _metrics_for_text(file_text)

    return {
        "file_path": str(path),
        "total_lines": len(lines),
        "function_count": len(functions),
        "whole_file_metrics": whole_file_metrics,
        "functions": [asdict(f) for f in functions],
    }


def write_markdown_report(data: dict, min_lines: int, top: int, out_path: Path) -> None:
    funcs = data["functions"]
    long_funcs = [f for f in funcs if f["lines"] >= min_lines]
    long_funcs.sort(key=lambda x: (x["lines"], x["risk_score"]), reverse=True)
    top_funcs = long_funcs[:top]

    lines = []
    lines.append("# C/C++ Porting Scope Analysis")
    lines.append("")
    lines.append(f"- File: `{data['file_path']}`")
    lines.append(f"- Total lines: `{data['total_lines']}`")
    lines.append(f"- Functions discovered: `{data['function_count']}`")
    lines.append(f"- Functions >= {min_lines} lines: `{len(long_funcs)}`")
    lines.append("")
    lines.append("## Whole-file risk signals")
    lines.append("")
    for key, value in data["whole_file_metrics"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Top long functions")
    lines.append("")
    lines.append(
        "| Function | Start | End | Lines | Risk | Branches | File IO | Crypto | C-buffer | Status |"
    )
    lines.append(
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for f in top_funcs:
        lines.append(
            "| "
            f"`{f['name']}` | {f['start_line']} | {f['end_line']} | {f['lines']} | "
            f"{f['risk_score']} | {f['branch_count']} | {f['file_io_calls']} | "
            f"{f['crypto_calls']} | {f['c_buffer_calls']} | {f['status_code_tokens']} |"
        )
    lines.append("")
    lines.append("## Suggested immediate targets")
    lines.append("")
    for idx, f in enumerate(top_funcs[:10], start=1):
        lines.append(
            f"{idx}. `{f['name']}` at lines {f['start_line']}-{f['end_line']} "
            f"(len={f['lines']}, risk={f['risk_score']})"
        )
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze C/C++ file migration scope.")
    parser.add_argument("source_file", type=Path, help="Path to .c/.cpp/.h source file")
    parser.add_argument("--min-lines", type=int, default=120, help="Long-function threshold")
    parser.add_argument("--top", type=int, default=20, help="Top long functions in markdown")
    parser.add_argument("--json", type=Path, help="Output JSON path")
    parser.add_argument("--md", type=Path, help="Output Markdown path")
    args = parser.parse_args()

    data = analyze_cpp_file(args.source_file)

    if args.json:
        args.json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.md:
        write_markdown_report(data, args.min_lines, args.top, args.md)

    print(
        json.dumps(
            {
                "file_path": data["file_path"],
                "total_lines": data["total_lines"],
                "function_count": data["function_count"],
                "long_functions": len([f for f in data["functions"] if f["lines"] >= args.min_lines]),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
