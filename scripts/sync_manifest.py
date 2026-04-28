#!/usr/bin/env python3
"""Sync MANIFEST.json skill entries from discovered SKILL.md directories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from skill_parser import parse_skill_file

DEFAULT_PLATFORMS = ["claude-code", "cursor", "continue", "copilot", "codex"]

CATEGORY_OVERRIDES = {
    "bidding-orchestrator": "orchestration",
    "bid-evidence-hub": "analysis",
    "bid-solution-designer": "synthesis",
    "bid-quality-gates": "analysis",
    "bid-estimator": "analysis",
    "bid-staffing-planner": "analysis",
    "bid-slide-factory": "documentation",
    "deep-codebase-discovery": "orchestration",
    "repo-recon": "analysis",
    "tech-build-audit": "analysis",
    "module-summary-report": "synthesis",
    "reverse-doc-reconstruction": "documentation",
    "legacy-cpp-porting-guardrails": "porting",
    "bug-impact-analyzer": "analysis",
}

DEPENDENCY_OVERRIDES = {
    "bidding-orchestrator": [
        "bid-evidence-hub",
        "bid-solution-designer",
        "bid-quality-gates",
        "bid-estimator",
        "bid-staffing-planner",
        "bid-slide-factory",
    ],
    "deep-codebase-discovery": ["repo-recon", "tech-build-audit", "module-summary-report"],
    "module-summary-report": ["repo-recon", "tech-build-audit"],
}


def discover_skill_files(root: Path) -> List[Path]:
    skills: List[Path] = []
    for item in sorted(root.iterdir()):
        skill_file = item / "SKILL.md"
        if item.is_dir() and skill_file.exists():
            skills.append(skill_file)
    return skills


def _default_display_name(skill_id: str, parsed_name: str) -> str:
    if parsed_name and parsed_name != skill_id:
        return parsed_name.replace("-", " ").strip().title()
    return skill_id.replace("-", " ").strip().title()


def build_skill_entry(skill_id: str, skill_data: Dict[str, Any], existing: Dict[str, Any]) -> Dict[str, Any]:
    existing_platforms = existing.get("platforms", [])
    if isinstance(existing_platforms, list) and existing_platforms:
        platforms = list(dict.fromkeys(existing_platforms + DEFAULT_PLATFORMS))
    else:
        platforms = DEFAULT_PLATFORMS

    entry: Dict[str, Any] = {}
    entry["id"] = skill_id
    entry["name"] = existing.get("name") or _default_display_name(skill_id, str(skill_data.get("name", "")))
    entry["description"] = str(skill_data.get("description") or existing.get("description") or "").strip()
    entry["category"] = existing.get("category") or CATEGORY_OVERRIDES.get(skill_id, "analysis")
    entry["path"] = f"{skill_id}/SKILL.md"
    entry["dependencies"] = existing.get("dependencies", DEPENDENCY_OVERRIDES.get(skill_id, []))
    entry["platforms"] = platforms
    return entry


def sync_manifest(manifest_path: Path, root: Path) -> Dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_entries = {entry.get("id"): entry for entry in manifest.get("skills", [])}

    updated_entries: List[Dict[str, Any]] = []
    for skill_file in discover_skill_files(root):
        skill_id = skill_file.parent.name
        parsed = parse_skill_file(skill_file)
        existing = existing_entries.get(skill_id, {})
        updated_entries.append(build_skill_entry(skill_id, parsed, existing))

    manifest["skills"] = updated_entries
    return manifest


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Sync MANIFEST.json with discovered skills.")
    parser.add_argument("--root", default=str(repo_root), help="Repository root path")
    parser.add_argument("--manifest", default=str(repo_root / "MANIFEST.json"), help="Manifest file path")
    parser.add_argument("--check", action="store_true", help="Check-only mode (no file write)")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()

    current_text = manifest_path.read_text(encoding="utf-8")
    updated_manifest = sync_manifest(manifest_path, root)
    updated_text = json.dumps(updated_manifest, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if current_text == updated_text:
            print("MANIFEST.json is already in sync.")
            return 0
        print("MANIFEST.json is out of sync.")
        return 1

    manifest_path.write_text(updated_text, encoding="utf-8")
    print(f"Synced {len(updated_manifest.get('skills', []))} skills in {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
