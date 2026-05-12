# Agent Skills Kit

A portable agent skills toolkit, deployable on Claude Code, Cursor AI, Continue.dev, GitHub Copilot, and OpenAI Codex

## Quick Start (30 seconds)

### Option 1: npm (Recommended)

```bash
npx @hyper_dev/skills
```

Or install globally:

```bash
npm install -g @hyper_dev/skills
hyper-dev-skills
```

### Option 2: Local Installation

```bash
./scripts/install.sh
```

Select platform → confirm → done! 

## What's Included

### 26 Agent Skills

| Skill | Description | Category |
|-------|-------------|----------|
| **bidding-orchestrator** | End-to-end hybrid bidding package orchestration | Orchestration |
| **bid-evidence-hub** | MCP + internet evidence aggregation for bidding | Analysis |
| **bid-solution-designer** | Baseline vs optimized solution design for proposals | Synthesis |
| **bid-quality-gates** | Proposal lifecycle quality gate evaluation | Analysis |
| **bid-estimator** | Best/base/worst PM and hybrid cost range estimation | Analysis |
| **bid-staffing-planner** | Phase-based staffing strategy generation | Analysis |
| **bid-slide-factory** | Bid deck brief and slide artifact generation | Documentation |
| **deep-codebase-discovery** | Orchestrator for full pipeline discovery | Orchestration |
| **repo-recon** | Analyzing the Repository Structure | Analysis |
| **tech-build-audit** | Audit tech stack & build system | Analysis |
| **module-summary-report** | Architecture & Module summary | Synthesis |
| **reverse-doc-reconstruction** | Create Reverse Documentation from code | Documentation |
| **legacy-cpp-porting-guardrails** | Port C++ code safely | Porting |
| **cpp-java-migration-planner** | Dependency-aware module/file/function migration order planning for C++ to Java | Porting |
| **cpp-java-pre-porting** | Pre-porting analysis and compat-layer design for C++ to Java migration | Porting |
| **cpp-java-file-structure-porting** | 1:1 file skeleton migration from C++ to Java | Porting |
| **cpp-java-function-porting** | 1:1 function conversion workflow from C++ to Java | Porting |
| **cpp-java-porting-orchestrator** | End-to-end orchestration of staged C++ to Java migration | Orchestration |
| **bug-impact-analyzer** | Bug Analysis & Impact Assessment | Bug Analysis |
| **knows** | Unified Git + MCP + memory evidence retrieval | Analysis |
| **harness-builder** | Build AI coding agent harness infrastructure (AGENTS.md, verification, lifecycle) | Infrastructure |
| **wiki-generator** | Generate structured wiki pages from code and docs (Index, Architecture, Module, API, Setup) | Documentation |
| **hi-security** | STRIDE + OWASP security audit with MCP-assisted analysis and iterative auto-fix | Security |
| **hi-scenario** | 12-dimension edge case and scenario explorer before implementation | Analysis |
| **hi-plan** | Multi-mode technical implementation planning with red-team review | Planning |
| **hi-predict** | 5-persona pre-analysis debate to catch issues before implementation | Analysis |

**👉 [Detailed Usage Guide →](USAGE_GUIDE.md)** — Comprehensive guide for each skill with examples, inputs, outputs, and use cases.



### Multi-Platform Support

| Platform | Installation | Usage |
|----------|-------------|-------|
| **Claude Code** | `--agent claude-code` | `/skill deep-codebase-discovery` |
| **Cursor AI** | `--agent cursor --scope global` | Ask normally, active via .cursorrules |
| **Continue.dev** | `--agent continue` | Ctrl+Shift+A → Select skill |
| **GitHub Copilot** | `--agent copilot` | Auto-select from `.github/skills/*` |
| **OpenAI CodeX** | `--agent codex` | Copy prompt to ChatGPT/CodeX |

This will check:
- ✓ Claude Code: `~/.claude/skills/*/`
- ✓ Cursor global: `~/.cursorrules`
- ✓ Cursor local: `.cursorrules`
- ✓ Continue.dev: `~/.continue/skills/*.json`
- ✓ Copilot: `.github/skills/*/SKILL.md`
- ✓ CodeX: `.openai/codex-instructions.md`
- ✓ Templates: `template/` directory with 28 files



