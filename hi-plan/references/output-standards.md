# Output Standards

## plan.md YAML Frontmatter (Required)
```yaml
title: "Brief plan title"
description: "One-sentence summary"
status: pending
priority: P2     # P1 | P2 | P3
effort: 4h
issue: 74
branch: kai/feat/feature-name
tags: [frontend, api]
blockedBy: []
blocks: []
created: 2025-12-16
```

### Auto-Population
title: from task | description: first sentence of Overview | status: always pending
priority: user or P2 | effort: sum phases | issue: from branch | branch: git branch --show-current
tags: infer from keywords | blockedBy/blocks: pre-creation scan | created: today YYYY-MM-DD

### Tag Vocabulary
Type: feature, bugfix, refactor, docs, infra
Domain: frontend, backend, database, api, auth
Scope: critical, tech-debt, experimental

## Task Naming
subject (imperative, <60 chars): "Setup database migrations"
activeForm (continuous): "Setting up database"
description: 1-2 sentences, concrete deliverables, reference phase file

## Writing Style
Sacrifice grammar for concision. Focus clarity over eloquence. Use bullets and lists. Short sentences. Prioritize actionable info.

## Output Requirements
- Plans ONLY, no implementation
- Self-contained with necessary context
- Code snippets/pseudocode when clarifying
- Multiple options with trade-offs when appropriate
- Unresolved questions: AskUserQuestion, then revise based on answers
- Fully respect ./docs/development-rules.md

## Quality
- Thorough: edge cases, failure modes, assumptions documented
- Maintainable: decision rationale, avoid over-engineering, YAGNI/KISS/DRY
- Research depth: multiple options, validated against best practices
- Security & performance: OWASP, bottlenecks, scalability, resource constraints
- Implementable: enough detail for junior devs, validate against existing patterns
