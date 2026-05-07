# Agent Skills Hooks Migration Guide

**Version**: 1.0.0
**Date**: 2026-05-05
**Breaking Change**: ✅ Yes - Mandatory hooks for all skills

## Overview

This guide helps you migrate existing agent skills to support the new mandatory hooks system. All skills in the agent-skills-kit must now include hook declarations in their SKILL.md frontmatter.

---

## What Changed?

### Breaking Changes

1. **Mandatory Hooks**: All skills must declare hooks in SKILL.md frontmatter
2. **Claude Code Integration**: Hooks use Claude Code's settings.json infrastructure (no custom executor)
3. **Fail-Fast Strategy**: All errors abort skill execution (no fallback/continue)
4. **Performance Target**: Hook overhead target is 250ms (updated from 100ms)

### New Features

1. **Centralized Hook Registry**: Reusable hook patterns in `template/hooks/`
2. **MCP Health Checks**: Automatic MCP availability validation
3. **Input Validation**: Centralized path, command, and file validation
4. **Progress Reporting**: Built-in progress tracking for long workflows
5. **Cleanup Automation**: Automated cache/temp cleanup with dry-run safety

---

## Migration Steps

### Step 1: Understand Required Hooks

All skills must include these hooks in their SKILL.md:

```yaml
---
name: your-skill
version: x.y.z
hooks:
  pre:
    - mcp-health-check      # Required for MCP-dependent skills
    - input-validation      # Required for all skills
  post:
    - cleanup-handler       # Required for skills that create artifacts
  phase:
    all_phases:
      post: [progress-reporter]  # Required for multi-phase skills
---
```

### Step 2: Identify Your Skill Category

**Category A: MCP-Dependent Skills** (most skills)
- Uses mind_mcp or graph_mcp
- Must include: `mcp-health-check`, `input-validation`, `progress-reporter`

**Category B: Simple Skills**
- No MCP dependencies
- Must include: `input-validation`

**Category C: Orchestrator Skills**
- Coordinates other skills
- Must include: All hooks plus skill-chain verification

### Step 3: Add Hooks to SKILL.md

#### Before (Example):

```yaml
---
name: cpp-java-migration-planner
description: "Plan migration order..."
version: 2.0.0
---
```

#### After (Example):

```yaml
---
name: cpp-java-migration-planner
description: "Plan migration order..."
version: 2.1.0
hooks:
  pre:
    - name: mcp-health-check
      timeout: 15s
      required: true
    - name: input-validation
      scope: [source_root, migration_scope]
      enable_redaction: true
  phase:
    phase_0_preflight:
      post: [progress-reporter]
    phase_2_dependency_graph:
      pre: [mcp-health-check]  # Re-check before heavy MCP usage
      on_timeout: abort
    all_phases:
      post: [progress-reporter]
  post:
    - name: cleanup-handler
      paths: [migration-planning-data/]
      keep: [*.json, *.md]
---
```

### Step 4: Test Your Hooks

1. **Verify Hook Declarations**:
   ```bash
   python scripts/sync_manifest.py
   ```

2. **Run Smoke Tests**:
   ```bash
   ./scripts/smoke_test.sh
   ```

3. **Test Hook Execution**:
   - Run your skill with `/skill your-skill`
   - Verify hooks execute before/after skill
   - Check MCP health checks work
   - Validate input validation blocks invalid inputs

---

## Hook Reference

### Pre-Execution Hooks

#### mcp-health-check
- **Purpose**: Verify MCP availability before skill execution
- **Required**: For MCP-dependent skills
- **Timeout**: 15s (default)
- **On Failure**: Abort

```yaml
hooks:
  pre:
    - mcp-health-check  # Basic usage
    - name: mcp-health-check
      timeout: 20s  # Custom timeout
```

#### input-validation
- **Purpose**: Centralized input validation
- **Required**: For all skills
- **Timeout**: 5s (default)
- **On Failure**: Abort

```yaml
hooks:
  pre:
    - input-validation  # Basic usage
    - name: input-validation
      scope: [path.exists, path.readable, file.size_limit]
      enable_redaction: true
```

### Post-Execution Hooks

