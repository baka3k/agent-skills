# MCP Bug Analysis Playbook

Detailed query patterns for using mind_mcp and graph_mcp in bug impact analysis with specific function names, parameters, and expected outputs.

## mind_mcp Functions

### mind_mcp.get_system_status

**Purpose**: Check MCP system health and availability (preflight check)

**Parameters**:
```yaml
params:
  check_services:
    - knowledge_base
    - documentation_index
    - cache_status
```

**Expected Output**:
```json
{
  "status": "healthy|degraded|unavailable",
  "services": {
    "knowledge_base": "available",
    "documentation_index": "available",
    "cache_status": "enabled"
  },
  "latency_ms": 45
}
```

**Usage Example**:
```python
# Phase 0: Preflight check
result = mind_mcp.get_system_status()
if result["status"] == "unavailable":
    fallback_to_degraded_mode()
elif result["status"] == "degraded":
    log.warning("MCP degraded, reduced functionality")
```

---

### mind_mcp.query_knowledge_base

**Purpose**: Retrieve historical context, architectural decisions, and domain knowledge

**Parameters**:
```yaml
params:
  query: string                    # Natural language query
  context:
    repository: string             # Repository path
    branch: string                 # Git branch (default: main)
  filters:
    content_types:
      - adr                       # Architecture Decision Records
      - documentation
      - bug_reports
      - design_docs
    time_range: string             # e.g., "last_2_years"
    max_results: integer           # Default: 50
```

**Expected Output**:
```json
{
  "results": [
    {
      "type": "adr",
      "title": "ADR-012: Move to microservices architecture",
      "summary": "Decision to break up monolith...",
      "relevance_score": 0.92,
      "date": "2024-03-15",
      "confidence": "high"
    },
    {
      "type": "bug_report",
      "title": "Issue #2345: Similar error in payment module",
      "summary": "Previous null pointer exception...",
      "relevance_score": 0.87,
      "date": "2024-02-10",
      "confidence": "high"
    }
  ],
  "total_found": 12,
  "query_time_ms": 120
}
```

**Usage Examples**:

**Find related architectural decisions**:
```python
# Phase 1: Contextualize bug
result = mind_mcp.query_knowledge_base(
    query="payment processing architecture decisions null checks",
    context={
        "repository": "/path/to/repo",
        "branch": "main"
    },
    filters={
        "content_types": ["adr", "design_docs"],
        "time_range": "last_2_years",
        "max_results": 20
    }
)

# Extract ADRs mentioning the affected module
adrs = [r for r in result["results"] if r["type"] == "adr"]
```

**Historical bugs and fixes**:
```python
result = mind_mcp.query_knowledge_base(
    query="NullPointerException payment module previous bugs",
    context={"repository": repo_path},
    filters={
        "content_types": ["bug_reports"],
        "time_range": "last_3_years"
    }
)

# Look for patterns in previous fixes
similar_bugs = [r for r in result["results"] if r["relevance_score"] > 0.8]
```

**Domain knowledge**:
```python
result = mind_mcp.query_knowledge_base(
    query="payment processing business rules SLA compliance requirements",
    context={"repository": repo_path},
    filters={
        "content_types": ["documentation"],
        "max_results": 15
    }
)

# Extract business rules and constraints
business_rules = [r["summary"] for r in result["results"]]
```

---

### mind_mcp.search_documentation

**Purpose**: Search documentation for expected behavior and requirements

**Parameters**:
```yaml
params:
  query: string
  sources:
    - "README.md"
    - "docs/**"
    - "*.md"
  file_types:
    - markdown
    - text
  max_results: integer              # Default: 30
  highlight_matches: boolean        # Default: true
```

**Expected Output**:
```json
{
  "matches": [
    {
      "file": "docs/api/payments.md",
      "line": 45,
      "excerpt": "The payment API should return 400 for invalid card numbers...",
      "highlight": "<mark>should return 400</mark> for invalid...",
      "confidence": "high"
    }
  ],
  "total_files_searched": 156,
  "query_time_ms": 89
}
```

**Usage Example**:
```python
# Phase 1: Recover procedural context
result = mind_mcp.search_documentation(
    query="expected behavior payment validation error handling",
    sources=["README.md", "docs/**/*.md"],
    max_results=20
)

# Extract expected behavior for comparison with actual code
expected_behaviors = [m["excerpt"] for m in result["matches"]]
```

---

### mind_mcp.get_domain_knowledge

