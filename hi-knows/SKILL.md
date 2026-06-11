---
name: knows
description: Unified knowledge retrieval skill. Build traceable answers from git, MCP, and memory files.
version: 2.0.0
last_updated: 2026-05-28
---

# Knows

Answer with evidence using sources in strict order: **Git → MCP (mind/graph) → Memory files**

## When To Use

- Why behavior/logic changed (git blame + commit history)
- Impact radius of function/screen/API (graph_mcp traversal)
- Architecture/decisions context (mind_mcp + memory files)
- NOT for: quick syntax fixes, pure implementation, DB mutations

## Evidence Priority

| Question Type | Priority Order |
|---------------|----------------|
| Structure/Runtime | graph_mcp → Git → mind_mcp → memory |
| Historical/Rationale | mind_mcp → memory → Git → graph_mcp |

## Workflow

**Phase 1 - Preflight:** Classify intent (`why-changed`, `impact-analysis`, `architecture-context`, `history-trace`)

**Phase 2 - Git:**
```bash
rg -n "keyword" .
git log --oneline --decorate -- <path>
git blame -L <start>,<end> <file>
git show <commit>
```

**Phase 3 - MCP:**
- `mind_mcp`: `hybrid_search`, `query_graph_rag_relation`, `sequential_search`
- `graph_mcp`: `explore_graph`, `query_subgraph`, `find_paths`, `analyze_workflow_impact`

**Phase 4 - Memory:** Workspace-first, then home. Allowlist: `memory*.md`, `agent*.md`, `claude*.md`, `cursor*.md`

**Phase 5 - Synthesis:** Merge by priority. Separate facts/inferences/conflicts.

## Output Format

```markdown
## Kết luận ngắn

## Độ tin cậy
- Confidence: high/medium/low
- Nguồn: list sources used

## Bằng chứng
- Git: file, commit, author
- MCP: query type + summary
- Memory: file + excerpt

## Điểm chưa chắc chắn

## Neo4j Query Suggestion (optional)
```

## Guardrails

- Never claim from single weak source
- Every high-impact claim needs citation
- Do not execute direct Neo4j queries
- Redact secrets before citing

## Limits

- MCP timeout: 30s/call, 5min total
- File size: 300KB max
- Files/query: 10 max
- Cache TTL: 10min

## Degraded Mode

```markdown
⚠️ Degraded Mode: {reason}
- Unavailable: {failed channels}
- Missing: {limited evidence}
- Confidence: {downgraded reason}
```