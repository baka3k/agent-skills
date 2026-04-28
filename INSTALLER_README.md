# Agent Skills Kit Installer

Cài đặt agent skills vào đúng thư mục của từng AI platform một cách tự động.

## 🚀 Quick Start

```bash
# Interactive mode (đơn giản nhất)
./scripts/install.sh --interactive

# Hoặc dùng Python version
python scripts/install_agent_kit.py --interactive
```

## 📦 Hỗ trợ các platforms

| Platform | Global | Local | Command |
|----------|--------|-------|---------|
| **Claude Code** | ✅ `~/.claude/skills/` | ❌ | `./scripts/install.sh --agent claude-code` |
| **Cursor AI** | ✅ `~/.cursorrules` | ✅ `.cursorrules` | `./scripts/install.sh --agent cursor --scope global` |
| **Continue.dev** | ✅ `~/.continue/skills/` | ❌ | `./scripts/install.sh --agent continue` |
| **GitHub Copilot** | ❌ | ✅ `.github/skills/` | `./scripts/install.sh --agent copilot` |
| **OpenAI CodeX** | ❌ | ✅ `.openai/codex-instructions.md` | `./scripts/install.sh --agent codex` |

## 🔧 Cách sử dụng

### Method 1: Interactive (Khuyên dùng)

```bash
./scripts/install.sh --interactive
```

Bạn sẽ được hướng dẫn:
1. Chọn AI platform
2. Chọn scope (global/local)
3. Xem kế hoạch cài đặt
4. Confirm và cài đặt

### Method 2: Direct command

```bash
# Claude Code (global only)
./scripts/install.sh --agent claude-code

# Cursor (global)
./scripts/install.sh --agent cursor --scope global

# Cursor (local - vào project)
./scripts/install.sh --agent cursor --scope local

# Continue.dev (global only)
./scripts/install.sh --agent continue

# GitHub Copilot (local only)
./scripts/install.sh --agent copilot

# OpenAI CodeX (local only)
./scripts/install.sh --agent codex
```

### Method 3: Dry run

```bash
# Xem trước khi cài
./scripts/install.sh --agent cursor --dry-run
```

### Method 4: List platforms

```bash
./scripts/install.sh --list
```

## 📂 Skills được cài đặt

| Skill | Mô tả |
|-------|-------|
| `deep-codebase-discovery` | Orchestrator cho full pipeline discovery |
| `repo-recon` | Phân tích cấu trúc repository |
| `tech-build-audit` | Audit tech stack và build system |
| `module-summary-report` | Tổng hợp architecture summary |
| `reverse-doc-reconstruction` | Tạo documentation từ code |
| `legacy-cpp-porting-guardrails` | Port C++ code an toàn |
| `bug-impact-analyzer` | Phân tích bug và đánh giá ảnh hưởng |

## 🎯 Sau khi cài đặt

### Claude Code
```bash
# Restart Claude Code
# Sử dụng skills:
/skill deep-codebase-discovery
/skill repo-recon /path/to/repo
```

### Cursor AI
```bash
# Restart Cursor
# Skills tự động active trong .cursorrules
# Hỏi Cursor bình thường:
"Analyze my codebase structure"
```

### Continue.dev
```bash
# Restart Continue extension
# Ctrl+Shift+A → Chọn skill
```

### GitHub Copilot
```bash
# Copilot đọc nhiều skill từ .github/skills/
ls .github/skills

# Prompt gợi ý
/task Use skill repo-recon from .github/skills for this repository.
```

### OpenAI CodeX
```bash
# Mở file hướng dẫn đã cài
cat .openai/codex-instructions.md

# Copy workflow phù hợp sang phiên CodeX/ChatGPT
```

## 📁 Cấu trúc sau cài đặt

### Claude Code (global)
```
~/.claude/skills/
├── deep-codebase-discovery/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/   # fallback từ kit root/scripts nếu skill không có scripts riêng
├── repo-recon/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/   # scripts riêng của skill (nếu có)
└── ...
```

