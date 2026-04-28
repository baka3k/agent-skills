# Source Priority and Conflict Rules

Use this policy when evidence is incomplete or contradictory.

## Provenance & Confidence Rules

When stating confidence levels, include provenance:

```markdown
Confidence: high
- Source agreement: graph_mcp + git blame both confirm X changed in commit ABC
- Evidence strength: Strong (multiple independent sources)
- Coverage: Complete (all relevant sources agree)

Confidence: medium
- Source agreement: mind_mcp suggests X, but git history is unclear
- Evidence strength: Medium (one strong source + weak corroboration)
- Coverage: Partial (some sources unavailable)

Confidence: low
- Source agreement: Only memory files mention X, no code evidence
- Evidence strength: Weak (single source, no corroboration)
- Coverage: Incomplete (key sources unavailable)
```

## Priority by Question Type

## Structure/Runtime Questions

Priority order:
1. `graph_mcp`
2. Git code history
3. `mind_mcp`
4. memory files

## Historical Rationale Questions

Priority order:
1. `mind_mcp`
2. memory files
3. Git code history
4. `graph_mcp`

## Conflict Handling

When top-priority sources disagree:

1. Mark as `conflict`.
2. Show both pieces of evidence with citations.
3. Provide one concrete verification step.
4. Avoid final root-cause statements until conflict is resolved.

## Confidence Scoring (Simple)

- `high`: two or more strong sources agree.
- `medium`: one strong source + one weak source, no contradiction.
- `low`: weak sources only or unresolved contradiction.
