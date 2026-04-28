# MCP Porting Playbook

Detailed guide for leveraging mind_mcp and graph_mcp for safe C++ legacy code porting with comprehensive function signatures, parameters, and examples.

## Phase 0: Preflight (30s)

### Step 1: Verify MCP Availability

**mind_mcp checks**:
```python
# List available collections
collections = mind_mcp.list_qdrant_collections()
expected: ["collection_1", "collection_2", ...]

# Optional: List source IDs
source_ids = mind_mcp.list_source_ids()
expected: ["source_1", "source_2", ...]
```

**graph_mcp checks**:
```python
# List available parsers (look for C++ parser)
parsers = graph_mcp.list_parsers()
expected: ["cpp", "cxx", "python", ...]

# List available databases
databases = graph_mcp.list_databases()
expected: ["database_1", "database_2", ...]

# List available functions
functions = graph_mcp.list_mcp_functions()
expected: ["explore_graph", "search_functions", ...]

# Activate project
activation = graph_mcp.activate_project(
    project_id="{project_id}",
    database="{database_name}",
    parser="cpp"  # C++ parser
)
expected: {"status": "activated", "node_count": N, "edge_count": M}
```

### Step 2: Record Available Context

```python
# Record available sources
selected_collections = collections[:1]  # Use first available collection
selected_source_ids = source_ids if source_ids else []
selected_parser = "cpp" if "cpp" in parsers else parsers[0]
selected_database = databases[0] if databases else "default"

# Initialize shared context
porting_context = {
    "project_id": "{project_id}",
    "collections": selected_collections,
    "source_ids": selected_source_ids,
    "parser": selected_parser,
    "database": selected_database,
    "timestamp": datetime.now().isoformat()
}
```

### Step 3: Fallback Mode

```python
if MCP_unavailable_or_degraded:
    fallback_mode = "filesystem_analysis_with_reduced_confidence"

    # Document unavailable sources
    unavailable_sources = {
        "mind_mcp": not mind_mcp_available,
        "graph_mcp": not graph_mcp_available
    }

    # Log degraded mode
    log.warning("MCP unavailable or degraded for porting analysis")
    log.info(f"Running in degraded mode: {fallback_mode}")
    log.info(f"Unavailable sources: {unavailable_sources}")

    # Proceed with filesystem-only analysis
    proceed_with_reduced_scope()
```

---

## Phase 1: Context Discovery from mind_mcp (Cached, 3min)

### Goal

Understand historical context, known issues, and porting constraints.

### Suggested Queries

```python
queries = [
    "porting guide OR migration guide",
    "architecture decision OR design rationale",
    "known issue OR technical debt",
    "dependency constraint OR platform requirement",
    "third party library OR external system"
]
```

### Tool Sequence with Examples

#### 1.1 hybrid_search for Broad Signal

```python
# Search for porting guides
result = mind_mcp.hybrid_search(
    query="porting guide migration strategy C++ modernization",
    collection=selected_collection,
    limit=20
)

expected_output:
{
  "results": [
    {
      "id": "paragraph_123",
      "score": 0.92,
      "metadata": {"file": "docs/porting-guide.md", "line": 45}
    },
    ...
  ],
  "query_time_ms": 123
}

# Search for architecture decisions
result = mind_mcp.hybrid_search(
    query="architecture decision design rationale legacy system",
    collection=selected_collection,
    limit=20
)

# Search for known issues
result = mind_mcp.hybrid_search(
    query="known issue technical debt legacy bug workaround",
    collection=selected_collection,
    limit=20
)
```

#### 1.2 sequential_search for Step-by-Step Procedures

```python
# Search for migration procedures
result = mind_mcp.sequential_search(
    query="migration procedure step by step porting process",
    collection=selected_collection,
    limit=10
)

expected_output:
{
  "results": [
    {
      "id": "paragraph_456",
      "order": 1,
      "content": "Step 1: Analyze existing code...",
      "metadata": {"file": "docs/migration.md"}
    },
    ...
  ]
}
```

#### 1.3 get_paragraph_text for Exact Citations

```python
# Get full text for relevant paragraphs
paragraph_ids = [r["id"] for r in hybrid_search_results]
result = mind_mcp.get_paragraph_text(
    paragraph_ids=paragraph_ids
)

expected_output:
{
  "paragraphs": [
    {
      "id": "paragraph_123",
      "text": "The legacy system must preserve exact behavior...",
      "metadata": {"file": "docs/porting-guide.md", "line": 45}
    },
    ...
  ]
}
```

