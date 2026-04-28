# MCP Orchestration Playbook

Detailed guide for running deep discovery consistently with evidence caching, sharing, and comprehensive MCP integration.

## Phase 0: Preflight and Health Check (30s)

### Step 1: Verify MCP Availability

**mind_mcp checks**:
```python
# List available collections
collections = mind_mcp.list_qdrant_collections()
expected: ["collection_1", "collection_2", ...]

# Optional: List source IDs
source_ids = mind_mcp.list_source_ids()
expected: ["source_1", "source_2", ...]

# Optional: List worksheet documents
worksheets = mind_mcp.list_worksheet_documents()
expected: ["worksheet_1", "worksheet_2", ...]
```

**graph_mcp checks**:
```python
# List available functions
functions = graph_mcp.list_mcp_functions()
expected: ["explore_graph", "search_functions", ...]

# List available parsers
parsers = graph_mcp.list_parsers()
expected: ["python", "javascript", "java", ...]

# List available databases
databases = graph_mcp.list_databases()
expected: ["database_1", "database_2", ...]

# Activate project
activation = graph_mcp.activate_project(
    project_id="{project_id}",
    database="{database_name}",
    parser="{parser_name}"
)
expected: {"status": "activated", "node_count": N, "edge_count": M}
```

### Step 2: Health Check

```python
# Confirm at least 1 collection accessible in mind_mcp
if len(collections) == 0:
    raise Exception("No mind_mcp collections available")

# Confirm project can be activated in graph_mcp
if activation["status"] != "activated":
    raise Exception(f"Failed to activate graph_mcp project: {activation}")

# Record selected sources
selected_collections = collections[:1]  # Use first available collection
selected_source_ids = source_ids if source_ids else []
selected_database = databases[0] if databases else "default"
selected_parser = parsers[0] if parsers else "auto"

# Initialize shared context
shared_context = {
    "project_id": "{project_id}",
    "collections": selected_collections,
    "source_ids": selected_source_ids,
    "database": selected_database,
    "parser": selected_parser,
    "timestamp": datetime.now().isoformat()
}
```

### Step 3: Fallback Mode

```python
if MCP_unavailable_or_degraded:
    fallback_mode = "filesystem_scan_with_reduced_confidence"

    # Document unavailable sources
    unavailable_sources = {
        "mind_mcp": not mind_mcp_available,
        "graph_mcp": not graph_mcp_available
    }

    # Log degraded mode
    log.warning("MCP unavailable or degraded")
    log.info(f"Running in degraded mode: {fallback_mode}")
    log.info(f"Unavailable sources: {unavailable_sources}")

    # Proceed with reduced scope
    proceed_with_reduced_expectations()
```

---

## Phase 1: mind_mcp Knowledge Sweep (Cached, 3min)

### Goal

Extract architecture intent, module definitions, platform constraints, and process docs.

### Tool Sequence with Examples

#### 1.1 list_qdrant_collections and list_source_ids

```python
# Confirm corpus scope
collections = mind_mcp.list_qdrant_collections()
expected_output:
{
  "collections": [
    {"name": "docs_collection", "count": 1234},
    {"name": "code_collection", "count": 5678}
  ]
}

# Optional: Get source IDs
source_ids = mind_mcp.list_source_ids()
expected_output:
{
  "source_ids": ["source_1", "source_2", "source_3"]
}

# Select collection for queries
selected_collection = collections[0]["name"]
log.info(f"Using collection: {selected_collection}")
```

#### 1.2 hybrid_search for Broad Signal

```python
# Architecture overview
result = mind_mcp.hybrid_search(
    query="architecture overview system design modules",
    collection=selected_collection,
    limit=20
)

expected_output:
{
  "results": [
    {
      "id": "paragraph_123",
      "score": 0.92,
      "metadata": {"file": "docs/architecture.md", "line": 45}
    },
    ...
  ],
  "query_time_ms": 123
}

# Module responsibilities
result = mind_mcp.hybrid_search(
    query="module responsibilities service boundaries",
    collection=selected_collection,
    limit=20
)

# Platform constraints
result = mind_mcp.hybrid_search(
    query="platform constraints deployment model infrastructure",
    collection=selected_collection,
    limit=20
)
```

