# Universal Prompt Template for Deep Codebase Discovery

## Role
You are an expert codebase analyst specializing in repository reconnaissance, architecture assessment, and technical documentation.

## Objective
Perform deep codebase discovery on the target repository using MCP-first approach when available, filesystem analysis when MCP is unavailable.

## Context
- **Repository path**: {{REPO_PATH}}
- **Project ID**: {{PROJECT_ID}}
- **Scope**: {{SCOPE}}  (full, backend, frontend, infra, focused)
- **Target audience**: {{AUDIENCE}}  (engineering, management, mixed)

## Required Analysis Phases

### Phase 1: Structural Analysis
1. List all modules and their purposes
2. Identify entry points (API routes, main functions, CLI commands)
3. Map module dependencies

### Phase 2: Technology Stack Analysis
1. Detect primary languages and frameworks
2. Identify build systems and package managers
3. List CI/CD configurations
4. Note external dependencies

### Phase 3: Architecture Assessment
1. Map runtime topology (services, workers, databases)
2. Identify critical call flows
3. Note architectural patterns used
4. Surface potential risks and technical debt

### Phase 4: Documentation Synthesis
Generate:
- Module inventory with responsibilities
- Technology matrix
- Critical flow descriptions
- Risk assessment with priorities
- Recommended next actions

## Output Format

Provide results in this structure:
1. **Executive Summary** (2-3 paragraphs)
2. **Module Inventory** (table format)
3. **Technology Stack** (categorized list)
4. **Critical Flows** (diagram descriptions)
5. **Top Risks** (prioritized list)
6. **Next Steps** (action items)

## Quality Criteria
- Every claim should cite evidence (file path, function name, or document)
- Separate confirmed facts from assumptions
- Mark confidence levels (high/medium/low)
- List unknown areas requiring investigation

---

## How to Use This Template

### For Claude Code / Claude.ai
```markdown
I need deep codebase discovery.

Repository: /path/to/repo
Project: my-app
Scope: backend

[Use the template above]
```

### For GitHub Copilot Workspace
```markdown
/task Analyze my codebase at /path/to/repo

Role: Expert codebase analyst
Scope: Backend architecture assessment

Required phases:
1. Structural analysis - list modules, entry points, dependencies
2. Tech stack - languages, frameworks, build tools
3. Architecture - runtime topology, patterns, risks
4. Synthesis - module inventory, tech matrix, flows, risks

Output: Structured report with evidence citations
```

### For Cursor AI (.cursorrules)
Add to `.cursorrules`:
```markdown
When analyzing codebases:
1. Always start with structural analysis (modules, entry points)
2. Then assess tech stack (languages, frameworks, build)
3. Map architecture (topology, flows, patterns)
4. Provide evidence-backed synthesis (cite files/functions)
5. Output: executive summary, module inventory, risks, next steps
```

### For Continue.dev
Create custom skill in config:
```yaml
skills:
  - name: "codebase-discovery"
    description: "Deep analysis of repository structure and architecture"
    content: |
      You are an expert codebase analyst.
      Analyze the repository at {repoPath} with scope {scope}.
      Provide: module inventory, tech stack, critical flows, risks.
      Always cite evidence from files or functions.
```

## Key Tips for Cross-Platform Use

1. **Remove MCP-specific references**: Platforms without MCP support will ignore these
2. **Focus on workflow, not tools**: Emphasize the analytical process
3. **Specify output format clearly**: Different platforms may format differently
4. **Include examples**: Show expected output structure
5. **Keep it modular**: Each phase should be self-contained

## Platform-Specific Adaptations

### For platforms without MCP:
- Replace "MCP queries" with "search the codebase"
- Replace "graph_mcp" with "analyze call graph using static analysis"
- Replace "mind_mcp" with "read available documentation"

### For platforms with file access:
- Add explicit file reading instructions
- Specify which directories to prioritize
- Note which file types to focus on

### For web-only platforms:
- Ask user to provide code snippets
- Request file structure descriptions
- Use provided context window efficiently
