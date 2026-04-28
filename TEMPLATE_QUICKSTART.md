# Template Installation Quick Start

**5 minutes to install skills with templates**

---

## 🚀 Fastest Way (Interactive)

```bash
cd /path/to/agent-skill
python scripts/install_agent_kit_with_templates.py --interactive
```

Follow the prompts → Done! 🎉

---

## 📋 Or Direct Commands

### Install to Your Project

```bash
cd /path/to/your-project

# Install Copilot skills + templates to current project
python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \
  --kit-root /path/to/agent-skill \
  --agent copilot \
  --scope local \
  --include-templates
```

### Install Globally (Claude Code)

```bash
# Install to ~/.claude/skills with templates
python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

### Install from Custom Location

```bash
# Install from anywhere
python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \
  --kit-root /path/to/agent-skill \
  --agent claude-code \
  --scope global \
  --include-templates
```

---

## ✅ Verify Installation

```bash
# Check templates were copied
ls ~/.claude/skills/template/

# Should see 28 template files
find ~/.claude/skills/template -name "*.md" | wc -l
```

---

## 🎯 What Gets Installed

```
~/.claude/skills/
├── deep-codebase-discovery/SKILL.md
├── reverse-doc-reconstruction/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
└── template/              ← 28 templates
    ├── 00_requirements/
    ├── 01_usecase/
    ├── 02_detail_design/
    ├── 03_system_design/
    ├── 04_testing/
    ├── 05_operations/
    └── 06_project_mgmt/
```

---

## 🔧 Common Options

| Need | Command |
|------|---------|
| **No templates** | Add `--no-templates` |
| **Custom templates** | Add `--template-source /path/to/templates` |
| **Preview only** | Add `--dry-run` |
| **Local project** | Use `--scope local` |
| **Global install** | Use `--scope global` |

---

## 📖 Full Documentation

- **[TEMPLATE_INSTALLATION_GUIDE.md](TEMPLATE_INSTALLATION_GUIDE.md)** - Complete guide
- **[TEMPLATE_INTEGRATION_GUIDE.md](TEMPLATE_INTEGRATION_GUIDE.md)** - Template details

---

**Pro Tip**: Use `--interactive` mode for first-time installation!