#### 1.3 sequential_search for Ordered Procedures

```python
# Build and release process
result = mind_mcp.sequential_search(
    query="build process deployment pipeline release steps",
    collection=selected_collection,
    limit=10
)

expected_output:
{
  "results": [
    {
      "id": "paragraph_456",
      "order": 1,
      "content": "Step 1: Run tests...",
      "metadata": {"file": "docs/build.md"}
    },
    ...
  ]
}

# Runtime environment
result = mind_mcp.sequential_search(
    query="runtime environment configuration dependencies",
    collection=selected_collection,
    limit=10
)
```

#### 1.4 get_paragraph_text for Exact Citations

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
      "text": "The system consists of three main modules...",
      "metadata": {"file": "docs/architecture.md", "line": 45}
    },
    ...
  ]
}
```

#### 1.5 query_graph_rag_relation for Cross-Entity Relations (Optional)

```python
# Find cross-module dependencies
result = mind_mcp.query_graph_rag_relation(
    entity="PaymentModule",
    relation_types=["depends_on", "implements", "related_to"],
    collection=selected_collection
)

expected_output:
{
  "relations": [
    {
      "source": "PaymentModule",
      "relation": "depends_on",
      "target": "DatabaseModule",
      "confidence": 0.89
    },
    ...
  ]
}
```

#### 1.6 query_worksheet for Structured Data (Optional)

```python
# Get structured data from worksheets
result = mind_mcp.query_worksheet(
    worksheet_id="module_inventory",
    query="SELECT * FROM modules WHERE type='service'"
)

expected_output:
{
  "rows": [
    {"name": "AuthModule", "type": "service", "owner": "team-a"},
    {"name": "PaymentModule", "type": "service", "owner": "team-b"},
    ...
  ]
}
```

### Cache to Shared Evidence

```python
# Save to mcp_knowledge_cache.json
knowledge_cache = {
    "timestamp": datetime.now().isoformat(),
    "project_id": shared_context["project_id"],
    "collections": [selected_collection],
    "queries": [
        {
            "query": "architecture overview",
            "results": hybrid_search_results,
            "citations": paragraph_texts
        },
        ...
    ],
    "evidence_items": [
        {
            "id": "ev_001",
            "type": "architecture_intent",
            "source": "mind_mcp",
            "ref": "paragraph_123",
            "confidence": "high",
            "content": "System consists of three main modules..."
        },
        ...
    ]
}

with open("mcp_knowledge_cache.json", "w") as f:
    json.dump(knowledge_cache, f, indent=2)

log.info(f"Cached {len(knowledge_cache['evidence_items'])} knowledge items")
```

---

## Phase 2: graph_mcp Semantic Map and Call Graph (Cached, 5min)

### Goal

Build code-true structure and flow map, detect API boundary violations.

### Tool Sequence with Examples

#### 2.1 explore_graph for High-Level Discovery

```python
# Discover modules
result = graph_mcp.explore_graph(
    query="module service component",
    limit=100
)

expected_output:
{
  "nodes": [
    {
      "id": "node_001",
      "name": "AuthService",
      "type": "class",
      "file": "src/auth/service.py"
    },
    {
      "id": "node_002",
      "name": "PaymentService",
      "type": "class",
      "file": "src/payment/service.py"
    },
    ...
  ],
  "edges": [
    {"from": "node_001", "to": "node_002", "type": "calls"},
    ...
  ]
}
```

#### 2.2 list_up_entrypoint for Externally-Invoked Roots

```python
# Get entry points
result = graph_mcp.list_up_entrypoint(
    file_pattern="*.py",  # Or specific to scope
    limit=100
)

expected_output:
{
  "entry_points": [
    {
      "id": "node_003",
      "name": "main",
      "type": "function",
      "file": "src/main.py",
      "is_entry": true
    },
    {
      "id": "node_004",
      "name": "app.handle_request",
      "type": "function",
      "file": "src/api/routes.py",
      "is_entry": true
    },
    ...
  ]
}
```

#### 2.3 search_functions for Known Domains

```python
# Search for authentication functions
result = graph_mcp.search_functions(
    query="auth authenticate login verify",
    limit=50
)

