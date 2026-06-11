# Retrieval Playbook

## Validation
- Block path traversal: `../`, `..\\`
- Query length: 1000 chars max
- Sanitize: `;`, `|`, `&`, `$`
- Validate commit hash: `/^[a-f0-9]{7,40}$/`

## Git Commands
```bash
rg -n "keyword" .
git log --oneline --decorate -- <path>
git blame -L <start>,<end> <file>
git show <commit>
```

## MCP Strategy

**mind_mcp** (historical rationale):
1. `hybrid_search`
2. `query_graph_rag_relation`
3. `sequential_search`

**graph_mcp** (code structure):
1. `explore_graph`
2. `query_subgraph` / `find_paths`
3. `analyze_workflow_impact`

Batch calls preferred over multiple small calls.

## Fallback

| Failure | Fallback | Confidence |
|---------|----------|------------|
| mind_mcp | Git + graph + memory | medium |
| graph_mcp | Git + mind + memory | medium |
| Both MCP | Git + memory only | low |

Always notify user of degraded mode with specific missing evidence.

## Progress (long ops >10s)
1. "Retrieving git history..."
2. "Querying code structure..."
3. "Synthesizing evidence..."