#### cleanup-handler
- **Purpose**: Cache and temp file cleanup
- **Required**: For skills creating artifacts
- **Timeout**: 60s (default)
- **On Failure**: Warn (doesn't affect skill result)

```yaml
hooks:
  post:
    - cleanup-handler  # Basic usage (dry-run)
    - name: cleanup-handler
      dry_run: false  # Production cleanup
```

### Phase Hooks

#### progress-reporter
- **Purpose**: Progress tracking for long workflows
- **Required**: For multi-phase skills
- **Timeout**: 2s (default)
- **On Failure**: Warn (doesn't affect workflow)

```yaml
hooks:
  phase:
    all_phases:
      post: [progress-reporter]
    phase_2:
      post: [progress-reporter]  # Specific phase
```

---

## Common Migration Patterns

### Pattern 1: MCP-Dependent Analysis Skill

```yaml
---
name: bug-impact-analyzer
version: 1.1.0
hooks:
  pre:
    - mcp-health-check
    - input-validation
  post:
    - cleanup-handler
  phase:
    all_phases:
      post: [progress-reporter]
---
```

### Pattern 2: Multi-Phase Migration Skill

```yaml
---
name: cpp-java-migration-planner
version: 2.1.0
hooks:
  pre:
    - mcp-health-check
    - input-validation
  phase:
    phase_0_preflight:
      post: [progress-reporter]
    phase_2_dependency_graph:
      pre: [mcp-health-check]  # Re-check MCP
      post: [progress-reporter]
    phase_3_ordering:
      post: [progress-reporter]
  post:
    - cleanup-handler
---
```

### Pattern 3: Orchestrator Skill

```yaml
---
name: bidding-orchestrator
version: 1.1.0
hooks:
  pre:
    - mcp-health-check
    - input-validation
    - skill-chain-verification  # Orchestrator-specific
  phase:
    all_phases:
      post: [progress-reporter]
  post:
    - cleanup-handler
    - metrics-aggregator
---
```

### Pattern 4: Simple Utility Skill

```yaml
---
name: bid-estimator
version: 1.1.0
hooks:
  pre:
    - input-validation
  post:
    - cleanup-handler
---
```

---

## Troubleshooting

### Issue: "Hook not found in registry"

**Solution**: Ensure hook name matches registry.yaml
```bash
# Check available hooks
cat template/hooks/registry.yaml | grep -A 5 "name:"
```

### Issue: "MCP health check failed"

**Solution**: Verify MCP servers are running
```bash
# Check MCP availability
# In Claude Code, run MCP functions manually
```

### Issue: "Input validation blocking valid inputs"

**Solution**: Adjust validation scope
```yaml
hooks:
  pre:
    - name: input-validation
      scope: [path.exists, path.readable]  # Remove strict checks
```

### Issue: "Cleanup in dry-run mode too long"

**Solution**: Enable actual cleanup
```yaml
hooks:
  post:
    - name: cleanup-handler
      dry_run: false  # Set to false in production
```

---

## Automated Migration Tool

### Quick Migration Script

```python
# scripts/add_hooks_to_skill.py
import yaml
import sys

def add_hooks_to_skill(skill_path):
    """Add mandatory hooks to a skill's SKILL.md"""

    # Read existing SKILL.md
    with open(skill_path, 'r') as f:
        content = f.read()

    # Parse frontmatter
    if '---' not in content:
        print("No YAML frontmatter found")
        return False

    # Add hooks if not present
    if 'hooks:' not in content:
        # Insert hooks after version line
        hooks_yaml = """
hooks:
  pre:
    - mcp-health-check
    - input-validation
  post:
    - cleanup-handler
  phase:
    all_phases:
      post: [progress-reporter]
"""
        # Insert hooks (implementation details)
        # ...

    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_hooks_to_skill.py <skill-path>")
        sys.exit(1)

    skill_path = sys.argv[1]
    if add_hooks_to_skill(skill_path):
        print(f"✅ Hooks added to {skill_path}")
    else:
        print(f"❌ Failed to add hooks to {skill_path}")
```

**Usage**:
```bash
python scripts/add_hooks_to_skill.py cpp-java-migration-planner/SKILL.md
```

---

## Validation Checklist

Before submitting your migrated skill:

- [ ] SKILL.md has `hooks:` section in frontmatter
- [ ] MCP-dependent skills include `mcp-health-check`
- [ ] All skills include `input-validation`
- [ ] Multi-phase skills include `progress-reporter`
- [ ] Skills creating artifacts include `cleanup-handler`
- [ ] Hook names match registry.yaml
- [ ] Version incremented (e.g., 1.0.0 → 1.1.0)
- [ ] Skill tested with `/skill your-skill`
- [ ] MCP health checks pass
- [ ] Input validation works
- [ ] Cleanup runs without errors

---

## Support

**Questions?** Check these resources:

- Hook Registry: `template/hooks/registry.yaml`
- Hook Templates: `template/hooks/*.yaml`
- Main Plan: `.claude/plans/260505-1011-hooks-strategy/plan.md`
- Phase Files: `.claude/plans/260505-1011-hooks-strategy/phase-*.md`

**Getting Help**:

1. Check if your question is answered in this guide
2. Review hook templates for examples
3. Test hooks in isolation before full skill execution
4. Run smoke tests to verify integration

---

## Summary

✅ **All skills must migrate to mandatory hooks**
✅ **Use Claude Code's settings.json hook infrastructure**
✅ **Fail-fast error handling (abort on errors)**
✅ **250ms performance target for hooks**
✅ **Automated migration tool available**

**Migration Timeline**:

- **Phase 1**: Foundation (hooks registry, core hooks) - 1h 30min
- **Phase 2**: Pilot skills (3 skills) - 2h
- **Phase 3**: All remaining skills (14 skills) - 4h 30min
- **Phase 4**: Monitoring hooks (all skills) - 4h

**Total Estimated Migration Time**: 12-14h for all 17 skills

---

**Last Updated**: 2026-05-05
**Guide Version**: 1.0.0
**Plan Status**: Active - See `.claude/plans/260505-1011-hooks-strategy/plan.md`
