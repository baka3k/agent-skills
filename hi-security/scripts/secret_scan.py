#!/usr/bin/env python3
"""Run secret detection scan as part of hi-security audit pipeline."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]

SECRET_PATTERNS = [
    (
        "API Key",
        re.compile(
            r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9\-_]{20,}['\"]"
        ),
        "critical",
    ),
    (
        "AWS Access Key",
        re.compile(r"AKIA[0-9A-Z]{16}"),
        "critical",
    ),
    (
        "JWT Token",
        re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
        "critical",
    ),
    (
        "Hardcoded Password",
        re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
        "critical",
    ),
    (
        "Private Key (PEM)",
        re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        "critical",
    ),
    (
        "GitHub Token",
        re.compile(r"ghp_[A-Za-z0-9]{36}"),
        "critical",
    ),
    (
        "Stripe Key",
        re.compile(r"sk_(live|test)_[A-Za-z0-9]{24,}"),
        "critical",
    ),
    (
        "Bearer Token",
        re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]{20,}"),
        "critical",
    ),
    (
        "DB Connection String",
        re.compile(
            r"(?i)(postgresql|mongodb|mysql|redis)://[^:\s]+:[^@\s]+@"
        ),
        "high",
    ),
    (
        "Email in Code",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "medium",
    ),
]

SKIP_PATTERNS = [
    "*.test.*",
    "*.spec.*",
    "*.example",
    "*.example.*",
    "*.md",
    "__pycache__",
    "node_modules",
    ".git",
    "vendor",
    "dist",
    "build",
]

SKIP_DIRS = {"test", "tests", "__tests__", "fixtures", "examples", "mocks"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Secret detection scan for hi-security skill."
    )
    parser.add_argument(
        "--source-root",
        required=True,
        help="Root directory to scan for secrets.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file for findings.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def should_skip(path: Path, source_root: Path) -> bool:
    rel = path.relative_to(source_root)
    parts = rel.parts
    for part in parts:
        if part in SKIP_DIRS:
            return True
    name = path.name.lower()
    for pattern in SKIP_PATTERNS:
        if Path(name).match(pattern):
            return True
    return False


def scan_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return findings

    lines = content.splitlines()
    for pattern_name, regex, severity in SECRET_PATTERNS:
        for i, line in enumerate(lines, start=1):
            match = regex.search(line)
            if not match:
                continue
            matched = match.group(0)
            if any(
                placeholder in matched.lower()
                for placeholder in [
                    "your_key_here",
                    "<your-token>",
                    "todo",
                    "placeholder",
                    "redacted",
                ]
            ):
                continue
            findings.append(
                {
                    "type": pattern_name,
                    "severity": severity,
                    "file": str(path),
                    "line": i,
                    "match": matched[:80],
                }
            )
    return findings


def main() -> int:
    args = parse_args()
    source_root = Path(args.source_root).expanduser().resolve()

    if not source_root.exists() or not source_root.is_dir():
        print(f"Error: Source root does not exist: {source_root}", flush=True)
        return 2

    all_findings: list[dict] = []
    files_scanned = 0

    for path in source_root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path, source_root):
            continue
        files_scanned += 1
        findings = scan_file(path)
        all_findings.extend(findings)

    result = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "source_root": str(source_root),
        "skill": "hi-security",
        "files_scanned": files_scanned,
        "findings_count": len(all_findings),
        "findings": all_findings,
    }

    if args.format == "json":
        out = args.output or "secret_findings.json"
        Path(out).write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Secret scan complete: {len(all_findings)} findings → {out}")
    else:
        print(
            f"Secret scan complete: {files_scanned} files, {len(all_findings)} findings"
        )
        for f in all_findings:
            print(
                f"  [{f['severity'].upper():8}] {f['type']:20} "
                f"{f['file']}:{f['line']}  {f['match']}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
