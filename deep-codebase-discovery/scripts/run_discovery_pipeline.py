#!/usr/bin/env python3
"""Run local companion analysis scripts for deep codebase discovery.

This helper is intentionally lightweight:
- Runs repo-recon and tech-build-audit scripts when available.
- Produces JSON/Markdown outputs in one output directory.
- Writes a manifest with execution status for each stage.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run local deep discovery pipeline via companion skill scripts.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository root path to analyze (default: current directory).",
    )
    parser.add_argument(
        "--output-dir",
        default="./deep_discovery_output",
        help="Output directory for generated artifacts.",
    )
    parser.add_argument(
        "--python",
        dest="python_bin",
        default=sys.executable,
        help="Python executable used to run companion scripts.",
    )
    return parser.parse_args()


def resolve_script_paths() -> Dict[str, Path]:
    # .../skills/deep-codebase-discovery/scripts/run_discovery_pipeline.py
    # -> skills root is parents[2]
    skills_root = Path(__file__).resolve().parents[2]
    return {
        "repo_recon": skills_root / "repo-recon" / "scripts" / "repo_recon.py",
        "tech_build_audit": skills_root / "tech-build-audit" / "scripts" / "tech_build_audit.py",
    }


def run_stage(
    python_bin: str,
    script_path: Path,
    repo_path: Path,
    json_out: Path,
    md_out: Path,
) -> Dict[str, str]:
    if not script_path.exists():
        return {
            "status": "missing",
            "script": str(script_path),
            "message": "Companion script not found",
        }

    command = [
        python_bin,
        str(script_path),
        str(repo_path),
        "--json",
        str(json_out),
        "--md",
        str(md_out),
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return {
            "status": "failed",
            "script": str(script_path),
            "message": result.stderr.strip() or "Command returned non-zero exit code",
            "stdout": result.stdout.strip(),
        }

    return {
        "status": "ok",
        "script": str(script_path),
        "json_output": str(json_out),
        "md_output": str(md_out),
    }


def main() -> int:
    args = parse_args()
    repo_path = Path(args.path).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not repo_path.exists() or not repo_path.is_dir():
        print(f"Error: Invalid repository path: {repo_path}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)
    scripts = resolve_script_paths()

    stages: List[Dict[str, str]] = []
    stages.append(
        {
            "name": "repo_recon",
            **run_stage(
                python_bin=args.python_bin,
                script_path=scripts["repo_recon"],
                repo_path=repo_path,
                json_out=output_dir / "repo_recon.json",
                md_out=output_dir / "repo_recon.md",
            ),
        }
    )
    stages.append(
        {
            "name": "tech_build_audit",
            **run_stage(
                python_bin=args.python_bin,
                script_path=scripts["tech_build_audit"],
                repo_path=repo_path,
                json_out=output_dir / "tech_build_audit.json",
                md_out=output_dir / "tech_build_audit.md",
            ),
        }
    )

    manifest = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "repository": str(repo_path),
        "output_dir": str(output_dir),
        "stages": stages,
        "note": "Run module-summary-report skill after these artifacts are generated.",
    }

    manifest_path = output_dir / "discovery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for stage in stages:
        print(f"[{stage['name']}] {stage['status']}")
        if stage["status"] != "ok":
            print(f"  {stage.get('message', 'No details')}")

    print(f"Manifest: {manifest_path}")

    has_failure = any(stage["status"] == "failed" for stage in stages)
    has_success = any(stage["status"] == "ok" for stage in stages)
    if has_failure:
        return 1
    if not has_success:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