**Purpose**: Retrieve domain-specific concepts, business rules, and compliance requirements

**Parameters**:
```yaml
params:
  domain: string                   # e.g., "payment_processing", "user_management"
  concepts:
    - business_rules
    - sla
    - compliance
    - data_constraints
  depth: string                    # "overview" or "detailed"
```

**Expected Output**:
```json
{
  "domain": "payment_processing",
  "concepts": {
    "business_rules": [
      "Payment must be processed within 30 seconds",
      "Payment gateway requires PCI compliance",
      "Failed payments must be logged for audit"
    ],
    "sla": [
      "99.9% uptime for payment API",
      "Max 2% failure rate allowed"
    ],
    "compliance": [
      "PCI DSS Level 1 required",
      "GDPR data retention: 7 years for transactions"
    ]
  },
  "confidence": "high"
}
```

**Usage Example**:
```python
# Phase 3: Classify severity with domain context
result = mind_mcp.get_domain_knowledge(
    domain="payment_processing",
    concepts=["business_rules", "sla", "compliance"],
    depth="detailed"
)

# Use for severity justification
if result["concepts"]["sla"]:
    severity_boost = "High SLA impact (99.9% uptime requirement)"
```

---

## graph_mcp Functions

### graph_mcp.get_database_info

**Purpose**: Check graph database availability and metadata (preflight check)

**Parameters**:
```yaml
params: {}  # No parameters required
```

**Expected Output**:
```json
{
  "status": "ready",
  "database": "code_graph",
  "node_count": 156789,
  "edge_count": 456123,
  "last_updated": "2025-04-16T10:30:00Z",
  "features": {
    "call_graph": true,
    "data_flow": true,
    "test_coverage": true,
    "centrality": true
  }
}
```

---

### graph_mcp.find_nodes

**Purpose**: Locate bug position by semantic search or exact pattern matching

**Parameters**:
```yaml
params:
  search_type: string              # "semantic" or "exact"
  pattern: string                  # Function name, error message, or class name
  filters:
    file_types:
      - "*.py"
      - "*.js"
      - "*.ts"
      - "*.java"
    directories: []                # Restrict search to specific dirs
    exclude_dirs:                  # Exclude test dirs, etc.
      - "test/"
      - "tests/"
      - "__tests__"
  max_results: integer             # Default: 100
  include_context: boolean         # Include surrounding code (default: true)
  context_lines: integer           # Lines before/after (default: 5)
```

**Expected Output**:
```json
{
  "nodes": [
    {
      "id": "node_12345",
      "type": "function",
      "name": "processPayment",
      "file": "src/payments/processor.py",
      "line": 156,
      "context": "def processPayment(card_info):\n    # Null check missing\n    if card_info.valid:",
      "confidence": 0.95,
      "match_type": "semantic"
    }
  ],
  "total_found": 3,
  "search_time_ms": 234
}
```

**Usage Examples**:

**By error message**:
```python
# Phase 2: Locate bug by error message
result = graph_mcp.find_nodes(
    search_type="exact",
    pattern="NullPointerException",
    filters={
        "file_types": ["*.py", "*.java"],
        "exclude_dirs": ["test/"]
    },
    max_results=50
)

bug_location = result["nodes"][0]["file"] + ":" + str(result["nodes"][0]["line"])
```

**By stack trace**:
```python
# Parse stack trace and search bottom-up
stack_trace = """
  File "app.py", line 45, in <module>
    process_order()
  File "orders.py", line 123, in process_order
    validate_payment()
  File "payments.py", line 67, in validate_payment
    check_card_balance()
  File "payments.py", line 156, in check_card_balance
    raise NullPointerException
"""

# Extract function names from stack trace
functions = extract_functions_from_stack(stack_trace)  # ["check_card_balance", "validate_payment", "process_order"]

# Search for bottom-most frame first
for func in reversed(functions):
    result = graph_mcp.find_nodes(
        search_type="exact",
        pattern=func,
        filters={"file_types": ["*.py"]}
    )
    if result["nodes"]:
        bug_location = result["nodes"][0]
        break
```

**By suspected location**:
```python
# Semantic search for related code
result = graph_mcp.find_nodes(
    search_type="semantic",
    pattern="payment validation card processing error handling",
    filters={
        "file_types": ["*.py"],
        "directories": ["src/payments/"]
    },
    max_results=20
)

# Find most relevant match
bug_location = max(result["nodes"], key=lambda n: n["confidence"])
```

---

### graph_mcp.get_call_graph

