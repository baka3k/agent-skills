#!/usr/bin/env python3
"""
Bootstrap reverse-engineering documentation workspace from template files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE_ROOT = REPO_ROOT / "template"


TEMPLATE_MAP = [
    (
        "00_requirements/tpl_requirements_spec.md",
        "00_requirements/requirements_spec_{module}.md",
    ),
    (
        "00_requirements/tpl_feature_list.md",
        "00_requirements/feature_list_{module}.md",
    ),
    ("01_usecase/tpl_usecase_list.md", "01_usecase/usecase_list_{module}.md"),
    ("01_usecase/tpl_usecase_metrics.md", "01_usecase/usecase_metrics_{module}.md"),
    ("01_usecase/tpl_usecase_detail.md", "01_usecase/uc001_{module}_template.md"),
    (
        "02_detail_design/tpl_screen_design.md",
        "02_detail_design/screen_design_{module}.md",
    ),
    (
        "02_detail_design/tpl_api_process_design.md",
        "02_detail_design/api_process_design_{module}.md",
    ),
    (
        "02_detail_design/tpl_openapi_spec.yaml",
        "02_detail_design/openapi_spec_{module}.yaml",
    ),
    (
        "02_detail_design/tpl_table_design.md",
        "02_detail_design/table_design_{module}.md",
    ),
    ("02_detail_design/tpl_sql_design.md", "02_detail_design/sql_design_{module}.md"),
    (
        "02_detail_design/tpl_batch_process_design.md",
        "02_detail_design/batch_process_design_{module}.md",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create reverse documentation workspace from template set."
    )
    parser.add_argument(
        "--target-root",
        required=True,
        help="Repository root where .github/reverse_reconstruction will be created.",
    )
    parser.add_argument(
        "--module",
        required=True,
        help="Module or scope id (example: vtgm01).",
    )
    parser.add_argument(
        "--owner",
        default="TBD",
        help="Owner name injected into document placeholders.",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Metadata date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--template-root",
        default=str(DEFAULT_TEMPLATE_ROOT),
        help="Path to template root folder.",
    )
    parser.add_argument(
        "--trace-root",
        default="",
        help=(
            "Path to trace documentation root. "
            "Default resolves to <target-root>/.github/trace_documentation."
        ),
    )
    parser.add_argument(
        "--output-subdir",
        default=".github/reverse_reconstruction",
        help="Output subdirectory under target-root.",
    )
    parser.add_argument(
        "--skip-seed-trace",
        action="store_true",
        help="Do not copy seed trace templates.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files if present.",
    )
    return parser.parse_args()


def replace_common_placeholders(
    text: str, module: str, owner: str, date_str: str
) -> str:
    replacements = {
        "{Tên Module}": module,
        "{ModuleID}": module,
        "{YYYY-MM-DD}": date_str,
        "{Tên người tạo}": owner,
        "{Tên}": owner,
        "{Owner}": owner,
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
        text = text.replace(f"`{old}`", f"`{new}`")
    return text


def write_file(target: Path, content: str, overwrite: bool) -> None:
    if target.exists() and not overwrite:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def copy_templates(
    package_root: Path,
    template_root: Path,
    module: str,
    owner: str,
    date_str: str,
    overwrite: bool,
) -> list[Path]:
    created: list[Path] = []
    for src_rel, dst_rel in TEMPLATE_MAP:
        src = template_root / src_rel
        if not src.exists():
            raise FileNotFoundError(f"Missing template file: {src}")
        dst = package_root / dst_rel.format(module=module)

        raw = src.read_text(encoding="utf-8")
        rendered = replace_common_placeholders(raw, module, owner, date_str)
        existed = dst.exists()
        write_file(dst, rendered, overwrite=overwrite)
        if overwrite or not existed:
            created.append(dst)
    return created


def build_trace_plan(
    package_root: Path,
    module: str,
    owner: str,
    date_str: str,
    trace_root: Path,
    overwrite: bool,
) -> Path:
    plan_path = package_root / "03_trace_evidence" / f"trace_plan_{module}.md"
    if plan_path.exists() and not overwrite:
        return plan_path

    content = f"""# Trace Plan - {module}

## Metadata

- Module: `{module}`
- Owner: `{owner}`
- Date: `{date_str}`

## Source Strategy References

- `{trace_root / "usecase_discovery_guide.md"}`
- `{trace_root / "uscase_trace_strategy.md"}`
- `{trace_root / "sequence_generation_instruction.md"}`
- `{trace_root / "usecase_review_procedure.md"}`
- `{trace_root / "impact_assessment_strategy.md"}`

## Baseline Checklist

- [ ] Count module files in scope
- [ ] Count total functions
- [ ] Count entry points
- [ ] Count IPC links (send + receive)
- [ ] Capture baseline metrics snapshot

## Trace Checklist

- [ ] Build main flow from entry points
- [ ] Add ALT/ERROR branches
- [ ] Tag critical nodes with ROLE/FLOW/RISK/STATE
- [ ] Create sequence diagram for each primary UC
- [ ] Sync class diagram with sequence participants
- [ ] Update usecase metrics

## Quality Targets

- ENTRY_COVERAGE >= 90%
- FUNCTION_COVERAGE >= 60%
- ERROR_PATH_COVERAGE >= 70%
- IPC_COVERAGE >= 90%
"""
    write_file(plan_path, content, overwrite=overwrite)
    return plan_path


def copy_trace_templates(package_root: Path, trace_root: Path, overwrite: bool) -> list[Path]:
    files = [
        "usecase_template.md",
        "usecase_trace_metrics.md",
        "create_sequences.md",
    ]
    created: list[Path] = []
    dst_root = package_root / "03_trace_evidence" / "seed_templates"
    dst_root.mkdir(parents=True, exist_ok=True)
    for name in files:
        src = trace_root / name
        if not src.exists():
            continue
        dst = dst_root / name
        if dst.exists() and not overwrite:
            continue
        shutil.copyfile(src, dst)
        created.append(dst)
    return created


def main() -> int:
    args = parse_args()
    module = args.module.strip().lower()
    if not module:
        raise ValueError("module must not be empty")

    target_root = Path(args.target_root).expanduser().resolve()
    template_root = Path(args.template_root).expanduser().resolve()
    if args.trace_root:
        trace_root = Path(args.trace_root).expanduser().resolve()
    else:
        trace_root = (target_root / ".github" / "trace_documentation").resolve()

    output_subdir = Path(args.output_subdir)
    package_root = target_root / output_subdir / module
    package_root.mkdir(parents=True, exist_ok=True)

    created = copy_templates(
        package_root=package_root,
        template_root=template_root,
        module=module,
        owner=args.owner,
        date_str=args.date,
        overwrite=args.overwrite,
    )
    plan = build_trace_plan(
        package_root=package_root,
        module=module,
        owner=args.owner,
        date_str=args.date,
        trace_root=trace_root,
        overwrite=args.overwrite,
    )
    created_trace: list[Path] = []
    if not args.skip_seed_trace:
        created_trace = copy_trace_templates(
            package_root=package_root,
            trace_root=trace_root,
            overwrite=args.overwrite,
        )

    print(f"Package root: {package_root}")
    print(f"Created/updated templates: {len(created)}")
    print(f"Trace plan: {plan}")
    print(f"Seed trace templates copied: {len(created_trace)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
