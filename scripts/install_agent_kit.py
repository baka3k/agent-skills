#!/usr/bin/env python3
"""Install agent skills to supported AI platforms."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from convert_skill import (
    convert_to_continue,
    convert_to_cursor,
    convert_to_openai,
)
from skill_parser import parse_skill_file


class AgentSkillsInstaller:
    """Installer for multi-platform AI skill kit."""

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

    def __init__(self, kit_root: Path, agent: str, scope: str = "local", project_root: Path | None = None):
        self.kit_root = kit_root
        self.agent = agent
        self.scope = scope
        self.project_root = project_root or Path.cwd()
        self.agent_config = self.AGENT_CONFIGS.get(agent)

        if not self.agent_config:
            raise ValueError(f"Unknown agent: {agent}")

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
        if src.exists() and src.is_dir():
            shutil.copytree(src, dst_root / name, dirs_exist_ok=True)
            return True
        return False

    def _copy_shared_scripts(self, dst_root: Path) -> bool:
        """Copy kit-level shared scripts into a skill when it has no local scripts."""
        shared_scripts = self.kit_root / "scripts"
        if not shared_scripts.exists() or not shared_scripts.is_dir():
            return False
        shutil.copytree(shared_scripts, dst_root / "scripts", dirs_exist_ok=True)
        return True

    def _prune_pycache(self, root: Path) -> None:
        if not root.exists():
            return
        for cache_dir in root.rglob("__pycache__"):
            shutil.rmtree(cache_dir, ignore_errors=True)

    def _install_claude(self, install_path: Path, skills: List[Dict]) -> int:
        install_path.mkdir(parents=True, exist_ok=True)

        for skill in skills:
            dst_root = install_path / skill["name"]
            dst_root.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill["path"], dst_root / "SKILL.md")
            self._copy_optional_dir(skill["dir"], dst_root, "references")
            skill_scripts_copied = self._copy_optional_dir(skill["dir"], dst_root, "scripts")
            if not skill_scripts_copied:
                self._copy_shared_scripts(dst_root)
            self._copy_optional_dir(skill["dir"], dst_root, "assets")
            self._prune_pycache(dst_root / "scripts")

        return len(skills)

    def _install_continue(self, install_path: Path, skills: List[Dict]) -> int:
        install_path.mkdir(parents=True, exist_ok=True)
        written = 0

        for skill in skills:
            content = convert_to_continue(skill)
            output_file = install_path / f"{skill['name']}.json"
            output_file.write_text(
                json.dumps(content, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            written += 1

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
        return len(skills)

    def install(self, dry_run: bool = False) -> bool:
        print(f"\n{'='*60}")
        print("Installing Agent Skills Kit")
        print(f"{'='*60}")
        print(f"Agent: {self.agent_config['name']}")
        print(f"Scope: {self.scope}")
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

        print(f"\n✓ Successfully installed {installed_count} skills")
        print(f"✓ Installation path: {install_path}")

        self._print_post_install_instructions()
        return True

    def _print_post_install_instructions(self) -> None:
        print(f"\n{'='*60}")
        print("Post-Installation Instructions")
        print(f"{'='*60}")

        if self.agent == "claude-code":
            print(
                """
To use the skills in Claude Code:
  1. Restart Claude Code CLI
  2. Use: /skill <skill-name>
  3. Example: /skill deep-codebase-discovery
"""
            )
        elif self.agent == "cursor":
            print(
                """
To use the skills in Cursor AI:
  1. Restart Cursor editor
  2. Skills are now active in .cursorrules
  3. Ask Cursor normally and mention the analysis intent
"""
            )
        elif self.agent == "continue":
            print(
                """
To use the skills in Continue.dev:
  1. Restart Continue extension
  2. Use Ctrl+Shift+A (Cmd+Shift+A on Mac)
  3. Select a generated skill from the menu
"""
            )
        elif self.agent == "copilot":
            print(
                """
To use the skills in GitHub Copilot:
  1. Open your repository
  2. Ensure skills are under .github/skills/
  3. Pick the relevant skill folder for the task context
"""
            )
        elif self.agent == "codex":
            print(
                """
