# Template Installation Guide

**Version**: 1.0.0
**Date**: 2025-04-17

---

## Overview

Agent Skills Kit now supports **template installation** when deploying skills to your projects. This ensures that skills like `reverse-doc-reconstruction` can access standard templates even when installed in different locations.

## Why Templates Matter

Some skills depend on template files to generate documentation artifacts:

| Skill | Templates Used | Purpose |
|-------|---------------|---------|
| **reverse-doc-reconstruction** | 11 templates from `template/` | Generate requirements, use cases, detail design |
| **repo-recon** | `module-inventory-template.md` | Generate module inventory reports |
| **tech-build-audit** | `audit-template.md` | Generate tech audit reports |
| **bug-impact-analyzer** | References `template/04_testing/` | Standard bug reports and test cases |

Without templates, these skills cannot function properly!

---

## Installation Options

### Option 1: Enhanced Installer (Recommended)

Use the new enhanced installer that includes template support:

```bash
# From agent-skill directory
python scripts/install_agent_kit_with_templates.py --interactive

# Or direct command
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

**Features**:
- ✅ Copies `template/` directory automatically
- ✅ Supports custom kit root (install from anywhere)
- ✅ Supports custom template location
- ✅ Option to exclude templates if not needed

---

### Option 2: Install to Your Project

Install skills directly to your project with templates:

```bash
cd /path/to/your-project

# Install Claude Code skills with templates
python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \
  --kit-root /path/to/agent-skill \
  --agent claude-code \
  --scope local \
  --include-templates
```

**Result**:
```
your-project/
├── .claude/
│   └── skills/
│       ├── deep-codebase-discovery/
│       │   └── SKILL.md
│       ├── reverse-doc-reconstruction/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   └── scripts/
│       └── template/           ← Templates copied here!
│           ├── 00_requirements/
│           ├── 01_usecase/
│           ├── 02_detail_design/
│           └── ...
```

---

### Option 3: Install to GitHub Copilot Project

```bash
cd /path/to/your-project

# Install Copilot skills with templates
python /path/to/agent-skill/scripts/install_agent_kit_with_templates.py \
  --kit-root /path/to/agent-skill \
  --agent copilot \
  --scope local \
  --include-templates
```

**Result**:
```
your-project/
├── .agents/
│   └── skills/
│       ├── repo-recon/
│       │   └── SKILL.md
│       ├── reverse-doc-reconstruction/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   └── scripts/
│       └── template/           ← Templates accessible here!
│           ├── 00_requirements/
│           └── ...
```

---

## Advanced Usage

### Custom Template Location

If you have custom templates in a different location:

```bash
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates \
  --template-source /path/to/custom-templates
```

**Use Cases**:
- Company-specific templates
- Custom documentation standards
- Localized templates (e.g., Vietnamese)

### Install Without Templates

If you don't need templates (for skills that don't use them):

```bash
python scripts/install_agent_kit_with_templates.py \
  --agent cursor \
  --scope global \
  --no-templates
```

### Dry Run

Preview what will be installed:

```bash
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --dry-run
```

Output:
```
[DRY RUN] Would install to:
  /Users/username/.claude/skills
  Templates: /path/to/agent-skill/template -> /Users/username/.claude/skills/template
```

---

## Template Directory Structure

After installation with templates, you'll have:

```
template/
├── 00_requirements/
│   ├── tpl_requirements_spec.md
│   └── tpl_feature_list.md
├── 01_usecase/
│   ├── tpl_usecase_list.md
│   ├── tpl_usecase_detail.md
│   └── tpl_usecase_metrics.md
├── 02_detail_design/
│   ├── tpl_screen_design.md
│   ├── tpl_api_process_design.md
│   ├── tpl_openapi_spec.yaml
│   ├── tpl_table_design.md
│   ├── tpl_sql_design.md
│   └── tpl_batch_process_design.md
├── 03_system_design/
│   ├── tpl_system_architecture.md
│   ├── tpl_infra_design.md
│   ├── tpl_security_design.md
│   └── tpl_adr.md
├── 04_testing/
│   ├── tpl_test_plan.md
│   ├── tpl_test_case.md
│   ├── tpl_bug_report.md
│   └── tpl_test_summary_report.md
├── 05_operations/
│   ├── tpl_release_note.md
│   ├── tpl_deployment.md
│   ├── tpl_runbook.md
│   └── tpl_monitoring.md
└── 06_project_mgmt/
    ├── tpl_meeting_minutes.md
    ├── tpl_risk_register.md
    └── tpl_change_log.md
```

**Total**: 28 standard templates across 6 categories

---

## Verifying Template Installation

### Check Templates Were Copied

```bash
# For Claude Code (global)
ls -la ~/.claude/skills/template/

# For local project installation
ls -la .claude/skills/template/
ls -la .github/skills/template/

# Count templates
find ~/.claude/skills/template -name "*.md" | wc -l
# Should output: 28
```

### Test Template Access

```bash
# In Claude Code
cd /path/to/your-project
/skill reverse-doc-reconstruction

