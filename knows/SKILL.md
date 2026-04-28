---
name: knows
description: Unified knowledge retrieval skill that answers with evidence by prioritizing git context, then mind_mcp/graph_mcp, then memory files (memory.md, agent.md, claude/cursor notes). Use when users ask why a change happened, what impacts a function/screen, or need traceable technical context before decisions.
version: 1.0.0
last_updated: 2026-04-26
---

# Knows

Build a traceable answer from multiple evidence sources in a strict order:
1) Git context
2) MCP context (`mind_mcp`, `graph_mcp`)
3) Memory files (`memory*.md`, `agent*.md`, `claude*.md`, `cursor*.md`)

Then synthesize with confidence and explicit uncertainties.

## When To Use

- User asks why behavior or logic changed.
- User asks impact radius of a function/screen/API.
- User needs architecture or decision context with citations.
- Existing answer quality depends on combining code history + graph + notes.

## Avoid Using When

- User only needs a quick syntax fix with no context tracing.
- Task is pure implementation and no historical/contextual rationale is needed.
- Request requires direct database mutations or admin operations.

## Required Inputs

- User question.
- Repository root path (default: current workspace).
- Optional focus hints: file path, symbol, endpoint, issue/PR id, commit hash.

## Operational Defaults (v1)

- Mode: design + scaffold workflow.
- Neo4j mode: suggest query only, do not run direct database queries.
- Memory policy: workspace/repo first, then standard home locations.
- Reliability over speed: prefer verifiable evidence over fast guesses.
- **Timeout: 30s per MCP call, 5min total workflow.**
- **Caching: memoize MCP results with same params for 10min.**

## Terminology

- **Git context**: Source code history from git commands (log, blame, show)
- **mind_mcp**: Knowledge graph MCP for historical/domain intent and design rationale
- **graph_mcp**: Code structure MCP for runtime dependencies and call graphs
- **Memory files**: Workspace and home-level markdown files (memory*.md, agent*.md, claude*.md, cursor*.md)

## Known Limitations

- Cannot execute direct Neo4j queries in v1 (suggest-only mode)
- Partial MCP failures may downgrade confidence without degraded UI indicator
- Cache invalidation is time-based (10min), not content-aware
- Large repositories (>100K files) may exceed retrieval timeouts

## Orchestration Workflow

### Phase A - Preflight

- Confirm repository root and active branch.
- Classify intent: `why-changed`, `impact-analysis`, `architecture-context`, `history-trace`.
- Check available retrieval channels:
  - Git CLI access
  - `mind_mcp`
  - `graph_mcp`
- Define scope and search seed (symbol/path/endpoint keywords).

### Phase B - Git-first Retrieval

- Use `rg` for code/text anchor discovery.
- Use git history commands to reconstruct timeline:
  - `git log -- <path>`
  - `git blame <file>`
  - `git show <commit>`
- Extract evidence with minimal but concrete citations:
  - file path, commit hash, author/time, key diff intent.

Detailed command patterns: `references/retrieval-playbook.md`.

### Phase C - MCP Retrieval

- Query `mind_mcp` for historical/domain intent and design rationale.
- Query `graph_mcp` for runtime structure and dependency/workflow impact.
- Choose tool strategy by intent:
  - impact: graph traversal and workflow expansion first
  - rationale: historical/context retrieval first
  - architecture: hybrid evidence from both

Fallback rule:
- If MCP channels are unavailable, continue with Git + memory evidence and downgrade confidence.

### Phase D - Memory-file Retrieval (Workspace First)

- Search workspace first, then standard home locations.
- Enforce allowlist filename patterns:
  - `memory*.md`
  - `agent*.md`
  - `claude*.md`
  - `cursor*.md`
- Apply read limits:
  - max file size: 300KB
  - max files per query: 10
  - prioritize newest modified files first

Detailed policy: `references/memory-source-policy.md`.

### Phase E - Synthesis

- Merge evidence by source priority and confidence.
- Separate:
  - confirmed facts
  - inferred conclusions
  - unresolved conflicts
- If deep graph detail is missing, emit `Neo4j Query Suggestion` with:
  - suggested Cypher
  - why this query helps
  - expected result shape

Template: `references/neo4j-query-suggestion-template.md`.

## Output Contract

Always structure answers with these sections:

1. `Kết luận ngắn`
2. `Độ tin cậy và nguồn`
   - Confidence level: high/medium/low
   - Provenance: which sources agree/disagree
   - Coverage: complete/partial/incomplete
   - Degraded mode warning (if applicable)