expected_output:
{
  "functions": [
    {
      "id": "node_005",
      "name": "verify_token",
      "file": "src/auth/jwt.py",
      "line": 45
    },
    {
      "id": "node_006",
      "name": "login_user",
      "file": "src/auth/handlers.py",
      "line": 78
    },
    ...
  ]
}

# Search for payment functions
result = graph_mcp.search_functions(
    query="payment charge refund transaction",
    limit=50
)

# Search for scheduled jobs
result = graph_mcp.search_functions(
    query="scheduler cron job task worker",
    limit=50
)
```

#### 2.4 search_by_code for Implementation Patterns

```python
# Find SQL queries
result = graph_mcp.search_by_code(
    code_pattern="SELECT",
    limit=50
)

expected_output:
{
  "locations": [
    {
      "file": "src/payment/repository.py",
      "line": 123,
      "code": "SELECT * FROM payments WHERE id = ?"
    },
    ...
  ]
}

# Find HTTP client calls
result = graph_mcp.search_by_code(
    code_pattern="http.get" or "requests.get" or "fetch(",
    limit=50
)

# Find environment variable usage
result = graph_mcp.search_by_code(
    code_pattern="os.getenv" or "process.env",
    limit=50
)
```

#### 2.5 query_subgraph Around Critical Functions

```python
# Get context around critical payment function
result = graph_mcp.query_subgraph(
    node_id="node_007",  # PaymentService.process
    depth=3,
    limit=50
)

expected_output:
{
  "nodes": [
    {"id": "node_007", "name": "process", "type": "method"},
    {"id": "node_008", "name": "validate", "type": "method"},
    {"id": "node_009", "name": "charge", "type": "method"},
    ...
  ],
  "edges": [
    {"from": "node_007", "to": "node_008", "type": "calls"},
    {"from": "node_007", "to": "node_009", "type": "calls"},
    ...
  ]
}
```

#### 2.6 trace_flow and find_paths for Runtime Paths

```python
# Trace execution flow from entry point
result = graph_mcp.trace_flow(
    start_node="node_004",  # API endpoint
    max_depth=5
)

expected_output:
{
  "flow": [
    "node_004",  # app.handle_request
    "node_010",  # AuthMiddleware.verify
    "node_011",  # PaymentController.process
    "node_007",  # PaymentService.process
    "node_009",  # PaymentService.charge
  ],
  "depth": 4
}

# Find paths between nodes
result = graph_mcp.find_paths(
    start_node="node_004",  # API endpoint
    end_node="node_012",    # Database
    max_paths=10
)

expected_output:
{
  "paths": [
    ["node_004", "node_011", "node_007", "node_012"],
    ["node_004", "node_011", "node_013", "node_012"],
    ...
  ]
}
```

#### 2.7 Cross-Module Boundary Discovery (Optional)

```python
# Find paths between modules
result = graph_mcp.find_path_between_module(
    start_module="api",
    end_module="database",
    max_depth=5
)

expected_output:
{
  "paths": [
    {
      "path": ["node_004", "node_011", "node_012"],
      "modules": ["api", "service", "database"],
      "crosses_boundary": true
    },
    ...
  ]
}

# Trace flow between modules
result = graph_mcp.trace_flow_between_module(
    start_module="api",
    end_module="database",
    max_depth=5
)
```

#### 2.8 get_node_details and get_symbol for Evidence Detail

```python
# Batch get node details (10-20 at a time)
node_ids = ["node_007", "node_008", "node_009", ...]
result = graph_mcp.get_node_details(
    node_ids=node_ids
)

expected_output:
{
  "details": [
    {
      "id": "node_007",
      "name": "process",
      "type": "method",
      "file": "src/payment/service.py",
      "line": 45,
      "signature": "process(self, payment_data)",
      "metadata": {"class": "PaymentService"}
    },
    ...
  ]
}

# Get specific symbol details
result = graph_mcp.get_symbol(
    symbol_id="node_007"
)
```

#### 2.9 API/Workflow-Centric Investigations (Optional)

```python
# Find callers of API endpoint
result = graph_mcp.find_callers_of_endpoint(
    endpoint_id="node_004",
    limit=50
)