### Capture Evidence

```python
# Capture context facts
context_facts = []

for result in hybrid_search_results:
    context_fact = {
        "source": "mind_mcp",
        "ref": result["id"],
        "type": determine_type(result),  # constraint | workaround | rationale
        "confidence": "high" if result["score"] > 0.8 else "medium",
        "content": summarize_content(result)
    }
    context_facts.append(context_fact)

# Cache context facts
with open("mcp_context_cache.json", "w") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "context_facts": context_facts
    }, f, indent=2)
```

---

## Phase 2: Code Structure Analysis from graph_mcp (Cached, 5min)

### Goal

Map class hierarchies, side effects, and dependencies before porting.

### 2.1 Class and Function Discovery

```python
# Activate project context
activation = graph_mcp.activate_project(
    project_id="{project_id}",
    database="{database}",
    parser="cpp"  # C++ parser
)

# Explore graph for classes/functions
result = graph_mcp.explore_graph(
    query="LegacyDataManager",  # Class name
    limit=100
)

expected_output:
{
  "nodes": [
    {
      "id": "node_001",
      "name": "LegacyDataManager",
      "type": "class",
      "file": "src/legacy/data_manager.cpp"
    },
    {
      "id": "node_002",
      "name": "processData",
      "type": "method",
      "file": "src/legacy/data_manager.cpp"
    },
    ...
  ],
  "edges": [
    {"from": "node_002", "to": "node_001", "type": "method_of"},
    ...
  ]
}

# Search for large functions
result = graph_mcp.search_functions(
    query="complex process handle",
    limit=50
)

expected_output:
{
  "functions": [
    {
      "id": "node_003",
      "name": "processTransaction",
      "file": "src/legacy/processor.cpp",
      "lines": "1234-1567"  # 333 lines - large!
    },
    ...
  ]
}
```

### 2.2 Class Hierarchy Mapping

```python
# Search for all methods in a class
class_name = "LegacyDataManager"
result = graph_mcp.search_functions(
    query=class_name,  # Search for class name
    limit=100
)

expected_output:
{
  "functions": [
    {
      "id": "node_010",
      "name": "LegacyDataManager::initialize",
      "type": "method",
      "file": "src/legacy/data_manager.cpp"
    },
    {
      "id": "node_011",
      "name": "LegacyDataManager::processData",
      "type": "method",
      "file": "src/legacy/data_manager.cpp"
    },
    ...
  ]
}

# Get subgraph centered on class constructor
result = graph_mcp.query_subgraph(
    node_id=constructor_node_id,
    depth=3,
    limit=50
)

expected_output:
{
  "nodes": [
    {"id": "node_020", "name": "~LegacyDataManager", "type": "destructor"},
    {"id": "node_021", "name": "memberVariable", "type": "field"},
    ...
  ],
  "edges": [
    {"from": "node_020", "to": "node_021", "type": "accesses"},
    ...
  ]
}

# Find externally-called methods
result = graph_mcp.list_up_entrypoint(
    file_pattern="src/legacy/*.h",
    limit=100
)

expected_output:
{
  "entry_points": [
    {
      "id": "node_030",
      "name": "LegacyDataManager::publicAPI",
      "type": "method",
      "file": "src/legacy/data_manager.h",
      "is_entry": true
    },
    ...
  ]
}
```

### 2.3 Side Effect Tracing

```python
# Trace flow from function entry point
function_id = "node_003"  # processTransaction
result = graph_mcp.trace_flow(
    start_node=function_id,
    max_depth=5
)

expected_output:
{
  "flow": [
    "node_003",  # processTransaction
    "node_040",  # validateInput
    "node_041",  # updateDatabase
    "node_042",  # sendNotification
    "node_043",  # logTransaction
  ],
  "depth": 4
}

# Find paths to global/static variables
result = graph_mcp.find_paths(
    start_node=function_id,
    end_node="global_state",  # Global variable node
    max_paths=10
)

expected_output:
{
  "paths": [
    ["node_003", "node_041", "node_050", "global_state"],
    ...
  ]
}

# Find paths to file I/O operations
result = graph_mcp.find_paths(
    start_node=function_id,
    end_node="file_write",  # File write operation
    max_paths=10
)

# Get node details for side effects
result = graph_mcp.get_node_details(
    node_ids=[function_id, "node_041", "node_042"]
)

expected_output:
{
  "details": [
    {
      "id": "node_003",
      "name": "processTransaction",
      "signature": "bool processTransaction(TransactionData& data)",
      "side_effects": ["writes to database", "sends notification", "logs transaction"],
      "thread_safety": "not_thread_safe",  # Important!
      "error_handling": "returns false on error"
    },
    ...
  ]
}
```