**Purpose**: Trace upstream callers and downstream dependencies

**Parameters**:
```yaml
params:
  start_node: string               # Node ID or function name from find_nodes
  direction: string                # "incoming" (upstream) or "outgoing" (downstream)
  max_depth: integer               # Default: 5, Recommended: 3-5
  include_centrality: boolean      # Include PageRank and betweenness (default: true)
  limit: integer                   # Max nodes to return (default: 100)
  filters:
    node_types:                    # Restrict to specific node types
      - function
      - class
      - module
    exclude_test_code: boolean     # Exclude test functions (default: true)
```

**Expected Output**:
```json
{
  "start_node": "node_12345",
  "direction": "incoming",
  "depth_reached": 4,
  "nodes": [
    {
      "id": "node_23456",
      "name": "validatePayment",
      "type": "function",
      "depth": 1,
      "centrality": {
        "pagerank": 0.0234,
        "betweenness": 0.0123,
        "frequency": 156
      },
      "file": "src/payments/validator.py"
    }
  ],
  "paths": [
    {
      "path": ["node_23456", "node_34567", "node_12345"],
      "length": 2,
      "call_frequency": 89
    }
  ],
  "total_nodes_found": 23,
  "truncated": false,
  "query_time_ms": 456
}
```

**Usage Examples**:

**Trace upstream callers**:
```python
# Phase 2: Find who calls the buggy function
result = graph_mcp.get_call_graph(
    start_node=bug_location["id"],
    direction="incoming",
    max_depth=3,
    include_centrality=True,
    limit=100,
    filters={"exclude_test_code": True}
)

# Categorize callers
api_endpoints = [n for n in result["nodes"] if "api" in n["file"].lower()]
high_centrality = [n for n in result["nodes"] if n["centrality"]["pagerank"] > 0.01]
direct_callers = [n for n in result["nodes"] if n["depth"] == 1]

print(f"Found {len(direct_callers)} direct callers")
print(f"Found {len(api_endpoints)} API endpoints affected")
print(f"High centrality callers: {len(high_centrality)}")
```

**Trace downstream dependencies**:
```python
# Phase 2: Find what the buggy function calls
result = graph_mcp.get_call_graph(
    start_node=bug_location["id"],
    direction="outgoing",
    max_depth=3,
    include_centrality=True
)

# Identify risky dependencies
database_calls = [n for n in result["nodes"] if "db" in n["name"].lower() or "query" in n["name"].lower()]
external_apis = [n for n in result["nodes"] if "http" in n["name"].lower() or "request" in n["name"].lower()]
state_mutations = [n for n in result["nodes"] if "update" in n["name"].lower() or "delete" in n["name"].lower()]

print(f"Database calls: {len(database_calls)}")
print(f"External API calls: {len(external_apis)}")
print(f"State mutations: {len(state_mutations)}")
```

**Stop conditions**:
```python
# Implement stop conditions from playbook
def trace_upstream_with_limits(start_node):
    result = graph_mcp.get_call_graph(
        start_node=start_node,
        direction="incoming",
        max_depth=5,
        limit=100
    )

    # Filter by stop conditions
    filtered_nodes = []
    for node in result["nodes"]:
        # Stop at module boundaries
        if is_different_bounded_context(start_node, node):
            continue

        # Stop at low centrality
        if node["centrality"]["pagerank"] < 0.001:
            continue

        # Stop at API boundaries (but mark them)
        if is_api_endpoint(node):
            mark_as_integration_point(node)

        filtered_nodes.append(node)

    return filtered_nodes
```

---

### graph_mcp.trace_data_flow

**Purpose**: Track where corrupted/incorrect data propagates through the code

**Parameters**:
```yaml
params:
  start_node: string               # Node ID or function name
  variable: string                 # Variable name to track
  max_depth: integer               # Default: 3, Recommended: 2-4
  follow_return: boolean           # Track return values (default: true)
  follow_params: boolean           # Track function parameters (default: true)
  follow_assignments: boolean      # Track variable assignments (default: true)
```

**Expected Output**:
```json
{
  "variable": "paymentResult",
  "flows": [
    {
      "path": [
        {
          "node": "node_12345",
          "operation": "assignment",
          "line": 167,
          "code": "paymentResult = processPayment(card)"
        },
        {
          "node": "node_23456",
          "operation": "parameter",
          "line": 234,
          "code": "updateOrderStatus(paymentResult)"
        },
        {
          "node": "node_34567",
          "operation": "return",
          "line": 89,
          "code": "return paymentResult"
        }
      ],
      "destination": "api_response",
      "length": 3
    }
  ],
  "total_flows": 2,
  "query_time_ms": 345
}
```

