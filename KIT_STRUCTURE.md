# 🎯 Agent Skills Kit - Tổng quan

## 📦 Bộ kit có gì?

### ✅ 6 Agent Skills (và MCP integration)

```
deep-codebase-discovery/     ← Orchestrator (chạy 3 skills dưới)
repo-recon/                  ← Phân tích cấu trúc
tech-build-audit/            ← Audit tech stack
module-summary-report/       ← Tổng hợp findings
reverse-doc-reconstruction/  ← Tạo docs từ code
legacy-cpp-porting-guardrails/ ← Port C++ an toàn
```

### ✅ Multi-Platform Installer

```bash
# Shell version (nhẹ, nhanh)
./scripts/install.sh --interactive

# Python version (full features)
python scripts/install_agent_kit.py --interactive
```

### ✅ Support Platforms

| Platform | Global | Local | Command |
|----------|--------|-------|---------|
| **Claude Code** | ✅ | ❌ | `--agent claude-code` |
| **Cursor AI** | ✅ | ✅ | `--agent cursor --scope global/local` |
| **Continue.dev** | ✅ | ❌ | `--agent continue` |
| **GitHub Copilot** | ❌ | ✅ | `--agent copilot` |

## 🚀 Quick Start

```bash
# 1. Clone repo
cd agent-skill

# 2. Chạy installer
./scripts/install.sh --interactive

# 3. Chọn platform, confirm, done!

# 4. Verify
./scripts/verify_install.sh
```

## 📁 Cấu trúc thư mục

```
agent-skill/
│
├── 📂 deep-codebase-discovery/        # Skills
│   ├── SKILL.md
│   └── references/
│
├── 📂 repo-recon/
├── 📂 tech-build-audit/
├── 📂 module-summary-report/
├── 📂 reverse-doc-reconstruction/
├── 📂 legacy-cpp-porting-guardrails/
│
├── 📂 template/                        # Templates & resources
│   ├── prompt-templates/              # Universal prompts
│   └── mcp-context-control-strategy.md # Large codebase strategy
│
├── 📂 scripts/                         # Tools
│   ├── install.sh                     # Shell installer ⚡
│   ├── install_agent_kit.py           # Python installer
│   ├── convert_skill.py               # Format converter
│   └── verify_install.sh              # Verify installation
│
├── 📄 README.md                        # Main documentation
├── 📄 QUICK_START.md                   # 30-second guide
├── 📄 INSTALLER_README.md              # Installation guide
├── 📄 CROSS_PLATFORM_GUIDE.md          # Cross-platform usage
├── 📄 MANIFEST.json                    # Metadata
└── 📄 KIT_STRUCTURE.md                 # This file
```

## 🔧 Installation Flow

```
┌─────────────────────────────────────────┐
│  1. ./scripts/install.sh --interactive │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Chọn AI platform                    │
│     □ Claude Code                       │
│     □ Cursor AI                         │
│     □ Continue.dev                      │
│     □ GitHub Copilot                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Chọn scope (global/local)           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. Xem kế hoạch cài đặt                │
│     - Agent: Cursor AI                  │
│     - Scope: global                     │
│     - Path: ~/.cursorrules              │
│     - Skills: 6                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  5. Confirm → Install                   │
│     ✓ Backup existing files             │
│     ✓ Convert skills to target format   │
│     ✓ Install to correct path           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  6. Done!                                │
│     ✓ 6 skills installed                │
│     ✓ Post-install instructions          │
└─────────────────────────────────────────┘
```

## 📖 Documentation Map

| Document | Mục đích | Audience |
|----------|----------|----------|
| **QUICK_START.md** | Bắt đầu nhanh (30s) | Tất cả |
| **INSTALLER_README.md** | Hướng dẫn cài đặt chi tiết | User |
| **CROSS_PLATFORM_GUIDE.md** | Dùng skills chéo platforms | Power user |
| **KIT_STRUCTURE.md** | Tổng quan cấu trúc | User |
| **README.md** | Main documentation | Tất cả |
| **MANIFEST.json** | Skill metadata | Developer |

## 🎯 Usage Examples

### Claude Code
```bash
/skill deep-codebase-discovery
/skill repo-recon /path/to/repo --scope backend
```

### Cursor AI
```bash
# Skills active trong .cursorrules
# Hỏi bình thường:
"Analyze my codebase structure"
```

### Continue.dev
```bash
# Ctrl+Shift+A → Chọn skill
/codebase-discovery
```

### GitHub Copilot
```markdown
/task Analyze my codebase
```

## 🔄 Workflow

```
┌────────────────────────────────────────────┐
│  Input: Repository path + Scope            │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  Phase 1: mind_mcp (Documentation)         │
│  - Architecture intent                     │
│  - Domain terms                            │
│  - Build/release process                   │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  Phase 2: graph_mcp (Source Code)          │
│  - Module boundaries                       │
│  - Entry points                            │
│  - Call graph & flows                      │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  Phase 3: Filesystem (Fallback)            │
│  - Config files                            │
│  - Missing gaps                            │
└──────────────┬─────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────┐
│  Output: Discovery bundle                  │
│  - Module inventory                        │
│  - Tech matrix                             │
│  - Critical flows                          │
│  - Risk assessment                         │
└────────────────────────────────────────────┘
```

## 🛠️ Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Permission denied | `chmod +x ./scripts/install.sh` |
| Skills not found | `./scripts/verify_install.sh` |
| Wrong path | Re-run installer with `--dry-run` |
| Need update | Re-run installer (auto backup) |

## 📞 Next Steps?

1. **New user**: Start with [QUICK_START.md](QUICK_START.md)
2. **Installing**: See [INSTALLER_README.md](INSTALLER_README.md)
3. **Cross-platform**: See [CROSS_PLATFORM_GUIDE.md](CROSS_PLATFORM_GUIDE.md)
4. **Contributing**: Check [MANIFEST.json](MANIFEST.json) for metadata

---

**Made with ❤️ for AI agents everywhere**

Version: 1.0.0 | Last updated: 2025-04-13