### Cursor (global)
```
~/.cursorrules  # Single file với tất cả skills
```

### Cursor (local)
```
your-project/
└── .cursorrules  # Single file với tất cả skills
```

### Continue.dev (global)
```
~/.continue/skills/
├── deep-codebase-discovery.json
├── repo-recon.json
└── ...
```

### GitHub Copilot (local)
```
your-project/
└── .github/
    └── skills/
        ├── deep-codebase-discovery/
        │   ├── SKILL.md
        │   ├── references/
        │   └── scripts/
        ├── repo-recon/
        │   ├── SKILL.md
        │   ├── references/
        │   └── scripts/
        └── ...
```

### OpenAI CodeX (local)
```
your-project/
└── .openai/
    └── codex-instructions.md  # Single file với tất cả skills
```

## 🔄 Update skills

Để update skills sau khi đã sửa code:

```bash
# Chạy lại installer (sẽ overwrite cũ)
./scripts/install.sh --agent <agent> --scope <scope>

# Backup tự động được tạo trước khi overwrite
# Cursor: ~/.cursorrules.backup.YYYYMMDD_HHMMSS
# CodeX: .openai/codex-instructions.md.backup.YYYYMMDD_HHMMSS
```

## 🛠️ Troubleshooting

### Permission denied
```bash
chmod +x ./scripts/install.sh
```

### Python not found
```bash
# install.sh là wrapper của Python installer
# Cài Python 3 rồi chạy lại
python3 --version
./scripts/install.sh --agent claude-code
```

### Claude Code không thấy skills
```bash
# Kiểm tra installation path
ls ~/.claude/skills/

# Restart Claude Code CLI
# Kill và restart terminal
```

### Cursor không active skills
```bash
# Kiểm tra .cursorrules content
cat ~/.cursorrules  # cho global
cat .cursorrules    # cho local

# Restart Cursor editor
```

## 📚 Advanced Usage

### Install multiple agents
```bash
./scripts/install.sh --agent claude-code
./scripts/install.sh --agent cursor --scope global
./scripts/install.sh --agent continue
./scripts/install.sh --agent codex
```

### Custom project root
```bash
# Python version only
python scripts/install_agent_kit.py \
    --agent copilot \
    --scope local \
    --project-root /path/to/project
```

### Batch installation script
```bash
#!/bin/bash
# install-all.sh

for agent in claude-code cursor continue; do
    ./scripts/install.sh --agent "$agent"
done
```

## 🔍 Verification

Kiểm tra cài đặt thành công:

```bash
# Claude Code
ls ~/.claude/skills/*/

# Cursor global
cat ~/.cursorrules | head -20

# Cursor local
cat .cursorrules | head -20

# Continue.dev
ls ~/.continue/skills/*.json

# Copilot
ls .github/skills/*/SKILL.md

# CodeX
cat .openai/codex-instructions.md | head -20
```

## 🤝 Contributing

Để thêm skill mới:

1. Tạo skill directory với SKILL.md
2. Thêm references/ nếu cần
3. Sync MANIFEST: `python scripts/sync_manifest.py`
4. Chạy lại installer
5. Test trên từng platform

## 📖 Documentation

- [Cross-Platform Guide](../CROSS_PLATFORM_GUIDE.md) - Hướng dẫn chi tiết
- [Skill Templates](../template/) - Templates cho các platforms
- [Converter Script](./convert_skill.py) - Convert skill formats

## ⚠️ Notes

- **Global installation**: Cần cho Claude Code, Continue.dev
- **Local installation**: Khuyên dùng cho Cursor, Copilot
- **Backup**: Tự động backup khi reinstall
- **Scripts fallback**: Nếu skill không có `scripts/` riêng, installer sẽ copy `scripts/` dùng chung từ root kit
- **Permissions**: Cần write permissions cho target directories

---

**Last updated**: 2026-04-14
**Compatible with**: Claude Code, Cursor AI, Continue.dev, GitHub Copilot, OpenAI CodeX