3. `Bằng chứng theo nguồn`
   - Git (commit hash, file, author/date)
   - mind_mcp (query type, result summary)
   - graph_mcp (query type, result summary)
   - memory files (file path, key excerpt)
4. `Điểm chưa chắc chắn`
5. `Neo4j Query Suggestion` (only when needed)

### Degraded Mode Output Format

When operating in degraded mode, include:

```markdown
⚠️ Degraded Mode: {mode_type}
- Unavailable channels: {list failed MCP channels}
- Missing evidence: {what's limited/missing}
- Confidence impact: {why confidence is downgraded}
- Manual verification suggested: {specific steps}
```

## Conflict Resolution Rules

- Current code structure/runtime facts: prioritize `graph_mcp` + Git.
- Historical rationale/intent: prioritize `mind_mcp` + memory files.
- If conflict remains unresolved:
  - label explicitly as `conflict`
  - provide next verification step
  - do not force a final root-cause claim.

Detailed rules: `references/source-priority-and-conflict.md`.

## Guardrails

- Never expose secrets/tokens from evidence.
- Do not claim root cause from a single weak source.
- Every high-impact claim must include at least one concrete citation.
- Do not execute direct Neo4j queries in v1.
- Do not modify repository state during retrieval/synthesis.

## Security & Privacy

### Input Validation
- Validate all user input before retrieval (paths, queries, symbols)
- Block path traversal: `../`, `..\\`
- Limit query length: 1000 chars
- Sanitize special characters: `;`, `|`, `&`, `$`
- Whitelist allowed file patterns

### Sensitive Data Redaction
- Redact API keys: `/\b[A-Za-z0-9]{32,}\b/g` → `[REDACTED]`
- Redact passwords: `/password.*/gi` → `[REDACTED]`
- Redact tokens: `/token.*/gi` → `[REDACTED]`
- Redact PII: emails, phones, SSN patterns → `[REDACTED]`
- Never log or cite unredacted secrets

### Access Boundaries
- Limit file size: 300KB per file
- Limit files per query: 10 files
- Limit total read size: 1MB per request
- Workspace-first policy: only read home paths if workspace is empty

## Performance & UX

### Timeout Handling
- Per MCP call: 30s timeout with partial result return
- Total workflow: 5min timeout with synthesis of available evidence
- On timeout: Log + continue with fallback + notify user

### Caching Strategy
- Cache MCP results by (function, params) for 10min
- Cache invalidation: Time-based (10min TTL)
- Prefer batch calls over multiple small calls
- Log cache hits/misses for observability

### Progress Feedback
For workflows >10s, provide progress updates:
- "Phase 1/4: Retrieving git history..."
- "Phase 2/4: Querying code structure..."
- "Phase 3/4: Reading memory files..."
- "Phase 4/4: Synthesizing evidence..."

## Observability

### Metrics to Track
- Workflow duration breakdown (git, MCP, memory, synthesis)
- MCP performance: calls, timeouts, errors, cache hit rate
- Confidence distribution: high/medium/low
- Degraded mode frequency

### Audit Logging
Log these events (with redaction):
- Workflow start/end with intent classification
- MCP calls (function name, params summary)
- Cache hits/misses
- Timeout/error events
- Degraded mode activations
- Confidence scores with provenance

## Validation Scenarios

1. Why logic X changed
   - Must include commit/blame evidence.
   - If memory notes exist, link rationale to timeline.
2. Impact of function/screen Y
   - Must include upstream/downstream graph evidence.
   - Must separate facts from assumptions.
3. MCP unavailable
   - Must fallback to Git + memory.
   - Must downgrade confidence explicitly.
   - Must label degraded mode with specific missing evidence.
4. MCP timeout
   - Must return partial results + continue with fallback.
   - Must log timeout event.
   - Must notify user of incomplete retrieval.
5. Deep graph detail missing
   - Must output a relevant Neo4j query suggestion.
   - Must not execute direct query.
6. Conflicting evidence
   - Must label conflict and next verification action.
   - Must not guess final conclusion.
7. Large repository (timeout risk)
   - Must use progressive retrieval: start focused, expand if needed.
   - Must provide progress updates for long operations.
   - Must respect 5min total workflow timeout.
8. Cache hit
   - Must return cached result within 10min TTL.
   - Must log cache hit for observability.
   - Must invalidate cache on workflow start.

## Progressive Disclosure

Load only what is needed:

- Retrieval playbook: `references/retrieval-playbook.md`
- Memory policy: `references/memory-source-policy.md`
- Conflict rules: `references/source-priority-and-conflict.md`
- Neo4j suggestion templates: `references/neo4j-query-suggestion-template.md`