expected_output:
{
  "callers": [
    {"id": "node_020", "name": "test_api", "type": "test"},
    {"id": "node_021", "name": "call_api", "type": "client"},
    ...
  ]
}

# Get API call chain
result = graph_mcp.get_api_call_chain(
    endpoint_id="node_004",
    max_depth=5
)

expected_output:
{
  "chain": [
    {"id": "node_004", "name": "handle_request", "layer": "api"},
    {"id": "node_011", "name": "process", "layer": "controller"},
    {"id": "node_007", "name": "process", "layer": "service"},
    {"id": "node_012", "name": "save", "layer": "repository"}
  ]
}

# Find workflows containing function
result = graph_mcp.find_workflows_containing(
    node_id="node_007"
)

expected_output:
{
  "workflows": [
    {"id": "workflow_001", "name": "payment_processing"},
    {"id": "workflow_002", "name": "refund_processing"},
    ...
  ]
}

# Analyze workflow impact
result = graph_mcp.analyze_workflow_impact(
    workflow_id="workflow_001"
)

expected_output:
{
  "impact": {
    "functions": ["node_007", "node_008", "node_009"],
    "entry_points": ["node_004"],
    "risk_level": "high"
  }
}
```

### API Warning Sub-Flow

```python
# Discover API entry nodes
api_entries = graph_mcp.list_up_entrypoint(
    file_pattern="*routes*.py" or "*controllers*.py",
    limit=100
)

# Discover driver/DB nodes
db_nodes = graph_mcp.search_functions(
    query="database db repository model",
    limit=50
)

# For each API endpoint, check path to database
api_warnings = []
for api_node in api_entries["entry_points"]:
    for db_node in db_nodes["functions"]:
        # Run path search
        paths = graph_mcp.find_paths(
            start_node=api_node["id"],
            end_node=db_node["id"],
            max_paths=5
        )

        # Check if path bypasses service/repository layers
        for path in paths["paths"]:
            if bypasses_service_layer(path):
                api_warnings.append({
                    "severity": "high",
                    "endpoint": api_node["name"],
                    "file": api_node["file"],
                    "path": path,
                    "warning": "Direct database access from API layer",
                    "suggested_fix": "Add service/repository layer"
                })

# Cache warnings with path evidence
api_warnings_cache = {
    "warnings": api_warnings,
    "timestamp": datetime.now().isoformat()
}
```

### Cache to Shared Evidence

```python
# Save to mcp_graph_cache.json
graph_cache = {
    "timestamp": datetime.now().isoformat(),
    "project_id": shared_context["project_id"],
    "database": shared_context["database"],
    "parser": shared_context["parser"],
    "queries": [
        {
            "query": "module discovery",
            "results": explore_graph_results
        },
        {
            "query": "entry points",
            "results": entry_points_results
        },
        ...
    ],
    "evidence_items": [
        {
            "id": "node_007",
            "type": "function",
            "source": "graph_mcp",
            "metadata": {
                "name": "process",
                "file": "src/payment/service.py",
                "signature": "process(self, payment_data)"
            },
            "neighbors": ["node_008", "node_009"],
            "detail_level": "compact"
        },
        ...
    ],
    "api_warnings": api_warnings
}

with open("mcp_graph_cache.json", "w") as f:
    json.dump(graph_cache, f, indent=2)

log.info(f"Cached {len(graph_cache['evidence_items'])} graph items")
```

---

## Phase 3: Run Companion Skills with Evidence Injection

### 3.1 repo-recon (Consumes Both Caches)

**Input from cache**:
```python
# Load caches
with open("mcp_knowledge_cache.json", "r") as f:
    knowledge_cache = json.load(f)

with open("mcp_graph_cache.json", "r") as f:
    graph_cache = json.load(f)

# Extract architecture intent and domain terms
architecture_intent = [
    item for item in knowledge_cache["evidence_items"]
    if item["type"] == "architecture_intent"
]

