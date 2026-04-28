# Knows Memory Source Policy

Workspace-first policy with controlled expansion to home paths.

## Input Validation Rules

Before reading any memory files, validate user input:

```python
# Path validation
- Block path traversal: "../", "..\\"
- Limit path length: 500 chars
- Whitelist allowed chars: alphanumeric, "/", "-", "_", ".", ":", "#"
- Verify path exists in workspace or home

# Filename validation
- Enforce allowlist: memory*.md, agent*.md, claude*.md, cursor*.md
- Reject patterns: "*.exe", "*.dll", "*.so", "*.dylib", "*.bin"
- Limit filename length: 100 chars

# Query validation
- Limit query length: 1000 chars
- Sanitize special chars: escape ";", "|", "&", "$"
- Block command injection patterns

# Scope validation
- Max files per request: 10
- Max file size: 300KB
- Max total read size: 1MB per request
```

## Source Priority

1. Workspace/repository local files
2. Workspace hidden config dirs (for example `.claude/`, `.cursor/`)
3. Standard home-level locations (only if nothing relevant in workspace)

## Allowlist Filenames

Only read files that match:

- `memory*.md`
- `agent*.md`
- `claude*.md`
- `cursor*.md`

## Suggested Search Locations

Workspace-first:

- `<repo>/**/memory*.md`
- `<repo>/**/agent*.md`
- `<repo>/.claude/**/*.md`
- `<repo>/.cursor/**/*.md`

Home fallback:

- `~/.claude/**/*.md`
- `~/.cursor/**/*.md`
- `~/.config/claude/**/*.md`
- `~/.config/cursor/**/*.md`

## Read Limits

- Max file size: 300KB
- Max files per request: 10
- Prioritize by modified time (newest first)

## Sanitization

- Redact secrets/tokens before citing.
- Do not include long verbatim excerpts.
- Prefer short summary + path citation.
