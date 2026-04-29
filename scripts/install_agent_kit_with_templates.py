#!/usr/bin/env python3
"""Install agent skills to supported AI platforms with template support."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

try:
    from convert_skill import (
        convert_to_continue,
        convert_to_cursor,
        convert_to_openai,
    )
    from skill_parser import parse_skill_file
except ImportError:
    print("Error: Required modules not found. Run from scripts/ directory or ensure PYTHONPATH is set.")
    sys.exit(1)


class EnhancedAgentSkillsInstaller:
    """Enhanced installer for multi-platform AI skill kit with template support."""

    AGENT_CONFIGS: Dict[str, Dict[str, object]] = {
        "claude-code": {
            "name": "Claude Code",
            "description": "Claude Code CLI skills (/skill command)",
            "install_paths": {"global": "~/.claude/skills", "local": None},
            "target_type": "directory",
            "mode": "claude",
        },
        "cursor": {
            "name": "Cursor AI",
            "description": "Cursor AI (.cursorrules)",
            "install_paths": {"global": "~/.cursorrules", "local": ".cursorrules"},
            "target_type": "file",
            "mode": "cursor",
        },
        "continue": {
            "name": "Continue.dev",
            "description": "Continue.dev custom skills",
            "install_paths": {"global": "~/.continue/skills", "local": None},
            "target_type": "directory",
            "mode": "continue",
        },
        "copilot": {
            "name": "GitHub Copilot",
            "description": "GitHub Copilot multi-skill directory (.github/skills)",
            "install_paths": {"global": None, "local": ".github/skills"},
            "target_type": "directory",
            "mode": "copilot-skills",
        },
        "codex": {
            "name": "OpenAI CodeX",
            "description": "OpenAI CodeX / ChatGPT instructions",
            "install_paths": {"global": None, "local": ".openai/codex-instructions.md"},
            "target_type": "file",
            "mode": "codex",
        },
        "agents": {
            "name": "Generic Agents Runtime",
            "description": "Default runtime skills directory (~/.agents/skills)",
            "install_paths": {"global": "~/.agents/skills", "local": "~/.agents/skills"},
            "target_type": "directory",
            "mode": "claude",
        },
    }

    def __init__(
        self,
        kit_root: Path,
        agent: str,
        scope: str = "local",
        project_root: Path | None = None,
        include_templates: bool = True,
        template_source: Path | None = None,
    ):
        self.kit_root = kit_root
        self.agent = agent
        self.scope = scope
        self.project_root = project_root or Path.cwd()
        self.include_templates = include_templates
        self.template_source = template_source or kit_root / "template"
        self.agent_config = self.AGENT_CONFIGS.get(agent)

        if not self.agent_config:
            raise ValueError(f"Unknown agent: {agent}")
        if not self.kit_root.exists():
            raise ValueError(f"Kit root does not exist: {self.kit_root}")

    def get_install_path(self) -> Path:
        paths = self.agent_config["install_paths"]
        install_path_str = paths.get(self.scope)

        if install_path_str is None:
            raise ValueError(f"{self.agent_config['name']} doesn't support {self.scope} installation")

        install_path = Path(str(install_path_str)).expanduser()
        if self.scope == "local" and not install_path.is_absolute():
            install_path = self.project_root / install_path
        return install_path

    def discover_skill_files(self) -> List[Path]:
        skills: List[Path] = []
        for item in sorted(self.kit_root.iterdir()):
            skill_file = item / "SKILL.md"
            if item.is_dir() and skill_file.exists():
                skills.append(skill_file)
        return skills

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")

    def _backup_file_if_exists(self, path: Path) -> Path | None:
        if not path.exists() or not path.is_file():
            return None
        backup_path = path.with_name(f"{path.name}.backup.{self._timestamp()}")
        shutil.copy2(path, backup_path)
        return backup_path

    def _copy_optional_dir(self, src_root: Path, dst_root: Path, name: str) -> bool:
        src = src_root / name
        if not src.exists() or not src.is_dir():
            return False
        shutil.copytree(src, dst_root / name, dirs_exist_ok=True)
        return True

    def _copy_shared_scripts(self, dst_root: Path) -> bool:
        shared_scripts = self.kit_root / "scripts"
        if not shared_scripts.exists() or not shared_scripts.is_dir():
            return False
        shutil.copytree(shared_scripts, dst_root / "scripts", dirs_exist_ok=True)
        return True

    def _copy_templates(self, dst_root: Path) -> bool:
        if not self.include_templates:
            return False
        if not self.template_source.exists() or not self.template_source.is_dir():
            print(f"  Warning: template directory not found: {self.template_source}")
            return False
        template_dst = dst_root / "template"
        shutil.copytree(self.template_source, template_dst, dirs_exist_ok=True)
        template_count = len(list(template_dst.rglob("*.md")))
        print(f"  Copied {template_count} template files to {template_dst}")
        return True

    def _prune_pycache(self, root: Path) -> None:
        if not root.exists():
            return
        for cache_dir in root.rglob("__pycache__"):
            shutil.rmtree(cache_dir, ignore_errors=True)

    def _install_claude(self, install_path: Path, skills: List[Dict]) -> int:
        install_path.mkdir(parents=True, exist_ok=True)

        for index, skill in enumerate(skills):
            dst_root = install_path / skill["name"]
            dst_root.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill["path"], dst_root / "SKILL.md")
            self._copy_optional_dir(skill["dir"], dst_root, "references")
            scripts_copied = self._copy_optional_dir(skill["dir"], dst_root, "scripts")
            if not scripts_copied:
                self._copy_shared_scripts(dst_root)
            self._copy_optional_dir(skill["dir"], dst_root, "assets")
            self._prune_pycache(dst_root / "scripts")

            if index == 0:
                self._copy_templates(install_path)

        return len(skills)

    def _install_continue(self, install_path: Path, skills: List[Dict]) -> int:
        install_path.mkdir(parents=True, exist_ok=True)
        written = 0
        for skill in skills:
            content = convert_to_continue(skill)
            output_file = install_path / f"{skill['name']}.json"
            output_file.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            written += 1
        if self.include_templates:
            self._copy_templates(install_path)
        return written

    def _build_bundle_content(self, mode: str, skills: List[Dict]) -> str:
        generated = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        if mode == "cursor":
            header = [
                "# Agent Skills Kit - Cursor Rules",
                "# Generated by: Agent Skills Kit Installer",
                f"# Date: {generated}",
                "",
            ]
            sections = [convert_to_cursor(skill).strip() for skill in skills]
            return "\n\n".join(header + sections).rstrip() + "\n"

        if mode == "codex":
            header = [
                "# Agent Skills Kit - OpenAI CodeX Instructions",
                "",
                f"Generated: {generated}",
                "",
                "## Available Skills",
                "",
            ]
            sections = [convert_to_openai(skill).strip() for skill in skills]
            return "\n\n".join(header + sections).rstrip() + "\n"

        raise ValueError(f"Unsupported bundle mode: {mode}")

    def _install_bundle_file(self, install_path: Path, mode: str, skills: List[Dict]) -> int:
        install_path.parent.mkdir(parents=True, exist_ok=True)
        backup = self._backup_file_if_exists(install_path)
        if backup:
            print(f"Backup created: {backup}")

        content = self._build_bundle_content(mode, skills)
        install_path.write_text(content, encoding="utf-8")

        if self.include_templates:
            self._copy_templates(self.project_root)

        return len(skills)

    def install(self, dry_run: bool = False) -> bool:
        print(f"\n{'='*60}")
        print("Installing Agent Skills Kit (Enhanced)")
        print(f"{'='*60}")
        print(f"Agent: {self.agent_config['name']}")
        print(f"Scope: {self.scope}")
        print(f"Project root: {self.project_root}")
        print(f"Include templates: {self.include_templates}")
        print(f"{'='*60}\n")

        install_path = self.get_install_path()
        print(f"Install path: {install_path}")

        skills = [parse_skill_file(path) for path in self.discover_skill_files()]
        print(f"\nFound {len(skills)} skills to install:")
        for skill in skills:
            desc = str(skill["description"]).strip()
            truncated = (desc[:64] + "...") if len(desc) > 67 else desc
            print(f"  - {skill['name']}: {truncated}")

        if dry_run:
            print("\n[DRY RUN] Would install to:")
            print(f"  {install_path}")
            if self.include_templates:
                print(f"  Templates from: {self.template_source}")
            return True

        response = input("\nProceed with installation? [y/N]: ").strip().lower()
        if response != "y":
            print("Installation cancelled.")
            return False

        mode = str(self.agent_config["mode"])
        target_type = str(self.agent_config["target_type"])

        if target_type == "directory" and mode in {"claude", "copilot-skills"}:
            installed_count = self._install_claude(install_path, skills)
        elif target_type == "directory" and mode == "continue":
            installed_count = self._install_continue(install_path, skills)
        elif target_type == "file":
            installed_count = self._install_bundle_file(install_path, mode, skills)
        else:
            raise ValueError(f"Unsupported installer mode: {mode}")

        print(f"\nSuccessfully installed {installed_count} skills")
        print(f"Installation path: {install_path}")

        self._print_post_install_instructions()
        return True

    def _print_post_install_instructions(self) -> None:
        print(f"\n{'='*60}")
        print("Post-Installation Instructions")
        print(f"{'='*60}")

        if self.agent == "copilot":
            print(
                """