domain_terms = [
    item for item in knowledge_cache["evidence_items"]
    if item["type"] == "module_def"
]

# Extract module boundaries and entry points
module_boundaries = [
    item for item in graph_cache["evidence_items"]
    if item["type"] == "module"
]

entry_points = [
    item for item in graph_cache["evidence_items"]
    if item["type"] == "entrypoint"
]
```

**Workflow**:
```python
# 1. Load cached evidence first
log.info("Loaded {len(architecture_intent)} architecture items")
log.info("Loaded {len(domain_terms)} domain terms")
log.info("Loaded {len(module_boundaries)} module boundaries")
log.info("Loaded {len(entry_points)} entry points")

# 2. Use cached results to scope queries
# Don't re-query same data from MCP
scope_for_filesystem_scan = {
    "known_modules": [item["metadata"]["name"] for item in module_boundaries],
    "known_entry_points": [item["metadata"]["name"] for item in entry_points],
    "gaps": identify_gaps(knowledge_cache, graph_cache)
}

# 3. Run filesystem scan only for gaps
filesystem_results = scan_filesystem_for_gaps(
    repo_path=shared_context["repo_path"],
    gaps=scope_for_filesystem_scan["gaps"]
)

# 4. Merge cached evidence with new filesystem evidence
merged_evidence = merge_evidence(
    knowledge_cache,
    graph_cache,
    filesystem_results
)

# 5. Output with evidence tags
output_repo_recon(merged_evidence)
```

### 3.2 tech-build-audit (Consumes Both Caches)

**Input from cache**:
```python
# Extract build/release process and platform constraints
build_process = [
    item for item in knowledge_cache["evidence_items"]
    if item["type"] == "process_doc"
]

platform_constraints = [
    item for item in knowledge_cache["evidence_items"]
    if item["type"] == "platform_constraint"
]

# Extract build orchestration code and deploy adapters
build_code = [
    item for item in graph_cache["evidence_items"]
    if "build" in item["metadata"]["file"].lower()
]

deploy_adapters = [
    item for item in graph_cache["evidence_items"]
    if "deploy" in item["metadata"]["name"].lower()
]
```

**Workflow**:
```python
# 1. Load cached evidence first
log.info("Loaded {len(build_process)} build process items")
log.info("Loaded {len(platform_constraints)} platform constraints")

# 2. Use cached results to identify build/runtime surfaces
build_surfaces = identify_build_surfaces(build_code, deploy_adapters)

# 3. Run filesystem audit only for configuration validation
config_validation = validate_config_files(
    repo_path=shared_context["repo_path"],
    expected_surfaces=build_surfaces
)

# 4. Merge cached evidence with config file evidence
merged_evidence = merge_evidence(
    knowledge_cache,
    graph_cache,
    config_validation
)

# 5. Output with evidence tags
output_tech_build_audit(merged_evidence)
```

### 3.3 module-summary-report (Consumes All Outputs)

**Input from**:
```python
# Load all evidence sources
knowledge_cache = load_cache("mcp_knowledge_cache.json")
graph_cache = load_cache("mcp_graph_cache.json")
repo_recon = load_output("repo_recon.*")
tech_build_audit = load_output("tech_build_audit.*")

# Merge all evidence
all_evidence = merge_all_evidence(
    knowledge_cache,
    graph_cache,
    repo_recon,
    tech_build_audit
)
```

**Workflow**:
```python
# 1. Load all evidence sources
log.info("Loaded {len(all_evidence)} total evidence items")

# 2. Reconcile conflicts
reconciled_evidence = reconcile_conflicts(
    all_evidence,
    conflict_rules={
        "implementation": "graph_mcp",
        "domain": "mind_mcp",
        "configuration": "filesystem"
    }
)

# 3. Synthesize into stakeholder-facing summary
summary = synthesize_summary(
    reconciled_evidence,
    audience=shared_context["audience"]
)

# 4. Output with comprehensive evidence tags
output_module_summary(summary, reconciled_evidence)
```

---

## Phase 4: Evidence Reconciliation and Bundle Generation

### Evidence Tagging

```python
# Per claim, attach source tags
for claim in all_claims:
    claim["source_type"] = determine_source_type(claim)
    claim["source_ref"] = get_source_reference(claim)
    claim["confidence"] = assess_confidence(claim)
    claim["cache_hit"] = was_cached(claim)

