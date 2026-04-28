# Template Installation - Summary

## ❌ Vấn Đề (Problem)

Hiện tại, khi install Agent Skills Kit, **template directory KHÔNG được copy theo**.

### Impact

Khi bạn install skills từ agent-skill directory sang project khác hoặc global installation:

```bash
# Script install hiện tại chỉ copy:
- SKILL.md ✅
- references/ ✅
- scripts/ ✅
- assets/ ✅
- template/ ❌ KHÔNG COPY!
```

### Kết Quả

Các skills sau sẽ **KHÔNG HOẠT ĐỘNG** đúng cách:

1. **reverse-doc-reconstruction** → Cần 11 templates từ `template/`
2. **repo-recon** → Cần `module-inventory-template.md`
3. **tech-build-audit** → Cần `audit-template.md`
4. **bug-impact-analyzer** → Reference templates từ `template/04_testing/`

**Lỗi gặp phải**:
```
Error: Template not found: template/01_usecase/tpl_usecase_list.md
```

---

## ✅ Giải Pháp (Solution)

### Enhanced Installer với Template Support

Tạo mới: `scripts/install_agent_kit_with_templates.py`

**Features**:
1. ✅ Copy template/ directory khi install
2. ✅ Hỗ trợ install từ bất kỳ directory nào (`--kit-root`)
3. ✅ Hỗ trợ custom template location (`--template-source`)
4. ✅ Option để exclude templates nếu không cần (`--no-templates`)

---

## 🚀 Cách Sử Dụng

### Cách 1: Interactive Mode (Dễ nhất)

```bash
cd /path/to/agent-skill
python scripts/install_agent_kit_with_templates.py --interactive
```

### Cách 2: Install to Project của Bạn

```bash
cd /path/to/your-project

# Install từ agent-skill directory
python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \
  --kit-root /path/to/agent-skill \
  --agent copilot \
  --scope local \
  --include-templates
```

**Kết quả**:
```
your-project/
├── .agents/
│   └── skills/
│       ├── reverse-doc-reconstruction/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   └── scripts/
│       └── template/           ← Templates được copy vào đây!
│           ├── 00_requirements/
│           ├── 01_usecase/
│           └── ...
```

### Cách 3: Global Installation

```bash
# Install to ~/.claude/skills với templates
python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

### Cách 4: Custom Templates

```bash
# Use custom template directory
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --template-source /path/to/company-templates
```

---

## 📦 Installation Options

| Option | Description | Example |
|--------|-------------|---------|
| `--agent` | AI platform | `claude-code`, `copilot`, `cursor` |
| `--scope` | global hoặc local | `--scope global` |
| `--kit-root` | Path tới agent-skill | `--kit-root /path/to/agent-skill` |
| `--include-templates` | Copy templates (default: True) | có hoặc không |
| `--no-templates` | Không copy templates | `--no-templates` |
| `--template-source` | Custom template path | `--template-source /custom/path` |
| `--dry-run` | Preview installation | `--dry-run` |
| `--interactive` | Interactive mode | `--interactive` |

---

## ✅ Verification

### Check Templates

```bash
# Claude Code (global)
ls ~/.claude/skills/template/

# Local project
ls .claude/skills/template/
ls .github/skills/template/

# Đếm số templates
find ~/.claude/skills/template -name "*.md" | wc -l
# Expected: 28
```

### Test Skill

```bash
cd /path/to/your-project

# Trong Claude Code
/skill reverse-doc-reconstruction

# Skill sẽ tìm templates ở:
# ~/.claude/skills/template/ hoặc .claude/skills/template/
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **TEMPLATE_QUICKSTART.md** | 5-minute quick start |
| **TEMPLATE_INSTALLATION_GUIDE.md** | Complete installation guide |
| **TEMPLATE_INTEGRATION_GUIDE.md** | Template usage in skills |

---

## 🔧 So Sánh: Original vs Enhanced

| Feature | Original | Enhanced |
|---------|----------|----------|
| Copy SKILL.md | ✅ | ✅ |
| Copy references/ | ✅ | ✅ |
| Copy scripts/ | ✅ | ✅ |
| Copy **template/** | ❌ | ✅ |
| Custom kit root | ❌ | ✅ |
| Custom template location | ❌ | ✅ |
| Option to exclude templates | N/A | ✅ |
| Interactive mode | ✅ | ✅ Enhanced |

---

## 🎯 Best Practices

### 1. Luôn Include Templates cho Skills Phức Tạp

```bash
# Cho reverse-doc-reconstruction, bug-impact-analyzer
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

### 2. Use Custom Templates cho Company Standards

```bash
# Tạo company templates
mkdir -p /path/to/company-templates
cp -r /path/to/agent-skill/template/* /path/to/company-templates/
# Edit để match company standards

# Install với custom templates
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --template-source /path/to/company-templates
```

### 3. Verify Sau Khi Install

```bash
# Luôn check templates exist
ls ~/.claude/skills/template/

# Đếm (should be 28)
find ~/.claude/skills/template -name "*.md" | wc -l
```

---

## 🐛 Troubleshooting

### Templates Not Found

```bash
# 1. Check templates exist
ls ~/.claude/skills/template/

# 2. Reinstall với templates
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

### Custom Templates Không Work

```bash
# 1. Verify custom template path
ls /path/to/custom-templates/

# 2. Reinstall với correct path
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --template-source /correct/path
```

---

## 📝 Summary

### Vấn Đề
- ❌ Original script KHÔNG copy template directory
- ❌ Skills cần templates sẽ fail khi install ở nơi khác

### Giải Pháp
- ✅ Enhanced installer với template support
- ✅ Copy template directory khi install
- ✅ Hỗ trợ custom paths
- ✅ Option để exclude templates

### Sử Dụng
```bash
# Cách dễ nhất
python scripts/install_agent_kit_with_templates.py --interactive

# Hoặc direct command
python scripts/install_agent_kit_with_templates.py \
  --agent copilot \
  --scope local \
  --include-templates
```

---

**Files Created**:
1. `scripts/install_agent_kit_with_templates.py` - Enhanced installer
2. `TEMPLATE_QUICKSTART.md` - 5-minute quick start
3. `TEMPLATE_INSTALLATION_GUIDE.md` - Complete guide
4. `TEMPLATE_INSTALLATION_SUMMARY.md` - This file

**Last Updated**: 2025-04-17
