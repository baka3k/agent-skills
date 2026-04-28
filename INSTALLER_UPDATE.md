# Installer Updates - Default Behavior Changed

## 🎯 New Behavior (2025-04-13)

### Old Behavior
```bash
./scripts/install.sh              # Error: agent required
./scripts/install.sh --list       # Show list
./scripts/install.sh --interactive # Show menu
```

### New Behavior
```bash
./scripts/install.sh              # ✅ Show list + prompt to select
./scripts/install.sh --list       # Show list and exit
./scripts/install.sh --agent X    # Auto mode: skip list
```

## 📋 Usage Modes

### Mode 1: Default Interactive (Recommended)
```bash
./scripts/install.sh
```

**Behavior:**
1. Shows header: "Agent Skills Kit Installer"
2. Shows mode: "Interactive (select from list)"
3. **Automatically displays** list of 5 supported agents
4. Prompts: "Select agent (1-5): "
5. For Cursor: asks "Install globally or locally? [G/l]:"
6. Shows installation plan
7. Prompts for confirmation
8. Installs skills

**Output:**
```
============================================
Agent Skills Kit Installer
============================================

Mode: Interactive (select from list)

============================================
Supported AI Agents
============================================

1. Claude Code (claude-code)
   Global: ~/.claude/skills/
2. Cursor AI (cursor)
   ...
```

### Mode 2: Auto Mode (Direct Command)
```bash
./scripts/install.sh --agent claude-code
./scripts/install.sh --agent cursor --scope global
./scripts/install.sh --agent codex --dry-run
```

**Behavior:**
1. Shows header: "Agent Skills Kit Installer"
2. Shows mode: "Auto (agent specified)"
3. Shows agent name
4. **Skips list display**
5. Goes directly to installation plan
6. Prompts for confirmation (unless --dry-run)
7. Installs skills

**Output:**
```
============================================
Agent Skills Kit Installer
============================================

Mode: Auto (agent specified)
Agent: Claude Code
============================================
Installation Plan
============================================
Agent: Claude Code
Scope: local
Install path: /Users/user/.claude/skills
Skills to install: 6
```

### Mode 3: List Only
```bash
./scripts/install.sh --list
./scripts/install.sh -l
```

**Behavior:**
1. Shows list of supported agents
2. **Exits immediately** (no installation)

## 🔧 Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| (none) | Interactive: show list and select | `./scripts/install.sh` |
| `--agent AGENT` | Auto mode: install for specific agent | `--agent claude-code` |
| `--scope SCOPE` | Installation scope (global/local) | `--scope global` |
| `--dry-run` | Preview installation without installing | `--dry-run` |
| `--list, -l` | List supported agents and exit | `--list` |
| `--help, -h` | Show help message | `--help` |

## 📊 Supported Agents

| # | Agent | ID | Install Path | Scope |
|---|-------|----|--------------|-------|
| 1 | Claude Code | `claude-code` | `~/.claude/skills/` | Global only |
| 2 | Cursor AI | `cursor` | `~/.cursorrules` or `.cursorrules` | Both |
| 3 | Continue.dev | `continue` | `~/.continue/skills/` | Global only |
| 4 | GitHub Copilot | `copilot` | `.github/copilot-instructions.md` | Local only |
| 5 | OpenAI CodeX | `codex` | `.openai/codex-instructions.md` | Local only |

## 🎨 User Experience Comparison

### Before (Old Script)
```bash
$ ./scripts/install.sh
Error: Agent is required (use --agent or --interactive)

$ ./scripts/install.sh --list
[Shows list]

$ ./scripts/install.sh --interactive
[Shows menu]
```

### After (New Script)
```bash
$ ./scripts/install.sh
============================================
Agent Skills Kit Installer
============================================

Mode: Interactive (select from list)

[Shows full list of 5 agents]

Select agent (1-5): _
```

## ✅ Benefits

1. **More intuitive**: Default behavior is helpful, not error
2. **Always informative**: Shows what's available
3. **Faster workflow**: No need to remember --interactive flag
4. **Backward compatible**: All existing commands still work
5. **Clear feedback**: Shows current mode (Auto vs Interactive)

## 🧪 Test Cases

### Test 1: Default (No arguments)
```bash
./scripts/install.sh
# Expected: Show list + prompt
# ✅ PASS
```

### Test 2: List only
```bash
./scripts/install.sh --list
# Expected: Show list + exit
# ✅ PASS
```

### Test 3: Auto mode
```bash
./scripts/install.sh --agent claude-code --dry-run
# Expected: Skip list, show plan
# ✅ PASS
```

### Test 4: Auto with scope
```bash
./scripts/install.sh --agent cursor --scope global --dry-run
# Expected: Skip list, use global scope
# ✅ PASS
```

### Test 5: Help
```bash
./scripts/install.sh --help
# Expected: Show usage
# ✅ PASS
```

## 📝 Migration Notes

### For Users

**Old way still works:**
```bash
./scripts/install.sh --agent claude-code  # Still works
./scripts/install.sh --list              # Still works
```

**New simpler way:**
```bash
./scripts/install.sh  # Now shows list automatically!
```

### For Documentation

Update examples from:
```bash
./scripts/install.sh --interactive  # Old
```

To:
```bash
./scripts/install.sh  # New (default behavior)
```

## 🚀 Future Enhancements

Possible improvements:
- [ ] Add `--quiet` flag to skip confirmations
- [ ] Add `--yes` flag to auto-confirm
- [ ] Add `--all` flag to install for all platforms
- [ ] Add `--uninstall` flag to remove installed skills
- [ ] Add update check for newer skill versions

---

**Updated**: 2025-04-13
**Version**: 1.1.0
**Status**: Production Ready ✅