def determine_source_type(claim):
    if claim["id"].startswith("ev_"):
        return "mind_mcp"
    elif claim["id"].startswith("node_"):
        return "graph_mcp"
    else:
        return "filesystem"

def assess_confidence(claim):
    if claim["source_type"] == "graph_mcp":
        return "high"  # Current code truth
    elif claim["source_type"] == "mind_mcp":
        return "medium"  # May be outdated
    else:
        return "low"  # Filesystem only
```

### Conflict Resolution

```python
# Apply conflict resolution rules
conflicts = detect_conflicts(all_claims)

for conflict in conflicts:
    mind_mcp_claim = conflict["mind_mcp"]
    graph_mcp_claim = conflict["graph_mcp"]

    # Apply priority rules
    if is_implementation_conflict(conflict):
        resolved = resolve_with_priority(
            conflict,
            priority="graph_mcp",
            reason="Implementation truth: graph_mcp"
        )
    elif is_domain_conflict(conflict):
        resolved = resolve_with_priority(
            conflict,
            priority="mind_mcp",
            reason="Domain/process truth: mind_mcp"
        )
    else:
        # Unresolved conflict
        resolved = mark_as_unresolved(conflict)
        create_follow_up_action(resolved)
```

### Bundle Generation

```python
# Generate discovery bundle
bundle = {
    "metadata": {
        "timestamp": datetime.now().isoformat(),
        "project_id": shared_context["project_id"],
        "mcp_sources": ["mind_mcp", "graph_mcp"],
        "cache_status": {
            "mind_mcp": "available" if knowledge_cache else "unavailable",
            "graph_mcp": "available" if graph_cache else "unavailable"
        }
    },
    "evidence_provenance": {
        "total_claims": len(all_claims),
        "mcp_sourced_claims": count_mcp_claims(all_claims),
        "cache_hit_rate": calculate_cache_hit_rate(all_claims)
    },
    "artifacts": {
        "repo_recon": "repo_recon.json",
        "tech_build_audit": "tech_build_audit.json",
        "summary": "summary.md"
    },
    "mcp_caches": {
        "knowledge_cache": "mcp_knowledge_cache.json",
        "graph_cache": "mcp_graph_cache.json"
    },
    "efficiency_metrics": {
        "total_claims": len(all_claims),
        "mcp_sourced_claims": count_mcp_claims(all_claims),
        "cache_hit_rate": calculate_cache_hit_rate(all_claims),
        "cache_miss_queries": get_cache_misses(all_claims),
        "context_control_batches": get_batch_operations(all_claims)
    }
}

with open("discovery_bundle.json", "w") as f:
    json.dump(bundle, f, indent=2)

log.info("Discovery bundle generated")
log.info(f"Total claims: {bundle['efficiency_metrics']['total_claims']}")
log.info(f"MCP-sourced: {bundle['efficiency_metrics']['mcp_sourced_claims']}")
log.info(f"Cache hit rate: {bundle['efficiency_metrics']['cache_hit_rate']}%")
```

---

## Context Control Guidelines

### For Large Codebases (>100k LOC)

#### 1. Scope by Module

```python
# Use explore_graph with module-specific terms
result = graph_mcp.explore_graph(
    query="AuthService login",  # Module-specific
    limit=50
)

# Use list_up_entrypoint filtered by module
result = graph_mcp.list_up_entrypoint(
    file_pattern="src/auth/*.py",  # Module-specific
    limit=50
)

# Process modules sequentially
modules = ["auth", "payment", "notification", ...]
for module in modules:
    log.info(f"Processing module: {module}")
    process_module(module)
    summarize_findings(module)
```

#### 2. Limit Result Sizes

```python
# search_functions with limit
result = graph_mcp.search_functions(
    query="auth",
    limit=20  # Conservative limit
)

# get_node_details in batches
node_ids = list_of_node_ids
batch_size = 20
for i in range(0, len(node_ids), batch_size):
    batch = node_ids[i:i+batch_size]
    result = graph_mcp.get_node_details(node_ids=batch)
    process_batch(result)