**Usage Example**:
```python
# Phase 2: Track data corruption propagation
result = graph_mcp.trace_data_flow(
    start_node=bug_location["id"],
    variable="cardInfo",  # Variable that's null/incorrect
    max_depth=4,
    follow_return=True,
    follow_params=True
)

# Identify where corrupted data ends up
api_responses = [f for f in result["flows"] if f["destination"] == "api_response"]
database_writes = [f for f in result["flows"] if "db" in str(f.get("destination", ""))]
state_changes = [f for f in result["flows"] if "update" in str(f.get("destination", ""))]

print(f"Data flows to API responses: {len(api_responses)}")
print(f"Data flows to database: {len(database_writes)}")
print(f"Data flows to state changes: {len(state_changes)}")
```

---

### graph_mcp.find_test_coverage

**Purpose**: Find existing tests and identify coverage gaps

**Parameters**:
```yaml
params:
  target_functions: list           # List of function names or node IDs
  test_types:
    - unit
    - integration
    - e2e
  include_coverage_metrics: boolean # Include coverage percentages (default: true)
```

**Expected Output**:
```json
{
  "coverage": [
    {
      "function": "processPayment",
      "node_id": "node_12345",
      "tests": {
        "unit": ["test_process_payment_success.py", "test_process_payment_invalid.py"],
        "integration": ["test_payment_flow.py"],
        "e2e": []
      },
      "coverage_percentage": 78,
      "uncovered_scenarios": ["null_card_info", "timeout_handling"]
    }
  ],
  "overall_coverage": 65,
  "query_time_ms": 234
}
```

**Usage Example**:
```python
# Phase 2: Assess test coverage
affected_functions = get_all_affected_functions(bug_location)
result = graph_mcp.find_test_coverage(
    target_functions=affected_functions,
    test_types=["unit", "integration", "e2e"],
    include_coverage_metrics=True
)

# Find high-reach, low-coverage areas (HIGH RISK)
high_risk = []
for cov in result["coverage"]:
    if cov["coverage_percentage"] < 50 and get_centrality(cov["node_id"]) > 0.01:
        high_risk.append({
            "function": cov["function"],
            "coverage": cov["coverage_percentage"],
            "uncovered": cov["uncovered_scenarios"]
        })

print(f"HIGH RISK: {len(high_risk)} high-centrality functions with low coverage")
```

---

### graph_mcp.find_integration_points

**Purpose**: Identify external service calls and API boundaries

**Parameters**:
```yaml
params:
  node: string                     # Start node
  types:
    - http                          # HTTP/HTTPS requests
    - rpc                           # RPC calls
    - queue                         # Message queue operations
    - database                      # Database operations
  max_depth: integer               # Default: 3
```

**Expected Output**:
```json
{
  "integration_points": [
    {
      "type": "http",
      "function": "callPaymentGateway",
      "file": "src/payments/gateway.py",
      "line": 89,
      "target": "https://api.payment-gateway.com/v1/charge",
      "confidence": "high"
    },
    {
      "type": "database",
      "function": "savePaymentResult",
      "file": "src/payments/repository.py",
      "line": 123,
      "table": "payments",
      "operation": "insert",
      "confidence": "high"
    }
  ],
  "total_found": 5,
  "query_time_ms": 178
}
```

**Usage Example**:
```python
# Phase 2: Map integration points
result = graph_mcp.find_integration_points(
    node=bug_location["id"],
    types=["http", "rpc", "queue", "database"],
    max_depth=3
)

# Assess impact on external systems
external_apis = [ip for ip in result["integration_points"] if ip["type"] == "http"]
databases = [ip for ip in result["integration_points"] if ip["type"] == "database"]

print(f"External APIs affected: {len(external_apis)}")
print(f"Database operations affected: {len(databases)}")

# Check for cascading failures
for api in external_apis:
    print(f"  - {api['target']} (called by {api['function']})")
```

---

### graph_mcp.analyze_complexity

**Purpose**: Analyze code complexity metrics for fix complexity assessment

**Parameters**:
```yaml
params:
  nodes: list                     # List of node IDs or function names
  metrics:
    - cyclomatic                   # Cyclomatic complexity
    - coupling                     # Coupling score
    - cohesion                     # Cohesion score
    - lines_of_code                # LOC
```

