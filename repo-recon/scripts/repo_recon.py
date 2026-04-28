#!/usr/bin/env python3
"""Repository reconnaissance helper.

Generate a module inventory, language distribution, and entry-point hints.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    "coverage",
}

ALLOWED_DOT_DIRS = {".github", ".devcontainer", ".vscode"}

SOURCE_EXT_TO_LANG = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C/C++ Header",
    ".cs": ".NET",
    ".vb": "VB.NET",
    ".bas": "VB6/VB",
    ".cls": "VB6/VB",
    ".frm": "VB6/VB",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".scala": "Scala",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".lua": "Lua",
}

KEY_FILENAMES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "makefile",
    "cmakelists.txt",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "jenkinsfile",
}


@dataclass
class ModuleStats:
    file_count: int = 0
    source_file_count: int = 0
    languages: Counter = field(default_factory=Counter)
    key_files: List[str] = field(default_factory=list)


def should_skip_dir(dirname: str) -> bool:
    if dirname in IGNORED_DIRS:
        return True
    return dirname.startswith(".") and dirname not in ALLOWED_DOT_DIRS


def should_skip_file(filename: str) -> bool:
    if filename in {".ds_store"}:
        return True
    if filename.startswith(".") and filename not in {".gitignore", ".dockerignore"}:
        return True
    return False


def detect_entry_reason(path: Path) -> Optional[str]:
    p = path.as_posix().lower()
    name = path.name.lower()
    stem = path.stem.lower()

    if name in {
        "main.py",
        "main.go",
        "main.rs",
        "main.c",
        "main.cpp",
        "program.cs",
        "manage.py",
    }:
        return "conventional-main"
    if name in {"server.js", "server.ts", "app.py", "app.js", "app.ts"}:
        return "service-startup"
    if name == "__main__.py":
        return "python-module-entry"
    if "/cmd/" in p and name == "main.go":
        return "go-cmd-entry"
    if stem in {"start", "run"} and path.suffix.lower() in {".sh", ".ps1"}:
        return "script-entry"
    if name in {"docker-compose.yml", "docker-compose.yaml"}:
        return "container-orchestration-entry"
    return None


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        current_path = Path(current)
        for filename in files:
            if should_skip_file(filename):
                continue
            file_path = current_path / filename
            if file_path.is_symlink():
                continue
            yield file_path


def build_inventory(root: Path) -> Dict:
    modules: Dict[str, ModuleStats] = defaultdict(ModuleStats)
    language_counter: Counter = Counter()
    entry_points: List[Dict[str, str]] = []
    root_files: List[str] = []
    total_files = 0
    source_files = 0

    for file_path in iter_files(root):
        rel = file_path.relative_to(root)
        total_files += 1
        top = rel.parts[0] if len(rel.parts) > 1 else "."
        module = modules[top]
        module.file_count += 1

        if top == ".":
            root_files.append(rel.as_posix())

        ext = file_path.suffix.lower()
        language = SOURCE_EXT_TO_LANG.get(ext)
        if language:
            source_files += 1
            language_counter[language] += 1
            module.source_file_count += 1
            module.languages[language] += 1

        if file_path.name.lower() in KEY_FILENAMES and len(module.key_files) < 12:
            module.key_files.append(rel.as_posix())

        reason = detect_entry_reason(rel)
        if reason:
            entry_points.append({"path": rel.as_posix(), "reason": reason})

    module_candidates = []
    for name, stats in modules.items():
        dominant = [lang for lang, _ in stats.languages.most_common(3)]
        module_candidates.append(
            {
                "module": name,
                "file_count": stats.file_count,
                "source_file_count": stats.source_file_count,
                "dominant_languages": dominant,
                "key_files": stats.key_files,
            }
        )

    module_candidates.sort(
        key=lambda x: (x["source_file_count"], x["file_count"], x["module"]),
        reverse=True,
    )

    inventory = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "root": str(root.resolve()),
        "total_files": total_files,
        "source_files": source_files,
        "language_distribution": dict(language_counter.most_common()),
        "root_files": sorted(root_files),
        "module_candidates": module_candidates,
        "entry_points": sorted(entry_points, key=lambda x: x["path"]),
    }
    return inventory


def load_template(template_path: str) -> str:
    """Load template from file."""
    script_dir = Path(__file__).parent
    template_abs_path = script_dir.parent / "references" / template_path
    with open(template_abs_path, "r", encoding="utf-8") as f:
        return f.read()


def populate_template(template: str, data: Dict) -> str:
    """Populate module inventory template with discovered data.

    Maps scan results to template sections:
    - Context: Repository, scan date, scope
    - Top-Level Modules: Module candidates with purpose inferred from structure
    - Entry Points: Detected entry points with runtime classification
    - Integration Boundaries: Placeholder for manual analysis
    - Unknowns and Next Probes: Gaps in understanding
    """
    lines = template.split("\n")
    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Section 1: Context
        if line.strip().startswith("- Repository:"):
            output_lines.append(f"- Repository: `{data.get('root', 'N/A')}`")
        elif line.strip().startswith("- Commit/branch:"):
            output_lines.append(f"- Commit/branch: `{data.get('commit', 'N/A')}`")
        elif line.strip().startswith("- Scan date:"):
            output_lines.append(f"- Scan date: `{data.get('generated_at_utc', 'N/A')}`")
        elif line.strip().startswith("- Scope:"):
            output_lines.append(f"- Scope: `{data.get('scope', 'Full repository scan')}`")

        # Section 2: Top-Level Modules
        elif line.strip() == "| Module | Purpose | Key Files | Dominant Languages | Notes |":
            output_lines.append(line)
            # Add separator if next line is not separator
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|---|")
            # Add module data
            modules = data.get("module_candidates", [])
            if modules:
                for mod in modules:
                    name = mod.get("module", "")
                    # Infer purpose from module name and structure
                    purpose = _infer_module_purpose(mod)
                    key_files = mod.get("key_files", [])
                    if isinstance(key_files, list):
                        key_files = "<br>".join(key_files[:5])  # Limit to 5 key files
                    langs = mod.get("dominant_languages", [])
                    if isinstance(langs, list):
                        langs = ", ".join(langs)
                    notes = f"{mod.get('source_file_count', 0)} source files"
                    output_lines.append(f"| {name} | {purpose} | {key_files} | {langs} | {notes} |")
            else:
                output_lines.append("| | | | | |")
            # Skip template rows until next section
            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("|") or lines[i + 1].strip() == ""):
                i += 1

        # Section 3: Entry Points
        elif line.strip() == "| Runtime | File/Path | Trigger | Notes |":
            output_lines.append(line)
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|")
            entry_points = data.get("entry_points", [])
            if entry_points:
                for ep in entry_points:
                    path = ep.get("path", "")
                    reason = ep.get("reason", "")
                    runtime = _classify_runtime(path, reason)
                    trigger = _classify_trigger(reason)
                    output_lines.append(f"| {runtime} | `{path}` | {trigger} | |")
            else:
                output_lines.append("| | | | |")
            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("|") or lines[i + 1].strip() == ""):
                i += 1

        # Section 4: Integration Boundaries (placeholder for manual analysis)
        elif line.strip() == "| Module | Inbound Interfaces | Outbound Dependencies | Risk |":
            output_lines.append(line)
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|")
            # Add placeholder for each module
            modules = data.get("module_candidates", [])
            if modules:
                for mod in modules[:5]:  # Limit to top 5 modules
                    name = mod.get("module", "")
                    output_lines.append(f"| {name} | | | |")
            else:
                output_lines.append("| | | | |")
            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("|") or lines[i + 1].strip() == ""):
                i += 1

        # Section 5: Unknowns and Next Probes
        elif line.strip().startswith("- Unknown:"):
            unknowns = _generate_unknowns(data)
            if unknowns:
                for unknown in unknowns:
                    output_lines.append(f"- **Unknown**: {unknown['unknown']}")
                    output_lines.append(f"  - **Why uncertain**: {unknown['why_uncertain']}")
                    output_lines.append(f"  - **Suggested probe command/file**: {unknown['suggested_probe']}")
            else:
                output_lines.append("- Basic scan complete. No significant unknowns.")
            # Skip template placeholder lines
            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("-") or lines[i + 1].strip() == ""):
                i += 1

        else:
            output_lines.append(line)

        i += 1

    return "\n".join(output_lines)


def _infer_module_purpose(mod: Dict) -> str:
    """Infer module purpose from name and structure."""
    name = mod.get("module", "").lower()
    key_files = mod.get("key_files", [])

    # Check for common patterns
    if any("test" in f.lower() for f in key_files):
        return "Test suite"
    if name in ["src", "source"]:
        return "Main source code"
    if name in ["lib", "libs", "library"]:
        return "Library/shared code"
    if name in ["docs", "doc"]:
        return "Documentation"
    if name in ["build", "ci", "cd"]:
        return "Build/CI configuration"
    if name in ["config", "configs", "settings"]:
        return "Configuration"
    if name == ".":
        return "Root directory"
    if "package.json" in key_files or "pom.xml" in key_files:
        return "Package/module"
    if "go.mod" in key_files or "cargo.toml" in key_files:
        return "Go/Rust module"

    # Default: use dominant language
    langs = mod.get("dominant_languages", [])
    if langs:
        return f"{langs[0]} module"
    return "Unknown"


def _classify_runtime(path: str, reason: str) -> str:
    """Classify entry point runtime type."""
    path_lower = path.lower()
    reason_lower = reason.lower()

    if any(x in path_lower for x in ["api", "server", "app.js", "app.ts", "app.py"]):
        return "API"
    if "worker" in path_lower or "job" in path_lower:
        return "Worker"
    if "cli" in path_lower or path.endswith((".sh", ".ps1")):
        return "CLI"
    if "main" in path_lower or "conventional" in reason_lower:
        return "Application"
    if "service" in reason_lower or "startup" in reason_lower:
        return "Service"

    return "Unknown"


def _classify_trigger(reason: str) -> str:
    """Classify entry point trigger."""
    reason_lower = reason.lower()

    if "main" in reason_lower:
        return "Process start"
    if "service" in reason_lower or "startup" in reason_lower:
        return "Service start"
    if "script" in reason_lower:
        return "Script execution"
    if "container" in reason_lower:
        return "Container start"
    if "entry" in reason_lower:
        return "Module import"

    return reason


def _generate_unknowns(data: Dict) -> List[Dict]:
    """Generate unknowns based on gaps in scan data."""
    unknowns = []

    # Check for missing integration boundary analysis
    if data.get("module_candidates"):
        unknowns.append({
            "unknown": "Integration boundaries between modules",
            "why_uncertain": "Static scan cannot determine runtime dependencies and IPC",
            "suggested_probe": "Use graph_mcp query_subgraph to trace call graphs across module boundaries"
        })

    # Check for missing entry points
    if not data.get("entry_points"):
        unknowns.append({
            "unknown": "Application entry points",
            "why_uncertain": "No conventional entry point files found (main.py, server.js, etc.)",
            "suggested_probe": "Check for Dockerfile, docker-compose.yml, or package.json 'scripts' section"
        })

    # Check for build system
    root_files = data.get("root_files", [])
    has_build_config = any(f in root_files for f in ["makefile", "cmakelists.txt", "build.gradle", "pom.xml"])
    if not has_build_config:
        unknowns.append({
            "unknown": "Build and test system",
            "why_uncertain": "No standard build configuration found",
            "suggested_probe": "Look for .github/workflows/, .gitlab-ci.yml, or Jenkinsfile"
        })

    return unknowns


def to_markdown(data: Dict) -> str:
    """Generate markdown output using module inventory template."""
    template = load_template("module-inventory-template.md")
    return populate_template(template, data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan repository and produce module/entry-point inventory."
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository root path")
    parser.add_argument("--json", dest="json_out", help="Write JSON output to file")
    parser.add_argument("--md", dest="md_out", help="Write markdown output to file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Invalid repository path: {root}")

    data = build_inventory(root)
    md = to_markdown(data)

    if args.json_out:
        out = Path(args.json_out).expanduser()
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if args.md_out:
        out = Path(args.md_out).expanduser()
        out.write_text(md + "\n", encoding="utf-8")

    if not args.json_out and not args.md_out:
        print(json.dumps(data, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
