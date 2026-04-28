# Cross-Platform Skill Usage Guide

Sử dụng các agent skills này với Claude Code, GitHub Copilot, Cursor AI, OpenAI, và platforms khác.

## 🎯 Quick Start

### Với Claude Code (Native support)
```bash
# Direct use via /skill command
/skill deep-codebase-discovery

# Or specify repo directly
/skill repo-recon /path/to/repo --scope backend
```

### Với GitHub Copilot Workspace
```markdown
# Copilot đọc nhiều skill từ .github/skills/
# Chọn rõ skill cần dùng trong prompt để tránh nhầm ngữ cảnh
/task Use skill deep-codebase-discovery from .github/skills for this repository.

# Hoặc:
/task Use skill bug-impact-analyzer from .github/skills for this production bug report.
```

### Với Cursor AI
```bash
# Add to .cursorrules in project root
cat > .cursorrules << 'EOF'
# Codebase Analysis Rules

When analyzing codebase:
1. Start with structural analysis (modules, entry points)
2. Then tech stack (languages, frameworks, build)
3. Map architecture (topology, flows, patterns)
4. Provide evidence-backed synthesis
5. Output: summary, inventory, risks, next steps

Always cite evidence from files/functions.
Separate facts from assumptions.
EOF

# Then just ask Cursor normally
"Analyze my codebase structure"
```

### Với Continue.dev
```yaml
# Add to ~/.continue/config.json
{
  "skills": [
    {
      "name": "codebase-discovery",
      "description": "Deep repository analysis and architecture assessment",
      "content": "You are an expert codebase analyst. Analyze the repository at {repoPath} with scope {scope}. Provide: module inventory, tech stack, critical flows, risks. Always cite evidence from files or functions."
    },
    {
      "name": "repo-recon",
      "description": "Structural repository reconnaissance",
      "content": "Build structural understanding: list modules, entry points, dependencies. Use documentation first, code analysis second. Cite all evidence sources."
    },
    {
      "name": "tech-build-audit",
      "description": "Technology stack and build system analysis",
      "content": "Detect: languages, frameworks, build tools, CI/CD, dependencies. Identify API boundary violations. Provide technology matrix with evidence."
    }
  ]
}
```

### Với OpenAI ChatGPT/CodeX
```markdown
I need deep codebase analysis. Please:

## Role
Expert codebase analyst and architect

## Task
Analyze my repository and provide:
1. Module inventory with responsibilities
2. Technology stack matrix
3. Critical call flows
4. Risk assessment with priorities
5. Recommended next actions

## Workflow
1. Read available documentation first
2. Analyze code structure second
3. Synthesize findings into report

## Output Format
- Executive summary (2-3 paragraphs)
- Module table with evidence citations
- Tech stack categorized by layer
- Critical flows with descriptions
- Risks prioritized by impact

Repository: [paste structure or zip]
Always cite file paths and function names as evidence.
```

## 📦 Batch Conversion

Use the converter script to convert all skills at once:

```bash
# Convert all skills for GitHub Copilot
python scripts/convert_skill.py --all --format copilot --output ./converted/copilot

# Convert all skills for Cursor AI
python scripts/convert_skill.py --all --format cursor --output ./converted/cursor

# Convert all skills for Continue.dev
python scripts/convert_skill.py --all --format continue --output ./converted/continue

# Convert single skill
python scripts/convert_skill.py --skill deep-codebase-discovery --format openai
```

## 🔄 Platform-Specific Adaptations

### Platforms WITHOUT MCP (Copilot, Cursor, OpenAI)

Replace MCP-specific terms:
- ❌ "mind_mcp" → ✅ "read documentation files"
- ❌ "graph_mcp" → ✅ "analyze code structure"
- ❌ "list_up_entrypoint" → ✅ "find entry points by searching for main functions, API routes, CLI commands"
- ❌ "trace_flow" → ✅ "trace function calls manually"

### Platforms WITH file access (Claude Code, Cursor)

