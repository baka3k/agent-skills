#!/usr/bin/env python3
"""Bootstrap .harness/ directory structure and copy templates for a project."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_ROOT / "templates"

TEMPLATE_MAP = [
    ("agents.md", ".harness/AGENT.md"),
    ("feature-list.json", ".harness/state/feature_list.json"),
    ("feature-list.schema.json", ".harness/state/feature_list.schema.json"),
    ("progress.md", ".harness/state/progress.md"),
    ("init.sh", ".harness/scripts/init.sh"),
    ("config.yaml", ".harness/config.yaml"),
]

DIRS = [
    ".harness/state",
    ".harness/scripts",
    ".harness/templates",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap .harness/ directory for harness-builder skill."
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Root directory of the project to add harness to.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing harness files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()

    if not project_root.exists() or not project_root.is_dir():
        print(f"Error: Project root does not exist: {project_root}", flush=True)
        return 2

    for d in DIRS:
        (project_root / d).mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []
    for src_name, dst_rel in TEMPLATE_MAP:
        src = TEMPLATE_DIR / src_name
        if not src.exists():
            print(f"Warning: Template missing: {src}", flush=True)
            continue
        dst = project_root / dst_rel
        if dst.exists() and not args.overwrite:
            skipped.append(dst_rel)
            continue
        shutil.copy2(src, dst)
        if src_name == "init.sh":
            dst.chmod(0o755)
        created.append(dst_rel)

    manifest = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "project_root": str(project_root),
        "skill": "harness-builder",
        "files_created": created,
        "files_skipped": skipped,
    }
    manifest_path = project_root / ".harness" / "harness_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Harness bootstrapped at: {project_root / '.harness'}")
    print(f"  Created: {len(created)} files")
    if skipped:
        print(f"  Skipped (existing): {len(skipped)} files")
    print(f"  Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