### 2.4 API Usage Analysis

```python
# Query subgraph to find system calls
result = graph_mcp.query_subgraph(
    node_id=function_id,
    depth=2,
    limit=50
)

# Look for system call patterns
system_calls = identify_system_calls(result)
# POSIX APIs: open, read, write, close, socket, etc.
# Win32 APIs: CreateFile, ReadFile, WriteFile, etc.

# Query subgraph for third-party libraries
result = graph_mcp.query_subgraph(
    node_id=function_id,
    depth=3,
    limit=50
)

# Look for library calls
library_calls = identify_library_calls(result)
# e.g., OpenSSL, Boost, custom libraries

# Search for unsafe patterns
result = graph_mcp.search_by_code(
    code_pattern="*",  # Raw pointer dereference
    limit=50
)

result = graph_mcp.search_by_code(
    code_pattern="(",
    limit=50  # C-style casts
)
```

---

## Phase 3: Behavior Contract Enrichment

### Combine Evidence Sources

```python
# For each target function
for function_id in target_functions:
    # Get graph_mcp analysis
    graph_analysis = get_from_cache(function_id, "graph_mcp")

    # Get mind_mcp context
    mind_context = get_from_cache(function_id, "mind_mcp")

    # Get filesystem analysis
    fs_analysis = get_from_cache(function_id, "filesystem")

    # Create enriched behavior contract
    contract = {
        "function_name": graph_analysis["name"],

        "from_mind_mcp": {
            "business_purpose": mind_context.get("purpose"),
            "historical_bugs": mind_context.get("bugs"),
            "known_workarounds": mind_context.get("workarounds"),
            "constraints": mind_context.get("constraints")
        },

        "from_graph_mcp": {
            "signature": graph_analysis["signature"],
            "side_effects": graph_analysis["side_effects"],
            "dependencies": graph_analysis["dependencies"],
            "thread_safety": graph_analysis["thread_safety"]
        },

        "from_filesystem": {
            "size_metrics": fs_analysis["size"],
            "complexity_metrics": fs_analysis["complexity"],
            "unsafe_patterns": fs_analysis["unsafe_patterns"]
        },

        "contract_fields": {
            "inputs": extract_inputs(graph_analysis),
            "outputs": extract_outputs(graph_analysis),
            "side_effects": graph_analysis["side_effects"],
            "ordering_constraints": extract_ordering(graph_analysis),
            "boundary_rules": extract_boundaries(graph_analysis),
            "nondeterminism": extract_nondeterminism(graph_analysis),
            "platform_assumptions": extract_platform(graph_analysis),
            "performance": extract_performance(fs_analysis)
        }
    }

    # Save contract
    save_contract(contract, f"contracts/{function_id}.md")
```

### Contract Template

```markdown
# Contract: {function_name}

## Signature
- Legacy: `{legacy_signature}`
- Target: `{target_signature}`

## Inputs
- Required params: `{required_params}`
- Optional params: `{optional_params}`
- Accepted ranges/formats: `{ranges}`

## Outputs
- Return/status code mapping: `{return_codes}`
- Output payload shape: `{output_shape}`

## Side Effects
- Files touched: `{files_touched}`
- Global/static state touched: `{globals_touched}`
- External dependencies: `{external_deps}`

## Invariants
- Must always hold: `{invariants}`

## Error and Edge Cases
- Empty/null handling: `{empty_handling}`
- Boundary numeric values: `{boundary_values}`
- Invalid state behavior: `{invalid_state}`

## Open Risks
- Unknown legacy intent: `{unknown_intents}`
- Unverified branches: `{unverified_branches}`

## Evidence Sources
- mind_mcp: `{mind_mcp_refs}`
- graph_mcp: `{graph_mcp_refs}`
- filesystem: `{filesystem_refs}`
```

---

