# graph_mcp Query Patterns

**Defaults:** `db="neo4j"`, `project_id="hyperdev"`

## Search Strategy by Scenario

### "I don't know the function name"
```python
# Describe behavior in natural language
semantic_search(query="xử lý thanh toán khi user chưa đăng nhập", db="neo4j", project_id="hyperdev", top_k=10)
```

### "I know part of the name"
```python
search_functions(query="Payment|Handler|Process", limit=20, db="neo4j")
```

### "I have an error message or code snippet"
```python
search_by_code(query="NullPointerException in payment", db="neo4j")
```

### "Vague concept, need graph expansion"
```python
explore_graph(query="authentication flow when token expires", mode="graph_expanded", top_k=15, db="neo4j")
```

## Call Graph Patterns

### Find all callers (upstream)
```python
node_ids = search_functions(query="processPayment", db="neo4j")["ids"]
query_subgraph(function_id=node_ids[0], direction="in", max_depth=3, db="neo4j")
```

### Find all callees (downstream)
```python
query_subgraph(function_id="<id>", direction="out", max_depth=3, db="neo4j")
```

### Trace path from entry point to target
```python
# First find both node IDs
start = search_functions(query="handleRequest", db="neo4j")["ids"][0]
end   = search_functions(query="writeDatabase", db="neo4j")["ids"][0]
find_paths(start_function_id=start, end_function_id=end, max_depth=6, db="neo4j")
```

### Include indirect/callback calls
```python
trace_flow(
  start_id="<id>",
  end_id="<id>",
  rel_types=["CALLS", "POSSIBLE_CALLS"],
  db="neo4j"
)
```

## Module/File Exploration

### List all functions in a file
```python
listup_symbols_matching_file_path(
  modules=["src/payment/"],
  node_types=["Function"],
  db="neo4j"
)
```

### Find public API of a module (entry points)
```python
list_up_entrypoint(modules=["src/payment/"], db="neo4j")
```

### How does module A talk to module B?
```python
find_path_between_module(
  source_modules=["src/order"],
  target_modules=["src/payment"],
  direction="out",
  db="neo4j"
)
```

### Get all methods of a class
```python
listup_class_matching_path(class_names=["PaymentService"], db="neo4j")
```

## Impact Analysis

### Blast radius before changing a function
```python
analyze_workflow_impact(function_id="<id>", direction="downstream", db="neo4j")
```

### Workflows affected by a change
```python
find_workflows_containing(function_id="<id>", include_indirect=True, db="neo4j")
```

## Fullstack (FE ↔ BE)

### Find frontend screens calling a backend endpoint
```python
find_callers_of_endpoint(endpoint_path="/api/payment/confirm", http_method="POST", db="neo4j")
```

### Full call chain from screen to database
```python
get_api_call_chain(component_name="CheckoutScreen", db="neo4j")
```

## Tips

- `semantic_search` results include `node_id` — use those IDs directly with `query_subgraph`, `find_paths`, etc.
- `search_functions` returns both `results` (details) and `ids` (ID list for further queries).
- `content_mode="code"` returns full source; `content_mode="summary"` returns compressed view — use summary for large subgraphs.
- `max_depth` in `query_subgraph` should stay ≤ 3 for performance; use `direction="in"` or `"out"` (not `"both"`) for deep searches.
- When `semantic_search` returns empty: check collection name with `list_qdrant_collections()`, or try `explore_graph` which has multiple fallback strategies.