## Project Structure

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
├── cpp-java-migration-planner/
├── cpp-java-pre-porting/
├── cpp-java-file-structure-porting/
├── cpp-java-function-porting/
├── cpp-java-porting-orchestrator/
├── bug-impact-analyzer/
├── harness-builder/                 # AI agent harness engineering
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/                  # 6 pattern docs (memory, context, tool-registry...)
│   ├── templates/                   # 7 harness file templates
│   └── scripts/harness_init.py
├── wiki-generator/                  # Code/docs → structured wiki pages
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/wiki-page-template.md
│   ├── templates/                   # 5 wiki page templates (index, architecture, module, api, setup)
│   └── scripts/wiki_bootstrap.py
├── hi-security/                     # STRIDE + OWASP security audit
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/stride-owasp-checklist.md
│   └── scripts/secret_scan.py
├── hi-scenario/                     # 12-dimension edge case explorer
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/dimension-checklist.md
├── hi-plan/                         # Multi-mode technical planning
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/                  # 5 planning reference docs
├── hi-predict/                      # 5-persona pre-analysis debate
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/persona-playbook.md
│
├── template/                        # standard templates (28 files)
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
│   ├── install_agent_kit_with_templates.py  #  Enhanced installer
│   ├── convert_skill.py            # Format converter
│   ├── skill_parser.py             # Shared skill parser
│   ├── sync_manifest.py            # Manifest sync tool
│   ├── smoke_test.sh               # Smoke test suite
│   └── verify_install.sh           # Verification script
│
├── test/                             # Test artifacts
│   └── TEST_RESULTS.md              # Installation and smoke test results
├── verify/                           # Review and verification docs
│   ├── QUICK_START.md               # Quick start guide
│   ├── TEMPLATE_QUICKSTART.md       # Template quick start
│   ├── TEMPLATE_INSTALLATION_GUIDE.md
│   ├── TEMPLATE_INTEGRATION_GUIDE.md
│   ├── INSTALLER_README.md
│   ├── CROSS_PLATFORM_GUIDE.md
│   ├── SECURITY_REVIEW_REPORT.md
│   └── ...
├── MANIFEST.json                    # Skill metadata
└── README.md                        # This file
```

---

## 📖 Full Documentation

**→ [Complete Usage Guide with all 26 skills →](USAGE_GUIDE.md)**

Topics covered:
- ✅ Installation methods (npm, shell, Python)
- ✅ Each skill: purpose, when to use, how to use, inputs, outputs
- ✅ MCP requirements & validation rules
- ✅ Skill chaining workflows
- ✅ Troubleshooting guide

---

## 📦 Installation Methods

### Method 1: npm (Recommended)

```bash
# Quick install
npx @hyper_dev/skills

# Or install globally
npm install -g @hyper_dev/skills
hyper-dev-skills
```

**Why npm?**
- ✅ One-command installation
- ✅ Auto-detects your platforms (Claude Code, Cursor, Copilot, etc.)
- ✅ Self-updates
- ✅ No git clone required

### Method 2: Shell Script (Local)

```bash
git clone https://github.com/hyper-dev/agent-skill.git
cd agent-skill
./scripts/install.sh
```

### Method 3: Python Installer (Advanced)

```bash
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --include-templates
```

### Method 4: Manual (Platform-Specific)

**Claude Code:**
```bash
cp -r {bidding-orchestrator,deep-codebase-discovery,...} ~/.claude/skills/
```

**GitHub Copilot:**
```bash
cp -r {bidding-orchestrator,deep-codebase-discovery,...} .github/skills/
```

**Cursor:**
```bash
# Global scope
cp -r .cursorrules ~/.cursorrules

# Local scope (per-project)
cp -r .cursorrules .cursorrules
```

---

## Contributing

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

##  Resources

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

##  Troubleshooting

### Permission denied
```bash
chmod +x ./scripts/install.sh
```

### Claude Code can not detect skills
```bash
# check installation
ls ~/.claude/skills/*/

# Restart Claude Code CLI
```

### Cursor can not detect skills
```bash
# check .cursorrules
cat ~/.cursorrules  # global
cat .cursorrules    # local

# Restart Cursor editor
```
## 📄 License

MIT License - feel free to use and modify

---