## Phase 4: Migration Planning with Evidence

### Slice by graph_mcp Clusters

```python
# Use graph_mcp cluster analysis
result = graph_mcp.query_subgraph(
    node_id=class_node_id,
    depth=2,
    limit=100
)

# Identify function clusters
clusters = identify_clusters(result)

# Order slices by risk
slices = []
for cluster in clusters:
    slice = {
        "slice_id": len(slices) + 1,
        "functions": cluster["functions"],
        "risk": assess_risk(cluster),  # low/medium/high
        "external_deps": cluster["external_dependencies"],
        "business_context": get_business_context(cluster, mind_mcp),
        "evidence": {
            "mind_mcp": get_mind_refs(cluster),
            "graph_mcp": get_graph_refs(cluster)
        }
    }
    slices.append(slice)

# Sort by risk (low first)
slices.sort(key=lambda s: s["risk"])
```

### Slice Order Example

```yaml
slice_order:
  - slice_id: 1
    functions: [UtilityClass::helper1, UtilityClass::helper2]
    risk: low
    external_deps: []
    business_context: "Utility functions, no side effects"
    evidence:
      mind_mcp: [para_123]
      graph_mcp: [node_001, node_002]

  - slice_id: 2
    functions: [LegacyDataManager::processData]
    risk: high
    external_deps: [legacy_database_lib]
    business_context: "Core business logic, must preserve exact protocol"
    evidence:
      mind_mcp: [para_456]
      graph_mcp: [node_003]
```

---

## Phase 5: Parity Harness Guidance

### Entry Point Coverage

```python
# Get all public callable methods
result = graph_mcp.list_up_entrypoint(
    file_pattern="src/public/*.h",
    limit=100
)

# Create parity test for each entry point
for entry_point in result["entry_points"]:
    create_parity_test(entry_point)
```

### Path Coverage

```python
# Find happy path
result = graph_mcp.find_paths(
    start_node=entry_point["id"],
    end_node=success_node,
    max_paths=5
)

# Find error paths
result = graph_mcp.search_functions(
    query="error exception failure",
    limit=20
)

# Create test cases for each path
for path in result["paths"]:
    create_test_case(path)
```

### Edge Case Discovery

```python
# Get historical bugs from mind_mcp
bugs = mind_mcp.hybrid_search(
    query="bug issue edge case boundary",
    collection=selected_collection,
    limit=20
)

# Get boundary conditions from graph_mcp
result = graph_mcp.get_node_details(
    node_ids=[function_id]
)

# Create edge case tests
for bug in bugs["results"]:
    create_edge_case_test(bug)
```

### Parity Test Template

```markdown
# Parity Cases: {function_name}

| Case ID | Input | Expected Legacy Output | Expected Side Effect | Port Output | Match |
| --- | --- | --- | --- | --- | --- |
| C01 | {input_data} | {expected_output} | {expected_side_effects} | {port_output} | ✅/❌ |
| C02 | {input_data} | {expected_output} | {expected_side_effects} | {port_output} | ✅/❌ |
```

---

## Phase 6: Verification After Port

### Re-analyze Ported Code

```python
# Re-run search_functions on ported code
result = graph_mcp.search_functions(
    query="{ported_function_name}",
    limit=50
)

# Re-run query_subgraph on ported code
result = graph_mcp.query_subgraph(
    node_id=ported_node_id,
    depth=3,
    limit=50
)

# Compare with original structure
original_structure = load_from_cache("original_structure")
ported_structure = result

# Verify preservation
if structures_match(original_structure, ported_structure):
    log.info("Call graph structure preserved")
else:
    log.warning("Call graph structure changed")
    document_divergence(original_structure, ported_structure)
```

### Verify Behavior Preservation

```python
# Run parity harness
parity_result = run_parity_harness(ported_function)

# Check all golden cases
if parity_result["all_pass"]:
    log.info("Parity verified: All golden cases pass")
else:
    log.error("Parity failed: Some golden cases fail")
    for failure in parity_result["failures"]:
        log.error(f"  Case {failure['case_id']}: {failure['details']}")
```

### Document Divergences

```python
# If structural changes needed
if structural_divergence:
    divergence_report = {
        "original_structure": original_structure,
        "ported_structure": ported_structure,
        "divergences": identify_divergences(),
        "rationale": explain_rationale(),
        "risks": assess_risks()
    }

    save_divergence_report(divergence_report)
```