**Expected Output**:
```json
{
  "complexity": [
    {
      "function": "processPayment",
      "node_id": "node_12345",
      "metrics": {
        "cyclomatic": 15,
        "coupling": 8,
        "cohesion": 0.6,
        "lines_of_code": 234
      },
      "complexity_level": "high"
    }
  ],
  "average_complexity": {
    "cyclomatic": 12,
    "coupling": 6,
    "cohesion": 0.7
  },
  "query_time_ms": 145
}
```

**Usage Example**:
```python
# Phase 4: Calculate fix complexity
result = graph_mcp.analyze_complexity(
    nodes=affected_functions,
    metrics=["cyclomatic", "coupling", "cohesion", "lines_of_code"]
)

# Assess overall complexity
avg_cyclomatic = result["average_complexity"]["cyclomatic"]
avg_coupling = result["average_complexity"]["coupling"]

if avg_cyclomatic > 15 or avg_coupling > 10:
    complexity = "Very Complex"
    effort = "1-2 weeks"
elif avg_cyclomatic > 10 or avg_coupling > 7:
    complexity = "Complex"
    effort = "1-3 days"
else:
    complexity = "Medium"
    effort = "2-8 hours"
```

---

### graph_mcp.get_module_inventory

**Purpose**: Get list of affected modules and team ownership

**Parameters**:
```yaml
params:
  affected_nodes: list            # List of affected node IDs
  include_ownership: boolean      # Include team ownership info (default: true)
  include_dependencies: boolean   # Include inter-module dependencies (default: true)
```

**Expected Output**:
```json
{
  "modules": [
    {
      "name": "payments",
      "path": "src/payments/",
      "functions_affected": 5,
      "ownership": {
        "team": "payments-team",
        "contact": "payments@company.com",
        "slack": "#payments-team"
      },
      "dependencies": ["orders", "users", "notifications"]
    }
  ],
  "total_modules": 3,
  "cross_team_impact": true,
  "query_time_ms": 234
}
```

**Usage Example**:
```python
# Phase 4: Assess coordination requirements
result = graph_mcp.get_module_inventory(
    affected_nodes=[n["id"] for n in affected_functions],
    include_ownership=True,
    include_dependencies=True
)

# Check for cross-team impact
if result["cross_team_impact"]:
    teams_involved = [m["ownership"]["team"] for m in result["modules"]]
    print(f"TEAMS INVOLVED: {', '.join(set(teams_involved))}")
    print(f"Coordination required across {len(set(teams_involved))} teams")
```

---

### graph_mcp.get_user_facing_surfaces

**Purpose**: Identify API endpoints and public interfaces affected

**Parameters**:
```yaml
params:
  nodes: list                     # List of affected node IDs
  surface_types:
    - api_endpoint                 # HTTP API endpoints
    - public_api                   # Library/public APIs
    - cli_command                  # CLI commands
    - webhook                      # Webhook handlers
```

**Expected Output**:
```json
{
  "surfaces": [
    {
      "type": "api_endpoint",
      "name": "POST /api/v1/payments",
      "file": "src/api/routes.py",
      "line": 45,
      "affected_by": ["processPayment"],
      "impact_severity": "high"
    }
  ],
  "total_surfaces": 2,
  "query_time_ms": 123
}
```

**Usage Example**:
```python
# Phase 3: Assess user-facing impact
result = graph_mcp.get_user_facing_surfaces(
    nodes=[n["id"] for n in affected_functions],
    surface_types=["api_endpoint", "public_api"]
)

user_impact = "HIGH" if result["total_surfaces"] > 0 else "LOW"
print(f"User-facing surfaces affected: {result['total_surfaces']}")
for surface in result["surfaces"]:
    print(f"  - {surface['name']} ({surface['impact_severity']} impact)")
```

---

## Query Sequences

### Standard Bug Analysis Sequence

