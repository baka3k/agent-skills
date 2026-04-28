# Knows Retrieval Playbook

Use this playbook to select the fastest high-confidence retrieval path by intent.

## 1) Preflight Checklist

- Confirm repo root and branch.
- Confirm question intent:
  - `why-changed`
  - `impact-analysis`
  - `architecture-context`
  - `history-trace`
- Extract search seeds: symbol names, paths, endpoint, commit id, issue id.
- **Validate inputs**: sanitize paths, limit query length, check for dangerous patterns

## 1.1) Input Validation

Before any retrieval, validate user input:

```python
# Path validation
- Block path traversal: "../", "..\\"
- Limit path length: 500 chars
- Whitelist allowed chars: alphanumeric, "/", "-", "_", ".", ":", "#"

# Query validation
- Limit query length: 1000 chars
- Sanitize special chars: escape ";", "|", "&", "$"
- Block SQL/NoSQL injection patterns

# Scope validation
- Verify file path exists in workspace
- Check symbol/module name is non-empty
- Validate commit hash format (if provided): /^[a-f0-9]{7,40}$/
```

## 2) Git-first Commands

Use minimal commands first, then expand scope.

```bash
rg -n "keyword|SymbolName" .
git log --oneline --decorate -- <path>
git blame -L <start>,<end> <file>
git show <commit>
```

Evidence to capture:
- `file path`
- `commit hash`
- `author/date`
- short reason from commit message and diff

## 3) mind_mcp Strategy

Use for historical/domain rationale:
- decision history
- requirement traces
- architecture intent

**Timeout:** 30s per call, with partial result return on timeout.

Suggested sequence:
1. `hybrid_search` for broad context.
2. `query_graph_rag_relation` when entity links are needed.
3. `sequential_search` for step-based procedures and numbered flows.

**Caching:** Cache results by (query_type, params) for 10min.

## 4) graph_mcp Strategy

Use for code structure and impact:
- call graph
- module boundaries
- workflow impact

**Timeout:** 30s per call, with partial result return on timeout.

Suggested sequence:
1. `explore_graph` for entry points.
2. `query_subgraph` or `find_paths` for focused traversals.
3. `analyze_workflow_impact` for risk scope when available.

**Caching:** Cache results by (query_type, params) for 10min.

**Batch optimization:** Prefer single batch calls over multiple small calls:
- Use `query_subgraph` with multiple nodes vs multiple `explore_graph` calls
- Use `find_paths` with multiple targets vs multiple single-target calls

## 5) Channel Fallback & Degraded Modes

### Timeout Handling
- On timeout (30s): Return partial results + log timeout + continue with fallback
- Total workflow timeout (5min): Synthesize available evidence + notify user of incomplete retrieval

### Degraded Modes

**Mode A: mind_mcp unavailable**
- Fallback: Git + graph_mcp + memory files
- Confidence: downgrade to `medium`
- Label: "⚠️ Degraded: mind_mcp unavailable - historical context may be incomplete"

**Mode B: graph_mcp unavailable**
- Fallback: Git + mind_mcp + memory files
- Confidence: downgrade to `medium`
- Impact analysis: mark as "incomplete - code structure limited to Git + static analysis"
- Label: "⚠️ Degraded: graph_mcp unavailable - dependency analysis limited"

**Mode C: Both MCP unavailable**
- Fallback: Git + memory files only
- Confidence: downgrade to `low`
- Scope: Provide git history + file-based context only
- Label: "⚠️ Degraded: MCP unavailable - Git + file context only"

### User Notification
Always include in output when in degraded mode:
1. Which channels failed
2. What evidence is missing/limited
3. Confidence downgrade reason
4. Suggested manual verification steps

## 6) Observability & Metrics

### Performance Metrics (to log)

```
knows.workflow.duration_ms: total workflow time
knows.git.duration_ms: git retrieval time
knows.mind_mcp.duration_ms: mind_mcp call time
knows.graph_mcp.duration_ms: graph_mcp call time
knows.memory.duration_ms: memory file retrieval time
knows.synthesis.duration_ms: evidence synthesis time

knows.mcp.cache_hits: number of cached MCP results returned
knows.mcp.cache_misses: number of uncached MCP calls
knows.mcp.timeouts: number of MCP timeouts
knows.mcp.errors: number of MCP errors

knows.confidence.level: final confidence (high/medium/low)
knows.degraded_mode: whether operating in degraded mode (true/false)
```

### Audit Logging (with redaction)

Log these events with sensitive data redacted:
- Workflow start/end with intent classification
- MCP calls made (function name, params summary)
- Cache hits/misses
- Timeout/error events
- Degraded mode activations
- Confidence scores with provenance breakdown

**Redaction patterns:**
- API keys: `/\b[A-Za-z0-9]{32,}\b/g` → `[REDACTED]`
- Passwords: `/password.*/gi` → `[REDACTED]`
- Tokens: `/token.*/gi` → `[REDACTED]`
- PII: emails, phones, SSN patterns → `[REDACTED]`

### Progress Feedback

For long-running operations (>10s), provide progress updates:
- "Phase 1/3: Retrieving git history..."
- "Phase 2/3: Querying code structure..."
- "Phase 3/3: Synthesizing evidence..."