# The skill should now be able to access templates from:
# ~/.claude/skills/template/ or .claude/skills/template/
```

---

## Manual Template Installation

If you prefer to copy templates manually:

```bash
# For Claude Code (global)
cp -r /path/to/agent-skill/template ~/.claude/skills/

# For local project
cp -r /path/to/agent-skill/template .claude/skills/
# or
cp -r /path/to/agent-skill/template .github/skills/

# For Continue.dev
cp -r /path/to/agent-skill/template ~/.continue/skills/
```

---

## Troubleshooting

### Templates Not Found

**Symptom**: Skill complains about missing templates

**Solution**:
1. Check if templates were installed:
   ```bash
   ls ~/.claude/skills/template/
   ```

2. Reinstall with templates:
   ```bash
   python scripts/install_agent_kit_with_templates.py \
     --agent claude-code \
     --scope global \
     --include-templates
   ```

### Permission Issues

**Symptom**: Cannot copy templates

**Solution**:
```bash
# Use sudo for global installation
sudo python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

### Custom Templates Not Working

**Symptom**: Skills still use default templates

**Solution**:
1. Verify custom template path:
   ```bash
   ls /path/to/custom-templates/
   ```

2. Reinstall with correct path:
   ```bash
   python scripts/install_agent_kit_with_templates.py \
     --agent claude-code \
     --scope global \
     --template-source /path/to/custom-templates
   ```

---

## Comparison: Original vs Enhanced Installer

| Feature | Original (`install_agent_kit.py`) | Enhanced (`install_agent_kit_with_templates.py`) |
|---------|-----------------------------------|--------------------------------------------------|
| Copy SKILL.md | ✅ | ✅ |
| Copy references/ | ✅ | ✅ |
| Copy scripts/ | ✅ | ✅ |
| Copy assets/ | ✅ | ✅ |
| Copy **template/** | ❌ | ✅ |
| Custom kit root | ❌ | ✅ |
| Custom template location | ❌ | ✅ |
| Option to exclude templates | N/A | ✅ (`--no-templates`) |
| Dry run for templates | Partial | ✅ |

---

## Best Practices

### 1. Always Include Templates

When installing skills that use templates:
- ✅ **Always use `--include-templates`** (default: True)
- Especially important for: `reverse-doc-reconstruction`, `bug-impact-analyzer`

### 2. Verify Installation

After installation, always check:
```bash
# Verify templates exist
ls ~/.claude/skills/template/

# Count should be 28
find ~/.claude/skills/template -name "*.md" | wc -l
```

### 3. Use Custom Templates for Standards

If your company has documentation standards:
```bash
# Create custom template directory
mkdir -p /path/to/company-templates

# Customize templates
cp -r /path/to/agent-skill/template/* /path/to/company-templates/
# Edit templates to match your standards

# Install with custom templates
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --template-source /path/to/company-templates
```

### 4. Keep Templates Updated

When updating agent-skill:
```bash
cd /path/to/agent-skill
git pull

# Reinstall to get updated templates
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

---

## FAQ

### Q: Do all skills need templates?

**A**: No. Only these skills require templates:
- `reverse-doc-reconstruction` (requires 11 templates)
- `repo-recon` (uses custom template, not standard)
- `tech-build-audit` (uses custom template, not standard)
- `bug-impact-analyzer` (references standard templates)

Other skills work fine without templates.

### Q: Can I share templates across projects?

**A**: Yes! Install once globally:
```bash
# Global installation for Claude Code
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --include-templates
```

All projects can now access templates from `~/.claude/skills/template/`.

### Q: What if I modify templates?

**A**: Modified templates will be used by skills. However:
- ⚠️ Updates to agent-skill may overwrite your changes
- 💡 Use `--template-source` with custom templates instead
- 💡 Or backup your changes before reinstalling

### Q: How much disk space do templates use?

**A**: Approximately 500KB - 1MB for all 28 templates.

---

## Quick Reference

### Common Commands

```bash
# Interactive (easiest)
python scripts/install_agent_kit_with_templates.py --interactive

# Claude Code with templates
python scripts/install_agent_kit_with_templates.py --agent claude-code --scope global

# Project installation with templates
python scripts/install_agent_kit_with_templates.py \
  --kit-root /path/to/agent-skill \
  --agent copilot \
  --scope local \
  --include-templates

# Custom templates
python scripts/install_agent_kit_with_templates.py \
  --agent claude-code \
  --scope global \
  --template-source /path/to/custom-templates

# Without templates
python scripts/install_agent_kit_with_templates.py \
  --agent cursor \
  --scope global \
  --no-templates
```

### Verification

```bash
# Check templates
ls ~/.claude/skills/template/

# Count templates
find ~/.claude/skills/template -name "*.md" | wc -l

# Test skill
cd /path/to/project
/skill reverse-doc-reconstruction
```

---

**Last Updated**: 2025-04-17
**Enhanced Installer**: `scripts/install_agent_kit_with_templates.py`
**Documentation**: See [TEMPLATE_INTEGRATION_GUIDE.md](TEMPLATE_INTEGRATION_GUIDE.md) for template details