---

## Evidence Reconciliation

### Per Claim Evidence Tags

```python
for claim in all_claims:
    claim["source_type"] = determine_source_type(claim)
    claim["source_ref"] = get_source_reference(claim)
    claim["confidence"] = assess_confidence(claim)

def determine_source_type(claim):
    if claim["id"].startswith("ev_"):
        return "mind_mcp"
    elif claim["id"].startswith("node_"):
        return "graph_mcp"
    else:
        return "filesystem"
```

### Conflict Resolution Rules

```yaml
conflict_resolution:
  priority_rules:
    1. "Implementation truth: graph_mcp (current code behavior)"
    2. "Intent/purpose truth: mind_mcp (why it exists)"
    3. "Recent changes: filesystem (actual files)"

  conflict_handling:
    - "If code behavior conflicts with documented intent: Flag as technical debt"
    - "If documentation unclear: Use code analysis as primary source"
    - "If both unclear: Mark as high-risk, require manual investigation"
```

---

## Context Control for Large Codebases

### When analyzing large C++ codebases (>100k LOC):

#### 1. Scope by Module/Class

```python
# Use search_functions with specific class names
result = graph_mcp.search_functions(
    query="DataManager",  # Specific class
    limit=50
)

# Use query_subgraph with low limit first
result = graph_mcp.query_subgraph(
    node_id=class_node_id,
    depth=2,  # Start shallow
    limit=20  # Conservative limit
)

# Then expand incrementally
if needs_expansion(result):
    result = graph_mcp.query_subgraph(
        node_id=class_node_id,
        depth=3,
        limit=50
    )
```

#### 2. Limit Result Sizes

```python
# Process in batches
node_ids = list_of_all_node_ids
batch_size = 20

for i in range(0, len(node_ids), batch_size):
    batch = node_ids[i:i+batch_size]

    # Get details for batch
    result = graph_mcp.get_node_details(
        node_ids=batch
    )

    process_batch(result)
```

#### 3. Incremental Analysis

```python
# Start with entry points
result = graph_mcp.list_up_entrypoint(
    file_pattern="src/public/*.h",
    limit=100
)

# Expand on-demand based on call graph
for entry_point in result["entry_points"]:
    log.info(f"Analyzing entry point: {entry_point['name']}")

    # Analyze call graph from entry point
    analyze_from_entry_point(entry_point)

    # Summarize before proceeding
    summarize_findings(entry_point)
```

---

## Performance Optimization

### Caching Strategy

```python
# Cache mind_mcp context
mind_cache = MCPCache(ttl=900)  # 15 minutes

def cached_hybrid_search(query):
    cache_key = f"hybrid_search:{query}"

    # Check cache
    cached = mind_cache.get(cache_key)
    if cached:
        log.info(f"Cache hit for {cache_key}")
        return cached

    # Call MCP
    result = mind_mcp.hybrid_search(query=query)

    # Cache result
    mind_cache.set(cache_key, result)

    return result
```

### Batch Processing

```python
# Batch node details requests
def batch_get_node_details(node_ids, batch_size=20):
    results = []

    for i in range(0, len(node_ids), batch_size):
        batch = node_ids[i:i+batch_size]

        result = graph_mcp.get_node_details(
            node_ids=batch
        )

        results.extend(result["details"])

    return results
```

---

## Error Handling Patterns

### Timeout Handling

```python
def call_with_timeout(func, *args, timeout=30, **kwargs):
    """Wrapper for MCP calls with timeout"""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Call timeout after {timeout}s")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        result = func(*args, **kwargs)
        signal.alarm(0)
        return result
    except TimeoutError as e:
        log.warning(f"Timeout: {e}")
        return {"timeout": True, "partial_results": {}}

# Usage
result = call_with_timeout(
    graph_mcp.query_subgraph,
    node_id=node_id,
    timeout=30
)

if result.get("timeout"):
    log.info("Returning partial results due to timeout")
```

---

## Evidence Documentation

For each query, record:
- **Query**: Function name and parameters
- **Result**: Summary of results
- **Confidence**: How certain you are (High/Medium/Low)
- **Relevance**: How it impacts the porting decision
- **Duration**: How long the query took
- **Cache Hit**: Whether result was cached

This creates a traceable chain from evidence to porting decisions.