To use the skills in OpenAI CodeX:
  1. Open .openai/codex-instructions.md
  2. Copy the relevant workflow into your Codex/ChatGPT session
  3. Provide repository context and run the analysis
"""
            )



def interactive_mode(kit_root: Path) -> int:
    print(f"\n{'='*60}")
    print("Agent Skills Kit - Interactive Installer")
    print(f"{'='*60}\n")

    agents = list(AgentSkillsInstaller.AGENT_CONFIGS.keys())
    print("Select AI Agent:")
    for i, agent_key in enumerate(agents, 1):
        config = AgentSkillsInstaller.AGENT_CONFIGS[agent_key]
        print(f"  {i}. {config['name']} - {config['description']}")

    selected_agent = ""
    while not selected_agent:
        try:
            choice = int(input(f"\nSelect agent (1-{len(agents)}): ").strip())
            if 1 <= choice <= len(agents):
                selected_agent = agents[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid choice. Please try again.")

    config = AgentSkillsInstaller.AGENT_CONFIGS[selected_agent]
    global_path = config["install_paths"].get("global")
    local_path = config["install_paths"].get("local")

    if global_path and local_path:
        response = input("\nInstall globally or locally? [G/l]: ").strip().lower()
        scope = "global" if response.startswith("g") else "local"
    elif global_path:
        scope = "global"
    else:
        scope = "local"

    installer = AgentSkillsInstaller(kit_root=kit_root, agent=selected_agent, scope=scope)
    return 0 if installer.install() else 1



def list_agents() -> None:
    print("\nSupported AI Agents:")
    print(f"{'='*60}\n")

    for agent_key, config in AgentSkillsInstaller.AGENT_CONFIGS.items():
        print(f"**{config['name']}** ({agent_key})")
        print(f"  Description: {config['description']}")
        print(f"  Global path: {config['install_paths'].get('global', 'N/A')}")
        print(f"  Local path: {config['install_paths'].get('local', 'N/A')}")
        print()



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install agent skills to AI platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python scripts/install_agent_kit.py --interactive

  # Install for Claude Code
  python scripts/install_agent_kit.py --agent claude-code --scope global

  # Install for Cursor globally
  python scripts/install_agent_kit.py --agent cursor --scope global

  # Install for Continue.dev globally
  python scripts/install_agent_kit.py --agent continue --scope global

  # Install for OpenAI CodeX locally
  python scripts/install_agent_kit.py --agent codex --scope local

  # List supported agents
  python scripts/install_agent_kit.py --list

  # Dry run
  python scripts/install_agent_kit.py --agent cursor --dry-run
""",
    )

    parser.add_argument("--agent", choices=list(AgentSkillsInstaller.AGENT_CONFIGS.keys()), help="Target AI agent")
    parser.add_argument("--scope", choices=["global", "local"], default="local", help="Installation scope")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root (for local installation)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive installation mode")
    parser.add_argument("--list", "-l", action="store_true", help="List supported agents")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be installed")

    args = parser.parse_args()
    kit_root = Path(__file__).resolve().parent.parent

    if args.list:
        list_agents()
        return 0

    if args.interactive:
        return interactive_mode(kit_root)

    try:
        selected_agent = args.agent
        selected_scope = args.scope

        if not selected_agent:
            selected_agent = "agents"
            selected_scope = "global"
            print("Info: No --agent provided. Using default target: ~/.agents/skills")

        config = AgentSkillsInstaller.AGENT_CONFIGS[selected_agent]
        if config["install_paths"].get(selected_scope) is None:
            fallback_scope = "global" if selected_scope == "local" else "local"
            if config["install_paths"].get(fallback_scope) is not None:
                print(
                    f"Info: {config['name']} does not support {selected_scope} scope. "
                    f"Using {fallback_scope}."
                )
                selected_scope = fallback_scope

        installer = AgentSkillsInstaller(
            kit_root=kit_root,
            agent=selected_agent,
            scope=selected_scope,
            project_root=args.project_root,
        )
        success = installer.install(dry_run=args.dry_run)
        return 0 if success else 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
