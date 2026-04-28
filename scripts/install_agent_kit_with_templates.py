#!/usr/bin/env python3
"""Install agent skills to supported AI platforms with template support.

Enhanced version that:
- Copies template/ directory for skills that need it
- Allows installation from custom kit root (any directory)
- Supports project-specific skill installations
"""

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
        template_source: Path | None = None
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

        # Verify kit root exists
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
        """Discover all SKILL.md files in the kit root."""
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
        """Copy optional directory if it exists. Returns True if copied."""
        src = src_root / name
        if not src.exists() or not src.is_dir():
            return False

        dst = dst_root / name
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return True

    def _copy_shared_scripts(self, dst_root: Path) -> bool:
        """Copy kit-level shared scripts into a skill when it has no local scripts."""
        shared_scripts = self.kit_root / "scripts"
        if not shared_scripts.exists() or not shared_scripts.is_dir():
            return False
        shutil.copytree(shared_scripts, dst_root / "scripts", dirs_exist_ok=True)
        return True

    def _copy_templates(self, dst_root: Path) -> bool:
        """Copy template directory to installation. Returns True if copied."""
        if not self.include_templates:
            return False

        template_src = self.template_source
        if not template_src.exists() or not template_src.is_dir():
            print(f"  ⚠ Template directory not found: {template_src}")
            return False

        template_dst = dst_root / "template"
        shutil.copytree(template_src, template_dst, dirs_exist_ok=True)

        # Count templates
        template_count = len(list(template_dst.rglob("*.md")))
        print(f"  ✓ Copied {template_count} template files to template/")
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

            # Copy SKILL.md
            shutil.copy2(skill["path"], dst_root / "SKILL.md")

            # Copy optional directories
            self._copy_optional_dir(skill["dir"], dst_root, "references")
            scripts_copied = self._copy_optional_dir(skill["dir"], dst_root, "scripts")
            if not scripts_copied:
                self._copy_shared_scripts(dst_root)
            self._copy_optional_dir(skill["dir"], dst_root, "assets")

            # Copy templates if enabled (once per installation, not per skill)
            # Only copy for the first skill to avoid duplication
            if skill == skills[0]:
                self._copy_templates(install_path)

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

        # Copy templates if enabled
        if self.include_templates:
            template_dst = install_path.parent.parent / "template"
            if self.template_source.exists():
                shutil.copytree(self.template_source, template_dst, dirs_exist_ok=True)
                template_count = len(list(template_dst.rglob("*.md")))
                print(f"  ✓ Copied {template_count} template files")

        return len(skills)

    def install(self, dry_run: bool = False) -> bool:
        print(f"\n{'='*60}")
        print("Installing Agent Skills Kit (Enhanced)")
        print(f"{'='*60}")
        print(f"Agent: {self.agent_config['name']}")
        print(f"Scope: {self.scope}")
        print(f"Kit root: {self.kit_root}")
        print(f"Include templates: {self.include_templates}")
        if self.include_templates:
            print(f"Template source: {self.template_source}")
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
                print(f"  Templates: {self.template_source} -> {install_path / 'template'}")
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
        if self.include_templates:
            print(f"✓ Templates included in installation")

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

Note: Templates are included in the installation.
Skills like reverse-doc-reconstruction will use templates from:
  {install_path}/template/
"""
            )
        elif self.agent == "cursor":
            print(
                """
To use the skills in Cursor AI:
  1. Restart Cursor editor
  2. Skills are now active in .cursorrules
  3. Ask Cursor normally and mention the analysis intent

Note: Templates are copied to {project_root}/template/
"""
            )
        elif self.agent == "continue":
            print(
                """
To use the skills in Continue.dev:
  1. Restart Continue extension
  2. Use Ctrl+Shift+A (Cmd+Shift+A on Mac)
  3. Select a generated skill from the menu

Note: Templates are copied to ~/.continue/skills/template/
"""
            )
        elif self.agent == "copilot":
            print(
                """
To use the skills in GitHub Copilot:
  1. Open your repository
  2. Ensure skills are under .github/skills/
  3. Pick the relevant skill folder for the task context