For GitHub Copilot, skills are installed under .github/skills in your selected folder.
Example: current-folder install -> <current>/.github/skills
"""
            )


def _pick_from_menu(prompt: str, option_count: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Invalid choice. Please enter a number.")
            continue
        if 1 <= value <= option_count:
            return value
        print("Invalid choice. Please try again.")


def _resolve_scope_and_root(
    selected_agent: str,
    requested_scope: str,
    requested_project_root: Path,
) -> tuple[str, Path]:
    config = EnhancedAgentSkillsInstaller.AGENT_CONFIGS[selected_agent]
    paths = config["install_paths"]
    scope = requested_scope

    if paths.get(scope) is None:
        fallback_scope = "global" if scope == "local" else "local"
        if paths.get(fallback_scope) is not None:
            print(
                f"Info: {config['name']} does not support {scope} scope. "
                f"Using {fallback_scope}."
            )
            scope = fallback_scope
        else:
            raise ValueError(f"{config['name']} has no valid install scope")

    return scope, requested_project_root.resolve()


def interactive_mode(kit_root: Path) -> int:
    print(f"\n{'='*60}")
    print("Agent Skills Kit - Interactive Installer (Enhanced)")
    print(f"{'='*60}\n")


    agents = list(EnhancedAgentSkillsInstaller.AGENT_CONFIGS.keys())
    print("Step 1/3 - Select AI Agent:")
    for i, agent_key in enumerate(agents, 1):
        config = EnhancedAgentSkillsInstaller.AGENT_CONFIGS[agent_key]
        print(f"  {i}. {config['name']} - {config['description']}")

    agent_choice = _pick_from_menu(f"\nSelect agent (1-{len(agents)}): ", len(agents))
    selected_agent = agents[agent_choice - 1]
    config = EnhancedAgentSkillsInstaller.AGENT_CONFIGS[selected_agent]

    print("\nStep 2/3 - Select installation location:")
    global_path = config["install_paths"].get("global")
    local_path = config["install_paths"].get("local")

    labels: List[str] = []
    actions: List[tuple[str, Path]] = []

    if global_path is not None:
        labels.append(f"Global ({global_path})")
        actions.append(("global", Path.cwd()))
    if local_path is not None:
        labels.append(f"Current folder ({Path.cwd()})")
        actions.append(("local", Path.cwd()))
        labels.append("Custom folder")
        actions.append(("local", Path.cwd()))

    for i, label in enumerate(labels, 1):
        print(f"  {i}. {label}")

    location_choice = _pick_from_menu(f"\nSelect location (1-{len(labels)}): ", len(labels))
    chosen_scope, chosen_root = actions[location_choice - 1]
    if labels[location_choice - 1] == "Custom folder":
        custom_root = input("Enter custom folder path: ").strip()
        if not custom_root:
            print("Error: Custom folder path is required.")
            return 1
        chosen_root = Path(custom_root).expanduser().resolve()

    selected_scope, selected_project_root = _resolve_scope_and_root(
        selected_agent=selected_agent,
        requested_scope=chosen_scope,
        requested_project_root=chosen_root,
    )

    include_templates = True
    template_source = None

    installer = EnhancedAgentSkillsInstaller(
        kit_root=kit_root,
        agent=selected_agent,
        scope=selected_scope,
        project_root=selected_project_root,
        include_templates=include_templates,
        template_source=template_source,
    )

    print("\nStep 3/3 - Confirm")
    print(f"  Agent: {config['name']} ({selected_agent})")
    print(f"  Scope: {selected_scope}")
    print(f"  Project root: {selected_project_root}")
    print(f"  Install path: {installer.get_install_path()}")
    print(f"  Include templates: {include_templates}")

    return 0 if installer.install() else 1


def list_agents() -> None:
    print("\nSupported AI Agents:")
    print(f"{'='*60}\n")
    for agent_key, config in EnhancedAgentSkillsInstaller.AGENT_CONFIGS.items():
        print(f"**{config['name']}** ({agent_key})")
        print(f"  Description: {config['description']}")
        print(f"  Global path: {config['install_paths'].get('global', 'N/A')}")
        print(f"  Local path: {config['install_paths'].get('local', 'N/A')}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install agent skills to AI platforms (Enhanced with template support)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python scripts/install_agent_kit_with_templates.py --interactive

  # Install into current folder
  python scripts/install_agent_kit_with_templates.py . --agent copilot

  # Install from custom kit root
  python scripts/install_agent_kit_with_templates.py --kit-root /path/to/agent-skill --agent claude-code --scope global

  # Dry run
  python scripts/install_agent_kit_with_templates.py --agent cursor --dry-run
""",
    )

    parser.add_argument("install_target", nargs="?", help="Use '.' to install to current folder or provide a custom folder path")
    parser.add_argument("--agent", choices=list(EnhancedAgentSkillsInstaller.AGENT_CONFIGS.keys()), help="Target AI agent")
    parser.add_argument("--scope", choices=["global", "local"], default="local", help="Installation scope")
    parser.add_argument("--kit-root", type=Path, help="Custom kit root path (default: parent of scripts/)")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root (for local installation)")
    parser.add_argument("--template-source", type=Path, help="Custom template directory path")
    parser.add_argument("--include-templates", action="store_true", default=True, dest="include_templates", help="Include template directory (default: True)")
    parser.add_argument("--no-templates", action="store_false", dest="include_templates", help="Exclude template directory")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive installation mode")
    parser.add_argument("--list", "-l", action="store_true", help="List supported agents")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed")

    args = parser.parse_args()

    kit_root = args.kit_root.resolve() if args.kit_root else Path(__file__).resolve().parent.parent

    if args.list:
        list_agents()
        return 0

    if args.interactive:
        return interactive_mode(kit_root)

    try:
        selected_agent = args.agent
        selected_scope = args.scope
        selected_project_root = args.project_root

        if args.install_target:
            if args.install_target == ".":
                selected_scope = "local"
                selected_project_root = Path.cwd()
            else:
                selected_scope = "local"
                selected_project_root = Path(args.install_target).expanduser().resolve()

        if not selected_agent:
            return interactive_mode(kit_root)

        selected_scope, selected_project_root = _resolve_scope_and_root(
            selected_agent=selected_agent,
            requested_scope=selected_scope,
            requested_project_root=selected_project_root,
        )

        installer = EnhancedAgentSkillsInstaller(
            kit_root=kit_root,
            agent=selected_agent,
            scope=selected_scope,
            project_root=selected_project_root,
            include_templates=args.include_templates,
            template_source=args.template_source,
        )
        return 0 if installer.install(dry_run=args.dry_run) else 1
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
