# Memory Source Policy

## Allowlist
- `memory*.md`, `agent*.md`, `cla(x)ude*.md`, `cursor*.md`
- Block: `*.exe`, `*.dll`, `*.so`, `*.dylib`

## Locations (workspace first)
```
<repo>/**/{memory,agent,claude,cursor}*.md
~/.claude/**/*.md
~/.cursor/**/*.md
~/.config/{claude,cursor}/**/*.md
```

## Limits
- Max file size: 300KB
- Max files: 10
- Max total read: 1MB
- Sort: newest first