```python
def analyze_bug_standard(bug_identifier, repo_path, scope="module"):
    """Standard sequence for most bug analyses"""

    # Phase 0: Preflight (30s)
    preflight_checks()

    # Phase 1: Contextualize (60s)
    context = mind_mcp.query_knowledge_base(
        query=f"{bug_identifier} historical context architecture decisions",
        context={"repository": repo_path}
    )

    # Phase 2: Locate and trace (90s)
    bug_location = graph_mcp.find_nodes(
        search_type="semantic",
        pattern=bug_identifier
    )

    callers = graph_mcp.get_call_graph(
        start_node=bug_location["nodes"][0]["id"],
        direction="incoming",
        max_depth=3
    )

    dependencies = graph_mcp.get_call_graph(
        start_node=bug_location["nodes"][0]["id"],
        direction="outgoing",
        max_depth=3
    )

    # Phase 3: Classify severity (45s)
    surfaces = graph_mcp.get_user_facing_surfaces(
        nodes=[bug_location["nodes"][0]["id"]]
    )

    # Phase 4: Calculate complexity (45s)
    complexity = graph_mcp.analyze_complexity(
        nodes=[bug_location["nodes"][0]["id"]]
    )

    # Phase 5: Generate report (60s)
    return generate_impact_report(context, callers, dependencies, surfaces, complexity)
```

### Critical Bug Sequence

```python
def analyze_bug_critical(bug_identifier, repo_path):
    """Fast sequence for critical/production bugs"""

    # Phase 0: Quick preflight (10s)
    quick_preflight()

    # Phase 1-2: Fast location and trace (60s)
    bug_location = graph_mcp.find_nodes(
        search_type="exact",
        pattern=bug_identifier,
        max_results=10
    )

    # Immediate impact assessment
    callers = graph_mcp.get_call_graph(
        start_node=bug_location["nodes"][0]["id"],
        direction="incoming",
        max_depth=2,  # Shallower for speed
        limit=50
    )

    integration_points = graph_mcp.find_integration_points(
        node=bug_location["nodes"][0]["id"],
        types=["http", "database"]
    )

    # Quick severity assessment
    severity = rapid_severity_assessment(callers, integration_points)

    return {
        "severity": severity,
        "api_affected": len([c for c in callers["nodes"] if "api" in c["file"]]),
        "integration_affected": len(integration_points["integration_points"]),
        "recommendation": "IMMEDIATE_ACTION_REQUIRED" if severity == "Critical" else "HIGH_PRIORITY"
    }
```

---

## Error Handling Patterns

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
        signal.alarm(0)  # Cancel alarm
        return result
    except TimeoutError as e:
        log.warning(f"MCP timeout: {e}")
        return {"timeout": True, "partial_results": {}}

# Usage
result = call_with_timeout(
    graph_mcp.get_call_graph,
    start_node=node_id,
    direction="incoming",
    timeout=30
)

if result.get("timeout"):
    # Handle partial results
    log.info("Returning partial traces due to timeout")
```

### Empty Results Handling

```python
def handle_empty_results(result, query_type):
    """Expand search scope when no results found"""

    if not result.get("nodes") and not result.get("results"):
        log.warning(f"No results for {query_type}, expanding scope")

        if query_type == "find_nodes":
            # Try semantic search instead of exact
            return graph_mcp.find_nodes(
                search_type="semantic",
                pattern=result["pattern"],
                max_results=result["max_results"] * 2
            )

        elif query_type == "call_graph":
            # Increase depth and limits
            return graph_mcp.get_call_graph(
                start_node=result["start_node"],
                direction=result["direction"],
                max_depth=result["max_depth"] + 2,
                limit=result["limit"] * 2
            )

    return result
```

---

## Performance Optimization

### Batch Processing

```python
def batch_process_nodes(nodes, batch_size=20):
    """Process nodes in batches to avoid overwhelming MCP"""

    results = []
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i+batch_size]

        # Parallel calls within batch
        batch_results = parallel_map(
            graph_mcp.analyze_complexity,
            batch,
            max_workers=3
        )

        results.extend(batch_results)

    return results
```

### Caching Strategy

```python
from functools import lru_cache
import time

class MCPCache:
    def __init__(self, ttl=300):
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
mcp_cache = MCPCache(ttl=300)  # 5 minute cache

def cached_query_knowledge_base(query):
    cache_key = f"kb:{query}"

    # Check cache
    cached = mcp_cache.get(cache_key)
    if cached:
        log.info(f"Cache hit for {cache_key}")
        return cached

    # Call MCP
    result = mind_mcp.query_knowledge_base(query=query)

    # Cache result
    mcp_cache.set(cache_key, result)

    return result
```

---

## Evidence Documentation

For each query, record:
- **Query**: What you searched for (function name, parameters)
- **Result**: What you found (summary of results)
- **Confidence**: How certain you are (High/Medium/Low)
- **Relevance**: How it impacts the analysis
- **Duration**: How long the query took
- **Cache Hit**: Whether result was cached

This creates a traceable chain from evidence to conclusions.