# query_subgraph with small limit first
result = graph_mcp.query_subgraph(
    node_id=critical_node,
    depth=2,  # Start shallow
    limit=20  # Conservative limit
)

# Then expand incrementally if needed
if needs_expansion(result):
    result = graph_mcp.query_subgraph(
        node_id=critical_node,
        depth=3,
        limit=50
    )
```

#### 3. Incremental Expansion

```python
# Start with entry points and high-level modules
entry_points = graph_mcp.list_up_entrypoint(limit=50)
high_level_modules = graph_mcp.explore_graph(
    query="module service",
    limit=50
)

# Expand only on critical paths
critical_paths = identify_critical_paths(entry_points, high_level_modules)

for path in critical_paths:
    log.info(f"Expanding critical path: {path['name']}")
    # Require user confirmation
    if confirm_expansion(path):
        expanded = expand_path(path)
        summarize_expansion(expanded)
    else:
        log.info(f"Skipping expansion of {path['name']}")
```

#### 4. Batch Processing

```python
# Process 20 nodes at a time
all_nodes = get_all_nodes()
batch_size = 20

for i in range(0, len(all_nodes), batch_size):
    batch = all_nodes[i:i+batch_size]
    log.info(f"Processing batch {i//batch_size + 1}/{len(all_nodes)//batch_size + 1}")

    # Get details for batch
    details = graph_mcp.get_node_details(node_ids=batch)

    # Summarize findings
    summary = summarize_batch(details)
    log.info(f"Batch {i//batch_size + 1}: {summary}")

    # Check if user wants to continue
    if i + batch_size < len(all_nodes):
        if not confirm_continue():
            log.info("Stopping at user request")
            break
```

---

## Error Handling and Recovery

### Timeout Handling

```python
def call_with_timeout(func, *args, timeout=30, **kwargs):
    """Wrapper for MCP calls with timeout"""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"MCP call timeout after {timeout}s")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        result = func(*args, **kwargs)
        signal.alarm(0)
        return result
    except TimeoutError as e:
        log.warning(f"MCP timeout: {e}")
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

### Empty Results Handling

```python
def handle_empty_results(result, query_type):
    """Expand search scope when no results found"""

    if not result.get("nodes") and not result.get("results"):
        log.warning(f"No results for {query_type}, expanding scope")

        if query_type == "search_functions":
            # Try semantic search instead of exact
            return graph_mcp.search_functions(
                query="module",  # Broader query
                limit=result["limit"] * 2
            )

        elif query_type == "query_subgraph":
            # Increase depth and limits
            return graph_mcp.query_subgraph(
                node_id=result["node_id"],
                depth=result["depth"] + 2,
                limit=result["limit"] * 2
            )

    return result
```

---

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import time

class MCPCache:
    def __init__(self, ttl=600):
        self.cache = {}
        self.ttl = ttl

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time())

# Usage
mcp_cache = MCPCache(ttl=600)  # 10 minute cache

def cached_hybrid_search(query):
    cache_key = f"hybrid_search:{query}"

    # Check cache
    cached = mcp_cache.get(cache_key)
    if cached:
        log.info(f"Cache hit for {cache_key}")
        return cached

    # Call MCP
    result = mind_mcp.hybrid_search(query=query)

    # Cache result
    mcp_cache.set(cache_key, result)

    return result
```

### Batch Processing

```python
def batch_process_nodes(nodes, batch_size=20):
    """Process nodes in batches to avoid overwhelming MCP"""

    results = []
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i+batch_size]

        # Parallel calls within batch
        batch_results = parallel_map(
            graph_mcp.get_node_details,
            batch,
            max_workers=3
        )

        results.extend(batch_results)

    return results
```

---

## Evidence Documentation

For each query, record:
- **Query**: Function name and parameters
- **Result**: Summary of results
- **Confidence**: How certain you are (High/Medium/Low)
- **Relevance**: How it impacts the analysis
- **Duration**: How long the query took
- **Cache Hit**: Whether result was cached

This creates a traceable chain from evidence to conclusions.
