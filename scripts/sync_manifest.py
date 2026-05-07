#!/usr/bin/env python3
"""Sync MANIFEST.json skill entries from discovered SKILL.md directories."""

from __future__ import annotations

import argparse
import json
import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from skill_parser import parse_skill_file

DEFAULT_PLATFORMS = ["claude-code", "cursor", "continue", "copilot", "codex"]

# Hooks validation
HOOKS_REGISTRY_PATH = Path(__file__).parent.parent / "template/hooks/registry.yaml"
MANDATORY_HOOKS = ["input-validation"]  # All skills must have this
MCP_HOOKS = ["mcp-health-check"]  # MCP-dependent skills must have this

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
    "cpp-java-pre-porting": "porting",
    "cpp-java-migration-planner": "porting",
    "cpp-java-file-structure-porting": "porting",
    "cpp-java-function-porting": "porting",
    "cpp-java-porting-orchestrator": "orchestration",
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
    "cpp-java-porting-orchestrator": [
        "cpp-java-migration-planner",
        "cpp-java-pre-porting",
        "cpp-java-file-structure-porting",
        "cpp-java-function-porting",
        "legacy-cpp-porting-guardrails",
    ],
}


def load_hooks_registry() -> Dict[str, Any]:
    """Load hooks registry for validation."""
    if HOOKS_REGISTRY_PATH.exists():
        return yaml.safe_load(HOOKS_REGISTRY_PATH.read_text(encoding="utf-8"))
    return {}

def parse_hooks_from_frontmatter(frontmatter: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Parse hooks section from YAML frontmatter."""
    hooks_str = frontmatter.get("hooks")
    if not hooks_str:
        return None

    try:
        # Try to parse as YAML
        if isinstance(hooks_str, str):
            return yaml.safe_load(hooks_str)
        return hooks_str
    except yaml.YAMLError:
        return None

def validate_hooks(hooks: Dict[str, Any], skill_id: str, registry: Dict[str, Any]) -> List[str]:
    """Validate hooks against registry and mandatory requirements."""
    errors = []

    if not hooks:
        errors.append(f"{skill_id}: Missing hooks declaration (mandatory)")
        return errors

    # Check for mandatory hooks
    hook_names = []
    for phase, phase_hooks in hooks.items():
        if isinstance(phase_hooks, list):
            for hook in phase_hooks:
                if isinstance(hook, str):
                    hook_names.append(hook)
                elif isinstance(hook, dict):
                    hook_names.append(hook.get("name", ""))

    # Check mandatory hooks
    for mandatory_hook in MANDATORY_HOOKS:
        if mandatory_hook not in hook_names:
            errors.append(f"{skill_id}: Missing mandatory hook '{mandatory_hook}'")

    # Validate against registry
    registered_hooks = registry.get("hooks", [])
    registered_names = {h["name"] for h in registered_hooks}

    for hook_name in hook_names:
        if hook_name and hook_name not in registered_names and not hook_name.startswith("skill-"):
            errors.append(f"{skill_id}: Unknown hook '{hook_name}' not in registry")

    return errors

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


def build_skill_entry(skill_id: str, skill_data: Dict[str, Any], existing: Dict[str, Any], registry: Dict[str, Any]) -> Dict[str, Any]:
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
    if skill_id in DEPENDENCY_OVERRIDES:
        entry["dependencies"] = DEPENDENCY_OVERRIDES[skill_id]
    else:
        entry["dependencies"] = existing.get("dependencies", [])
    entry["platforms"] = platforms

    # Parse and validate hooks
    hooks = parse_hooks_from_frontmatter(skill_data.get("frontmatter", {}))
    if hooks:
        entry["hooks"] = hooks
        # Validate hooks
        validation_errors = validate_hooks(hooks, skill_id, registry)
        if validation_errors:
            entry["hooks_warnings"] = validation_errors

    return entry


def sync_manifest(manifest_path: Path, root: Path) -> Dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_entries = {entry.get("id"): entry for entry in manifest.get("skills", [])}

    # Load hooks registry
    registry = load_hooks_registry()

    updated_entries: List[Dict[str, Any]] = []
    all_validation_errors = []

    for skill_file in discover_skill_files(root):
        skill_id = skill_file.parent.name
        parsed = parse_skill_file(skill_file)
        existing = existing_entries.get(skill_id, {})
        entry = build_skill_entry(skill_id, parsed, existing, registry)
        updated_entries.append(entry)

        # Collect validation errors
        if "hooks_warnings" in entry:
            all_validation_errors.extend(entry["hooks_warnings"])

    manifest["skills"] = updated_entries

    # Add hooks metadata to manifest
    manifest["hooks_metadata"] = {
        "registry_version": registry.get("version", "unknown"),
        "mandatory_hooks": MANDATORY_HOOKS,
        "mcp_hooks": MCP_HOOKS,
        "validation_errors": all_validation_errors if all_validation_errors else None,
    }

    return manifest


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Sync MANIFEST.json with discovered skills.")
    parser.add_argument("--root", default=str(repo_root), help="Repository root path")
    parser.add_argument("--manifest", default=str(repo_root / "MANIFEST.json"), help="Manifest file path")
    parser.add_argument("--check", action="store_true", help="Check-only mode (no file write)")
    parser.add_argument("--validate-hooks", action="store_true", help="Validate hooks and exit with error code if issues found")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()

    current_text = manifest_path.read_text(encoding="utf-8")
    updated_manifest = sync_manifest(manifest_path, root)
    updated_text = json.dumps(updated_manifest, indent=2, ensure_ascii=False) + "\n"

    # Check for hook validation errors
    validation_errors = updated_manifest.get("hooks_metadata", {}).get("validation_errors", [])
    if validation_errors and args.validate_hooks:
        print("❌ Hooks validation failed:")
        for error in validation_errors:
            print(f"  - {error}")
        return 1

    if args.check:
        if current_text == updated_text:
            print("✅ MANIFEST.json is already in sync.")
            if validation_errors:
                print("⚠️  Hooks validation warnings:")
                for error in validation_errors:
                    print(f"  - {error}")
            return 0
        print("❌ MANIFEST.json is out of sync.")
        return 1

    manifest_path.write_text(updated_text, encoding="utf-8")

    # Print summary
    skill_count = len(updated_manifest.get('skills', []))
    hooks_metadata = updated_manifest.get('hooks_metadata', {})
    print(f"✅ Synced {skill_count} skills in {manifest_path}")

    if hooks_metadata.get("registry_version"):
        print(f"   Hooks registry version: {hooks_metadata['registry_version']}")

    if validation_errors:
        print(f"⚠️  Hooks validation warnings: {len(validation_errors)}")
        for error in validation_errors[:3]:  # Show first 3
            print(f"   - {error}")
        if len(validation_errors) > 3:
            print(f"   ... and {len(validation_errors) - 3} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
