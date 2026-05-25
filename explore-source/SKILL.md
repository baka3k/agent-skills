---
name: explore-source
description: Explore and understand source code using graph_mcp. Always start with semantic_search for fast relevance, then trace call graphs. Default db=neo4j, project_id=hyperdev.
version: 1.0.0
last_updated: 2026-05-25
---

# Explore Source Code — graph_mcp

**Always-on defaults:** `db="neo4j"`, `project_id="hyperdev"`

Activate once per session to set session-wide defaults:
```python
activate_project(database_name="neo4j")
```

## 1. Find — Always Start with semantic_search

`semantic_search` uses vector embeddings — it matches *meaning*, not just keywords.

```python
# PRIMARY: search by meaning
semantic_search(query="<describe what the code does>", db="neo4j", project_id="hyperdev", top_k=10)

# FALLBACK 1: vague query + graph expansion (heavier, more comprehensive)
explore_graph(query="<natural language>", mode="hybrid", db="neo4j", top_k=10)

# FALLBACK 2: fuzzy name match
search_functions(query="ClassName|funcName", db="neo4j")

# FALLBACK 3: exact code text
search_by_code(query="exact_string_in_code", db="neo4j")
```

## 2. Inspect

```python
get_symbol(node_id="<id>", db="neo4j")
get_node_details(node_ids=["id1", "id2"], db="neo4j")  # batch
```

## 3. Call Graph (who calls whom)

```python
# Callers + callees around a function
query_subgraph(function_id="<id>", direction="both", max_depth=2, db="neo4j")
# direction: "in"=callers, "out"=callees, "both"=both

# Trace path between two functions
find_paths(start_function_id="<id_a>", end_function_id="<id_b>", db="neo4j")

# Include indirect calls (function pointers, callbacks)
trace_flow(start_id="<id>", end_id="<id>", rel_types=["CALLS", "POSSIBLE_CALLS"], db="neo4j")
```

## 4. Module / File Level

```python
listup_symbols_matching_file_path(modules=["path/fragment"], db="neo4j")
list_up_entrypoint(modules=["path/fragment"], db="neo4j")           # public API of a module
find_path_between_module(source_modules=["A"], target_modules=["B"], db="neo4j")
```

## 5. Impact & API Chain

```python
analyze_workflow_impact(function_id="<id>", db="neo4j")             # blast radius
find_callers_of_endpoint(endpoint_path="/api/path", db="neo4j")     # FE callers of BE endpoint
get_api_call_chain(component_name="ScreenName", db="neo4j")         # FE → BE → DB chain
```

## Quick Decision Table

| Goal | Tool |
|------|------|
| Find by meaning/description | `semantic_search` ← **start here** |
| Find by name (fuzzy) | `search_functions` |
| Find by code text | `search_by_code` |
| Who calls function X? | `query_subgraph(direction="in")` |
| What does X call? | `query_subgraph(direction="out")` |
| Path from A to B | `find_paths` |
| All symbols in a file | `listup_symbols_matching_file_path` |
| Module A → Module B paths | `find_path_between_module` |
| Blast radius before change | `analyze_workflow_impact` |
| FE → BE → DB chain | `get_api_call_chain` |

Extended patterns: `references/query-patterns.md`
