# Agent Skills Kit

Bộ kit agent skills portable, có thể cài đặt cho Claude Code, Cursor AI, Continue.dev, GitHub Copilot, OpenAI CodeX.

## 🚀 Quick Start (30 seconds)

```bash
# Interactive installation with templates (recommended)
python scripts/install_agent_kit_with_templates.py --interactive

# Or traditional installer
./scripts/install.sh --interactive
```

Chọn platform → confirm → done! 🎉

> **⚠️ IMPORTANT**: Use `install_agent_kit_with_templates.py` for skills that require templates (reverse-doc-reconstruction, bug-impact-analyzer, etc.). See [Template Installation](#-template-installation) below.

## 📦 What's Included

### 15 Agent Skills

| Skill | Description | Category |
|-------|-------------|----------|
| **bidding-orchestrator** | End-to-end hybrid bidding package orchestration | Orchestration |
| **bid-evidence-hub** | MCP + internet evidence aggregation for bidding | Analysis |
| **bid-solution-designer** | Baseline vs optimized solution design for proposals | Synthesis |
| **bid-quality-gates** | Proposal lifecycle quality gate evaluation | Analysis |
| **bid-estimator** | Best/base/worst PM and hybrid cost range estimation | Analysis |
| **bid-staffing-planner** | Phase-based staffing strategy generation | Analysis |
| **bid-slide-factory** | Bid deck brief and slide artifact generation | Documentation |
| **deep-codebase-discovery** | Orchestrator cho full pipeline discovery | Orchestration |
| **repo-recon** | Phân tích cấu trúc repository | Analysis |
| **tech-build-audit** | Audit tech stack & build system | Analysis |
| **module-summary-report** | Tổng hợp architecture summary | Synthesis |
| **reverse-doc-reconstruction** | Tạo documentation từ code | Documentation |
| **legacy-cpp-porting-guardrails** | Port C++ code an toàn | Porting |
| **bug-impact-analyzer** | Phân tích bug & đánh giá ảnh hưởng | Bug Analysis |
| **knows** | Unified Git + MCP + memory evidence retrieval | Analysis |

### Multi-Platform Support

| Platform | Installation | Usage |
|----------|-------------|-------|
| **Claude Code** | `--agent claude-code` | `/skill deep-codebase-discovery` |
| **Cursor AI** | `--agent cursor --scope global` | Ask normally, active via .cursorrules |
| **Continue.dev** | `--agent continue` | Ctrl+Shift+A → Select skill |
| **GitHub Copilot** | `--agent copilot` | Auto-select from `.github/skills/*` |
| **OpenAI CodeX** | `--agent codex` | Copy prompt to ChatGPT/CodeX |

## 📖 Documentation

### Getting Started
- **[TEMPLATE_QUICKSTART.md](TEMPLATE_QUICKSTART.md)** - 5-minute template installation guide
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide
- **[INSTALLER_README.md](INSTALLER_README.md)** - Detailed installation guide
- **[CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md)** - Cross-platform usage

### Template & Integration Guides
- **[TEMPLATE_INSTALLATION_GUIDE.md](TEMPLATE_INSTALLATION_GUIDE.md)** - Complete template installation guide
- **[TEMPLATE_INTEGRATION_GUIDE.md](TEMPLATE_INTEGRATION_GUIDE.md)** - How skills use templates
- **[TEMPLATE_INSTALLATION_SUMMARY.md](TEMPLATE_INSTALLATION_SUMMARY.md)** - Vietnamese summary

### Security & Quality
- **[SECURITY_REVIEW_REPORT.md](SECURITY_REVIEW_REPORT.md)** - Security audit (✅ PASS)
- **[MANIFEST.json](MANIFEST.json)** - Skill metadata & platform info

## 🔧 Installation

### Option 1: With Templates (Recommended)

Use enhanced installer for skills that require templates:

```bash
# Interactive mode (easiest)
python scripts/install_agent_kit_with_templates.py --interactive

# Install to your project with templates
python scripts/install_agent_kit_with_templates.py \
  --kit-root /path/to/agent-skill \
  --agent copilot \
  --scope local \
  --include-templates

# Global installation with templates
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

**When to use**: Skills like `reverse-doc-reconstruction`, `bug-impact-analyzer` need templates to function properly.

### Option 2: Traditional Installation

```bash
# Interactive mode
./scripts/install.sh --interactive

# Direct commands
# Claude Code
./scripts/install.sh --agent claude-code

# Cursor (global)
./scripts/install.sh --agent cursor --scope global

# Cursor (local)
./scripts/install.sh --agent cursor --scope local

# Continue.dev
./scripts/install.sh --agent continue

# GitHub Copilot
./scripts/install.sh --agent copilot

# OpenAI CodeX
./scripts/install.sh --agent codex
```

**When to use**: For simple skills that don't require templates (repo-recon, tech-build-audit, module-summary-report).

### Installation Comparison

| Feature | Enhanced Installer | Traditional Installer |
|---------|-------------------|----------------------|
| Copy templates | ✅ Yes | ❌ No |
| Custom kit root | ✅ Yes | ❌ No |
| Custom templates | ✅ Yes | ❌ No |
| Exclude templates option | ✅ Yes | N/A |
| Interactive mode | ✅ Yes | ✅ Yes |
| Dry run | ✅ Yes | ✅ Yes |

### List Platforms

```bash
# Enhanced installer
python scripts/install_agent_kit_with_templates.py --list

# Traditional installer
./scripts/install.sh --list
```

### Dry Run

```bash
# Enhanced installer
python scripts/install_agent_kit_with_templates.py --agent cursor --dry-run

# Traditional installer
./scripts/install.sh --agent cursor --dry-run
```

## ✅ Verify Installation

```bash
# Traditional verification
./scripts/verify_install.sh

# Verify templates (if using enhanced installer)
ls ~/.claude/skills/template/          # Claude Code global
ls .claude/skills/template/            # Local project
ls .github/skills/template/            # Copilot project
find ~/.claude/skills/template -name "*.md" | wc -l  # Should be 28
```

This will check:
- ✓ Claude Code: `~/.claude/skills/*/`
- ✓ Cursor global: `~/.cursorrules`
- ✓ Cursor local: `.cursorrules`
- ✓ Continue.dev: `~/.continue/skills/*.json`
- ✓ Copilot: `.github/skills/*/SKILL.md`
- ✓ CodeX: `.openai/codex-instructions.md`
- ✓ Templates: `template/` directory with 28 files

## 🎯 Usage Examples

### Claude Code

```bash
# Use skill directly
/skill deep-codebase-discovery

# With parameters
/skill repo-recon /path/to/repo --scope backend
```

### Cursor AI

```bash
# Skills are active in .cursorrules
# Just ask Cursor normally:
"Analyze my codebase structure"
"What's my tech stack?"
"Generate documentation from code"
```

### Continue.dev

```bash
# Ctrl+Shift+A to open skills menu
# Select your skill

# Or use slash command
/codebase-discovery
```

### GitHub Copilot

```markdown
# Copilot scans .github/skills/
# Pick one skill context explicitly in your prompt:
/task Use skill deep-codebase-discovery from .github/skills and analyze this repo.
```

## 🔄 Update Skills

```bash
# Re-run installer to update
./scripts/install.sh --agent <agent> --scope <scope>

# Backup tự động được tạo trước khi overwrite
```

## 📁 Project Structure

```
agent-skill/
├── bidding-orchestrator/           # Project bidding orchestrator
│   ├── SKILL.md
│   ├── contracts/
│   ├── examples/
│   ├── references/
│   └── scripts/
├── bid-evidence-hub/
├── bid-solution-designer/
├── bid-quality-gates/
├── bid-estimator/
├── bid-staffing-planner/
├── bid-slide-factory/
├── deep-codebase-discovery/        # Skill directories
│   ├── SKILL.md                     # Main skill definition
│   ├── references/                  # Supporting docs & playbooks
│   │   └── mcp-orchestration-playbook.md
│   └── scripts/                     # Skill-specific scripts (optional in source)
├── repo-recon/
├── tech-build-audit/
├── module-summary-report/
├── reverse-doc-reconstruction/
├── legacy-cpp-porting-guardrails/
├── bug-impact-analyzer/
│
├── template/                        # 🎯 Standard templates (28 files)
│   ├── 00_requirements/            # Requirements templates
│   │   ├── tpl_requirements_spec.md
│   │   └── tpl_feature_list.md
│   ├── 01_usecase/                 # Use case templates
│   │   ├── tpl_usecase_list.md
│   │   ├── tpl_usecase_detail.md
│   │   └── tpl_usecase_metrics.md
│   ├── 02_detail_design/           # Design templates
│   │   ├── tpl_screen_design.md
│   │   ├── tpl_api_process_design.md
│   │   ├── tpl_openapi_spec.yaml
│   │   ├── tpl_table_design.md
│   │   ├── tpl_sql_design.md
│   │   └── tpl_batch_process_design.md
│   ├── 03_system_design/           # Architecture templates
│   ├── 04_testing/                 # Testing templates
│   ├── 05_operations/              # Ops templates
│   └── 06_project_mgmt/            # PM templates
│
├── scripts/                         # Installer & tools
│   ├── install.sh                  # Shell installer (traditional)
│   ├── install_agent_kit.py        # Python installer (traditional)
│   ├── install_agent_kit_with_templates.py  # ⭐ Enhanced installer
│   ├── convert_skill.py            # Format converter
│   ├── skill_parser.py             # Shared skill parser
│   ├── sync_manifest.py            # Manifest sync tool
│   ├── smoke_test.sh               # Smoke test suite
│   └── verify_install.sh           # Verification script
│
├── MANIFEST.json                    # Skill metadata
├── QUICK_START.md                   # Quick start guide
├── TEMPLATE_QUICKSTART.md           # ⭐ Template quick start
├── TEMPLATE_INSTALLATION_GUIDE.md   # ⭐ Complete template guide
├── TEMPLATE_INTEGRATION_GUIDE.md    # ⭐ Template usage details
├── INSTALLER_README.md              # Installation guide
├── CROSS_PLATFORM_GUIDE.md          # Cross-platform usage
├── SECURITY_REVIEW_REPORT.md        # Security audit (✅ PASS)
└── README.md                        # This file
```

## 🛠️ Advanced Usage

### Convert Skills for Other Platforms

```bash
# Convert single skill
python scripts/convert_skill.py --skill deep-codebase-discovery --format copilot

# Convert all skills
python scripts/convert_skill.py --all --format cursor

# Output directory
python scripts/convert_skill.py --all --format continue --output ./converted
```

### Custom Installation

```bash
# Enhanced installer - install from any directory
python scripts/install_agent_kit_with_templates.py \
    --kit-root /path/to/agent-skill \
    --agent copilot \
    --scope local \
    --include-templates

# Traditional installer - with custom project root
python scripts/install_agent_kit.py \
    --agent copilot \
    --scope local \
    --project-root /path/to/project
```

### Batch Installation

```bash
#!/bin/bash
# install-all.sh

for agent in claude-code cursor continue codex; do
    ./scripts/install.sh --agent "$agent"
done
```

### Sync MANIFEST.json từ skill directories

```bash
# Rewrite MANIFEST.json["skills"] from discovered */SKILL.md
python scripts/sync_manifest.py

# Check-only mode (CI friendly)
python scripts/sync_manifest.py --check
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add/modify skills in `*/SKILL.md`
4. Sync manifest: `python scripts/sync_manifest.py`
5. Run smoke tests: `./scripts/smoke_test.sh`
6. Optional verification: `./scripts/verify_install.sh`
7. Submit PR

### Adding New Skills

1. Create directory: `your-skill/SKILL.md`
2. Add metadata in YAML frontmatter
3. Add references/ if needed
4. Review quality using `template/06_project_mgmt/tpl_skill_review_checklist_mcp_first.md`
5. Run `python scripts/sync_manifest.py`
6. Test installer

## 📚 Resources

### Core Features
- **MCP Integration**: Skills support mind_mcp and graph_mcp
- **Context Control**: Strategy for large codebases
- **Template System**: 28 standard templates across 6 categories
- **Security**: Comprehensive redaction patterns (see SECURITY_REVIEW_REPORT.md)

### Templates
- **Standard Templates**: `template/` directory with requirements, use cases, design, testing, operations, PM templates
- **Template Usage**: How skills use templates (see TEMPLATE_INTEGRATION_GUIDE.md)
- **Template Installation**: Installing skills with templates (see TEMPLATE_QUICKSTART.md)
- **Skill Review Checklist**: `template/06_project_mgmt/tpl_skill_review_checklist_mcp_first.md`

### Tools
- **Converter**: Convert between skill formats
- **Manifest Sync**: Keep MANIFEST.json in sync with skills
- **Smoke Tests**: Validate skill quality

## ⚠️ Troubleshooting

### Permission denied
```bash
chmod +x ./scripts/install.sh
```

### Claude Code không thấy skills
```bash
# Kiểm tra installation
ls ~/.claude/skills/*/

# Restart Claude Code CLI
```

### Cursor không active skills
```bash
# Kiểm tra .cursorrules
cat ~/.cursorrules  # global
cat .cursorrules    # local

# Restart Cursor editor
```

### Templates not found error

**Symptom**: Skill complains "Template not found: template/01_usecase/tpl_usecase_list.md"

**Solution 1**: Use enhanced installer
```bash
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

**Solution 2**: Manually copy templates
```bash
# For Claude Code (global)
cp -r /path/to/agent-skill/template ~/.claude/skills/

# For local project
cp -r /path/to/agent-skill/template .github/skills/
```

**Solution 3**: Verify templates exist
```bash
ls ~/.claude/skills/template/
find ~/.claude/skills/template -name "*.md" | wc -l  # Should be 28
```

### Skills fail after installation

Installer hiện tại sẽ copy `scripts/` theo thứ tự:
1. `scripts/` riêng của từng skill (nếu có)
2. fallback `scripts/` dùng chung từ root kit (nếu skill không có script riêng)

**Check 1**: Verify all files were installed
```bash
# Claude Code
ls ~/.claude/skills/deep-codebase-discovery/
# Should show: SKILL.md, references/, scripts/

# Copilot
ls .github/skills/reverse-doc-reconstruction/
# Should show: SKILL.md, references/, scripts/
```

**Check 2**: Verify templates if needed
```bash
# For template-dependent skills
ls ~/.claude/skills/template/
ls .github/skills/template/
```

**Check 3**: Reinstall with enhanced installer
```bash
python scripts/install_agent_kit_with_templates.py \
  --agent <your-agent> \
  --scope <global|local> \
  --include-templates \
  --dry-run  # Preview first
```

## 📄 License

MIT License - feel free to use and modify

## 🙏 Acknowledgments

Built for AI agents everywhere, with ❤️

---

**Version**: 1.2.0
**Last updated**: 2026-04-26
**Compatible with**: Claude Code, Cursor AI, Continue.dev, GitHub Copilot, OpenAI CodeX

### Recent Updates
- ✅ **Project Bidding Suite**: Added 7 bidding-focused skills and contracts
- ✅ **Hybrid estimator pipeline**: Fixed-price + T&M range generation with confidence tiers
- ✅ **Bid package generator**: Proposal, estimate, staffing, quality, evidence, and slide outputs
- ✅ **Enhanced installer**: Template support (`install_agent_kit_with_templates.py`)
- ✅ **Template integration**: All template-dependent scripts updated
- ✅ **Security audit**: Complete review (✅ PASS)
- ✅ **Documentation**: Template installation guides added
