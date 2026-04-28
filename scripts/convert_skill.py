#!/usr/bin/env python3
"""Convert SKILL.md definitions to other AI platform formats."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from skill_parser import extract_workflow_snippet, parse_skill_file


def _extract_use_when(description: str) -> str:
    match = re.search(r"(use when .+)$", description.strip(), flags=re.IGNORECASE)
    if match:
        text = match.group(1).strip()
        return text[0].upper() + text[1:]
    summary = description.strip()
    if summary:
        if len(summary) > 160:
            summary = summary[:157].rstrip() + "..."
        return f"Use when you need: {summary}"
    return "Use this skill when the user request matches this domain."


def _extract_required_inputs(workflow: str, limit: int = 4) -> list[str]:
    match = re.search(
        r"(?ms)^\*\*Required Inputs:\*\*\s*(.*?)(?=^\*\*Workflow:\*\*|\Z)",
        workflow,
    )
    if not match:
        return []

    inputs: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            inputs.append(stripped[2:].strip())
        if len(inputs) >= limit:
            break
    return inputs


def _extract_step_titles(workflow: str, limit: int = 6) -> list[str]:
    titles = re.findall(r"(?m)^###\s+(.+)$", workflow)
    cleaned: list[str] = []
    for title in titles:
        item = title.strip()
        item = re.sub(r"^\d+\)\s*", "", item)
        if item:
            cleaned.append(item)
        if len(cleaned) >= limit:
            break
    return cleaned


def convert_to_copilot(skill_data: Dict[str, Any]) -> str:
    workflow = extract_workflow_snippet(skill_data["markdown"])
    skill_name = str(skill_data["name"])
    description = str(skill_data["description"])
    use_when = _extract_use_when(description)
    required_inputs = _extract_required_inputs(workflow)
    steps = _extract_step_titles(workflow)

    lines = [
        f"# {skill_name}",
        "",
        description,
        "",
        "## When To Use",
        use_when,
        "",
    ]

    if required_inputs:
        lines.append("## Required Inputs (Quick)")
        lines.extend(f"- {item}" for item in required_inputs)
        lines.append("")

    lines.append("## Quick Workflow")
    if steps:
        lines.extend(f"{i}. {step}" for i, step in enumerate(steps, start=1))
    else:
        lines.append("1. Follow the workflow in SKILL.md for this skill.")
    lines.append("")

    lines.extend(
        [
            "## Instructions",
            "Select this skill only when the request matches 'When To Use'.",
            "If the request spans multiple concerns, chain relevant skills in phases.",
            "Always provide evidence citations (file paths, symbol names).",
            "",
            "## Full Reference",
            f"- `{skill_name}/SKILL.md`",
            "",
        ]
    )

    return "\n".join(lines)


def convert_to_cursor(skill_data: Dict[str, Any]) -> str:
    workflow = extract_workflow_snippet(skill_data["markdown"])
    friendly_name = skill_data["name"].replace("-", " ")
    return f"""# {skill_data['name']}

{skill_data['description']}

When the user asks for {friendly_name}:

{workflow}

Always:
- Provide evidence citations (file paths, function names)
- Separate confirmed facts from assumptions
- Mark confidence levels (high/medium/low)
"""


def convert_to_continue(skill_data: Dict[str, Any]) -> Dict[str, Any]:
    workflow = extract_workflow_snippet(skill_data["markdown"])
    return {
        "name": skill_data["name"],
        "description": skill_data["description"],
        "content": (
            f"You are an expert in {skill_data['name'].replace('-', ' ')}.\n\n"
            f"{workflow}\n\n"
            "Always provide evidence-based results with clear citations."
        ),
    }


def convert_to_openai(skill_data: Dict[str, Any]) -> str:
    workflow = extract_workflow_snippet(skill_data["markdown"])
    return f"""System: You are an expert software architect and code analyst.

User Task: {skill_data['description']}

## Analysis Workflow

{workflow}

## Expected Output
Provide a comprehensive report with:
1. Summary of findings
2. Detailed analysis with evidence
3. Recommendations with priorities
4. Next steps with clear actions

Always cite your sources (file paths, function names, documentation).
"""


def _resolve_conversion(format_name: str) -> Tuple[Any, str]:
    mapping = {
        "copilot": (convert_to_copilot, ".md"),
        "cursor": (convert_to_cursor, ".cursorrules"),
        "continue": (convert_to_continue, ".json"),
        "openai": (convert_to_openai, ".md"),
        "codex": (convert_to_openai, ".md"),
        "claude": (lambda skill_data: skill_data["path"].read_text(encoding="utf-8"), ".md"),
    }
    return mapping[format_name]


def _collect_skill_files(root_dir: Path, skill_name: str | None, convert_all: bool) -> Iterable[Path]:
    if convert_all:
        return sorted(root_dir.glob("*/SKILL.md"))
    if not skill_name:
        raise ValueError("--skill is required unless --all is used")
    skill_file = root_dir / skill_name / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"Skill not found: {skill_file}")
    return [skill_file]


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Claude Code skills to other platforms")
    parser.add_argument("--skill", help="Skill name (e.g., deep-codebase-discovery)")
    parser.add_argument("--all", action="store_true", help="Convert all skills")
    parser.add_argument(
        "--format",
        required=True,
        choices=["copilot", "cursor", "continue", "openai", "codex", "claude"],
        help="Target platform format",
    )
    parser.add_argument("--output", help="Output directory (default: ./converted)")

    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    output_dir = Path(args.output) if args.output else (root_dir / "converted")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        skill_files = _collect_skill_files(root_dir, args.skill, args.all)
    except Exception as exc:
        print(exc)
        return 1

    converter, extension = _resolve_conversion(args.format)

    for skill_file in skill_files:
        skill_data = parse_skill_file(skill_file)
        print(f"Converting {skill_data['name']}...")

        converted = converter(skill_data)
        output_file = output_dir / f"{skill_data['name']}{extension}"

        if extension == ".json":
            output_file.write_text(
                json.dumps(converted, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        else:
            output_file.write_text(str(converted).rstrip() + "\n", encoding="utf-8")

        print(f"  -> {output_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
