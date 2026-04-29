# Agent Skills Kit - Quick Start

Bộ kit agent skills có thể cài đặt cho Claude Code, Cursor AI, Continue.dev, GitHub Copilot, OpenAI CodeX.

## 🚀 30-second Quick Start

```bash
# Clone hoặc navigate tới repo
cd agent-skill

# Chạy installer (interactive mode)
./scripts/install.sh --interactive

# Hoặc dùng Python version
python scripts/install_agent_kit.py --interactive
```

That's it! Chọn platform → confirm → done. 🎉

## 📋 Platform Support

| Platform | Command |
|----------|---------|
| **Claude Code** | `./scripts/install.sh --agent claude-code` |
| **Cursor AI** | `./scripts/install.sh --agent cursor --scope global` |
| **Continue.dev** | `./scripts/install.sh --agent continue` |
| **GitHub Copilot** | `./scripts/install.sh --agent copilot` |
| **OpenAI CodeX** | `./scripts/install.sh --agent codex` |

## 🎯 What's included

7 Agent Skills:
- **deep-codebase-discovery**: Full pipeline orchestrator
- **repo-recon**: Repository reconnaissance
- **tech-build-audit**: Tech stack & build audit
- **module-summary-report**: Architecture synthesis
- **reverse-doc-reconstruction**: Documentation generation
- **legacy-cpp-porting-guardrails**: C++ porting safety
- **bug-impact-analyzer**: Bug impact analysis

## 📖 Documentation

- **[INSTALLER_README.md](INSTALLER_README.md)** - Full installation guide
- **[CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md)** - Cross-platform usage
- **[template/](template/)** - Prompt templates & resources

## 🔍 Verify Installation

```bash
# Run verification script
./scripts/verify_install.sh

# Or check manually
ls ~/.claude/skills/*/          # Claude Code
cat ~/.cursorrules | head -20   # Cursor global
cat .cursorrules | head -20     # Cursor local
ls ~/.continue/skills/*.json    # Continue.dev
ls .github/skills/*/SKILL.md    # Copilot
cat .openai/codex-instructions.md | head -20    # CodeX
```

## 🛠️ Troubleshooting

```bash
# List supported agents
./scripts/install.sh --list

# Dry run (xem trước khi cài)
./scripts/install.sh --agent cursor --dry-run

# Check permissions
chmod +x ./scripts/install.sh
```

## 💡 Pro Tips

1. **Global vs Local**:
   - Global: Claude Code, Continue.dev (cần)
   - Local: Cursor, Copilot, CodeX (khuyên dùng)

2. **Reinstall**:
   - Chạy lại lệnh install → tự động backup cũ
   - Backup format: `.backup.YYYYMMDD_HHMMSS`

3. **Multiple agents**:
   - Có thể cài cho nhiều platforms cùng lúc
   - Mỗi platform independent

## 📞 Need Help?

- See [INSTALLER_README.md](INSTALLER_README.md) for detailed guide
- Check [CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md) for usage examples
- Run `python scripts/sync_manifest.py --check` to verify manifest consistency

---

**Made with ❤️ for AI agents everywhere**