Note: Templates are copied to {project_root}/template/
Skills can now access templates locally.
"""
            )
        elif self.agent == "codex":
            print(
                """
To use the skills in OpenAI CodeX:
  1. Open .openai/codex-instructions.md
  2. Copy the relevant workflow into your Codex/ChatGPT session
  3. Provide repository context and run the analysis

Note: Templates are copied to {project_root}/template/
"""
            )


def interactive_mode(kit_root: Path) -> int:
    print(f"\n{'='*60}")
    print("Agent Skills Kit - Interactive Installer (Enhanced)")
    print(f"{'='*60}\n")

    # Ask for custom kit root
    custom_kit = input(f"Kit root [{kit_root}]: ").strip()
    if custom_kit:
        kit_root = Path(custom_kit).resolve()
        if not kit_root.exists():
            print(f"Error: Kit root does not exist: {kit_root}")
            return 1

    agents = list(EnhancedAgentSkillsInstaller.AGENT_CONFIGS.keys())
    print("Select AI Agent:")
    for i, agent_key in enumerate(agents, 1):
        config = EnhancedAgentSkillsInstaller.AGENT_CONFIGS[agent_key]
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

    config = EnhancedAgentSkillsInstaller.AGENT_CONFIGS[selected_agent]
    global_path = config["install_paths"].get("global")
    local_path = config["install_paths"].get("local")

    if global_path and local_path:
        response = input("\nInstall globally or locally? [G/l]: ").strip().lower()
        scope = "global" if response.startswith("g") else "local"
    elif global_path:
        scope = "global"
    else:
        scope = "local"

    # Ask about templates
    include_templates = input("\nInclude template directory? [Y/n]: ").strip().lower()
    include_templates = include_templates != "n"

    # Ask for custom template source
    template_source = None
    if include_templates:
        custom_template = input("Template source (press Enter for default): ").strip()
        if custom_template:
            template_source = Path(custom_template).resolve()
            if not template_source.exists():
                print(f"Warning: Template source not found: {template_source}")
                print("Will use default template directory")
                template_source = None

    installer = EnhancedAgentSkillsInstaller(
        kit_root=kit_root,
        agent=selected_agent,
        scope=scope,
        include_templates=include_templates,
        template_source=template_source
    )
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

  # Install for Claude Code (from current directory)
  python scripts/install_agent_kit_with_templates.py --agent claude-code --scope global

  # Install from custom kit root (e.g., your project directory)
  python scripts/install_agent_kit_with_templates.py \\
    --kit-root /path/to/agent-skill \\
    --agent claude-code \\
    --scope global

  # Install for your project with templates
  cd /path/to/your-project
  python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \\
    --kit-root /path/to/agent-skill \\
    --agent copilot \\
    --scope local \\
    --include-templates

  # Install with custom template location
  python scripts/install_agent_kit_with_templates.py \\
    --agent claude-code \\
    --scope global \\
    --include-templates \\
    --template-source /path/to/custom-templates

  # Install without templates
  python scripts/install_agent_kit_with_templates.py \\
    --agent cursor \\
    --scope global \\
    --no-templates

  # List supported agents
  python scripts/install_agent_kit_with_templates.py --list

  # Dry run
  python scripts/install_agent_kit_with_templates.py \\
    --agent cursor \\
    --kit-root /path/to/agent-skill \\
    --dry-run
""",
    )

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

    # Determine kit root
    if args.kit_root:
        kit_root = args.kit_root.resolve()
    else:
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

        config = EnhancedAgentSkillsInstaller.AGENT_CONFIGS[selected_agent]
        if config["install_paths"].get(selected_scope) is None:
            fallback_scope = "global" if selected_scope == "local" else "local"
            if config["install_paths"].get(fallback_scope) is not None:
                print(
                    f"Info: {config['name']} does not support {selected_scope} scope. "
                    f"Using {fallback_scope}."
                )
                selected_scope = fallback_scope

        installer = EnhancedAgentSkillsInstaller(
            kit_root=kit_root,
            agent=selected_agent,
            scope=selected_scope,
            project_root=args.project_root,
            include_templates=args.include_templates,
            template_source=args.template_source
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
