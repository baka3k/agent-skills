#!/usr/bin/env python3
"""Bootstrap wiki directory structure and copy page templates."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = SKILL_ROOT / "templates"

PAGE_TEMPLATES = [
    ("index.md", "wiki/index.md"),
    ("architecture-overview.md", "wiki/architecture-overview.md"),
    ("setup-guide.md", "wiki/setup-guide.md"),
]

DIRS = [
    "wiki/modules",
    "wiki/api",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap wiki/ directory for wiki-generator skill."
    )
    parser.add_argument(
        "--output-root",
        required=True,
        help="Directory where wiki/ will be created.",
    )
    parser.add_argument(
        "--project-name",
        default="Project",
        help="Project name injected into page placeholders.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing wiki pages.",
    )
    return parser.parse_args()


def replace_placeholders(text: str, project_name: str) -> str:
    return text.replace("{ProjectName}", project_name).replace(
        "{YYYY-MM-DD}", datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    )


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root).expanduser().resolve()

    if not output_root.exists():
        print(f"Error: Output root does not exist: {output_root}", flush=True)
        return 2

    for d in DIRS:
        (output_root / d).mkdir(parents=True, exist_ok=True)

    created = []
    for src_name, dst_rel in PAGE_TEMPLATES:
        src = TEMPLATE_DIR / src_name
        if not src.exists():
            print(f"Warning: Template missing: {src}", flush=True)
            continue
        dst = output_root / dst_rel
        if dst.exists() and not args.overwrite:
            continue
        content = src.read_text(encoding="utf-8")
        rendered = replace_placeholders(content, args.project_name)
        dst.write_text(rendered, encoding="utf-8")
        created.append(dst_rel)

    manifest = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "output_root": str(output_root),
        "project_name": args.project_name,
        "skill": "wiki-generator",
        "files_created": created,
    }
    manifest_path = output_root / "wiki" / "wiki_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Wiki bootstrapped at: {output_root / 'wiki'}")
    print(f"  Created: {len(created)} page templates")
    print(f"  Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
