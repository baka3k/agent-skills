#!/usr/bin/env python3
"""Shared helpers for parsing SKILL.md files and extracting workflow sections."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)



def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and ((value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")):
        return value[1:-1].strip()
    return value



def parse_frontmatter(content: str) -> Dict[str, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}

    frontmatter: Dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = _strip_quotes(value)
    return frontmatter



def strip_frontmatter(content: str) -> str:
    return FRONTMATTER_RE.sub("", content, count=1).strip()



def parse_skill_markdown(content: str, fallback_name: str) -> Dict[str, Any]:
    frontmatter = parse_frontmatter(content)
    markdown = strip_frontmatter(content)
    return {
        "name": frontmatter.get("name", fallback_name),
        "description": frontmatter.get("description", ""),
        "frontmatter": frontmatter,
        "markdown": markdown,
    }



def parse_skill_file(skill_path: Path) -> Dict[str, Any]:
    content = skill_path.read_text(encoding="utf-8")
    parsed = parse_skill_markdown(content, skill_path.parent.name)
    parsed["path"] = skill_path
    parsed["dir"] = skill_path.parent
    return parsed



def extract_markdown_section(markdown: str, headings: Iterable[str]) -> str:
    for heading in headings:
        pattern = re.compile(
            rf"(?ms)^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)",
        )
        match = pattern.search(markdown)
        if match:
            return match.group(1).strip()
    return ""



def extract_workflow_snippet(markdown: str) -> str:
    required_inputs = extract_markdown_section(markdown, ["Required Inputs"])
    workflow = extract_markdown_section(markdown, ["Workflow", "Orchestration Workflow"])

    sections = []
    if required_inputs:
        sections.append(f"**Required Inputs:**\n{required_inputs}")
    if workflow:
        sections.append(f"**Workflow:**\n{workflow}")

    if sections:
        return "\n\n".join(sections).strip()
    return markdown.strip()