Add file context:
```markdown
Repository structure:
[optional: paste `tree` output]

Key files to analyze:
- README.md, docs/**/*
- package.json, pom.xml, build.gradle
- src/main/**/*, app/**/*
```

### Web-only platforms (ChatGPT, Claude.ai)

Request user input:
```markdown
To analyze your codebase, please provide:
1. Repository structure (directory tree)
2. Key files content (README, main entry points)
3. Build configuration files
4. Any existing documentation

Or provide a GitHub/GitLab URL if accessible.
```

## 📋 Quick Reference Matrix

| Task | Claude Code | Copilot | Cursor | Continue | OpenAI |
|------|-------------|---------|--------|----------|--------|
| **Codebase discovery** | `/skill deep-codebase-discovery` | `/task analyze repo` | Auto via .cursorrules | `/skill codebase-discovery` | Paste template |
| **Structural analysis** | `/skill repo-recon` | `/task map structure` | Auto via .cursorrules | `/skill repo-recon` | Paste template |
| **Tech stack audit** | `/skill tech-build-audit` | `/task detect stack` | Auto via .cursorrules | `/skill tech-build-audit` | Paste template |
| **Doc generation** | `/skill reverse-doc-reconstruction` | `/task generate docs` | Auto via .cursorrules | Custom skill | Paste template |
| **Bug impact analysis** | `/skill bug-impact-analyzer` | `/task analyze bug` | Auto via .cursorrules | `/skill bug-impact` | Paste template |

## 🎨 Tips for Best Results

### 1. Provide Context
```markdown
## Context
- Repository: /path/to/repo or GitHub URL
- Language: Java/Python/TypeScript/etc.
- Scope: backend/frontend/full
- Audience: engineering/management
```

### 2. Specify Output Format
```markdown
## Expected Output
- Markdown report with sections
- Tables for module inventory
- Code blocks for examples
- Diagrams in Mermaid format (if supported)
```

### 3. Set Quality Criteria
```markdown
## Quality Requirements
- Every claim must cite evidence
- Separate facts from assumptions
- Mark confidence levels
- List unknown areas explicitly
```

### 4. Iterate and Refine
```markdown
# First pass: High-level analysis
"Give me executive summary and module list"

# Second pass: Deep dive specific areas
"Analyze the payment module in detail"

# Third pass: Validate findings
"Verify these claims against the actual code"
```

## 🚀 Advanced Usage

### Chaining Multiple Skills
```markdown
# With Claude Code
/skill repo-recon /path/to/repo
/skill tech-build-audit /path/to/repo
/skill module-summary-report /path/to/repo

# With other platforms (manual)
Step 1: Run structural analysis
Step 2: Run tech stack analysis
Step 3: Synthesize into summary report
```

### Customizing for Your Stack
```markdown
# Add to prompt:
## Custom Context
- My project uses: Spring Boot, React, PostgreSQL
- Build tool: Maven
- CI/CD: GitHub Actions
- Focus areas: authentication, payment processing
```

### Integrating with Existing Workflows
```bash
# Pre-commit hook for documentation
#!/bin/bash
python scripts/convert_skill.py --skill reverse-doc-reconstruction --format claude
# Run Claude Code to generate docs from code changes

# CI/CD integration
python scripts/convert_skill.py --all --format continue
# Use Continue.dev in pipeline for automated analysis
```

## 📚 Resources

- **Universal template**: `template/prompt-templates/cross-platform-skill-template.md`
- **Converter script**: `scripts/convert_skill.py`
- **Original skills**: `*/SKILL.md` files
- **Playbooks**: `*/references/*.md` for detailed workflows

## 🤝 Contributing

To add support for new platforms:
1. Update `scripts/convert_skill.py` with new format converter
2. Add example to this guide
3. Test with actual platform
4. Submit PR

---

**Last updated**: 2026-04-14
**Compatible with**: Claude Code, GitHub Copilot, Cursor AI, Continue.dev, OpenAI ChatGPT/CodeX
