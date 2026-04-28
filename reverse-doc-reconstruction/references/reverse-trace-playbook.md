# Reverse Trace Playbook

## 1. Objective

Trace source code into reusable documentation evidence, then transform that evidence into use case and detail design documents using MCP tools first, filesystem fallback second, with comprehensive security hardening, operational resilience, and evidence-based decision making.

## 2. MCP-First Tool Order with Detailed Signatures

### Phase 0: Preflight and Validation (Required, 30s timeout)

**Objective**: Verify MCP capabilities, validate inputs, and configure analysis environment.

#### Step 1: Input Validation (Required)

```yaml
validation_checks:
  repository_path:
    - repository_path must exist: os.path.exists(repo_path)
    - repository_path must be readable: os.access(repo_path, os.R_OK)
    - Block path traversal: reject if contains "../" or absolute path outside allowed dirs
    - Character whitelist: [a-zA-Z0-9_\-./]
    - Max length: 10000 characters

  output_path:
    - output_path must be creatable: os.access(parent_dir, os.W_OK)
    - output_path must be within allowed directories
    - Block path traversal: reject if contains "../"
    - Sufficient disk space: estimated_output_size * 2

  module_scope:
    - Module name format: /^[a-zA-Z0-9_-]+$/
    - Max length: 100 characters
    - Optional: verify module exists in repository

  depth_preference:
    - Allowed values: ["quick", "deep"]
    - Default: "quick"
```

#### Step 2: MCP Capability Verification

```python
# mind_mcp functions to verify
mind_mcp.list_qdrant_collections [required]
  params: {}
  timeout: 30s
  output:
    - collections: list of available collections
  failure_action: "fallback_to_filesystem_only"

mind_mcp.list_source_ids [optional]
  params:
    collection: string
  timeout: 30s
  output:
    - source_ids: list of document sources
  failure_action: "continue_without_source_filtering"

# graph_mcp functions to verify
graph_mcp.list_mcp_functions [required]
  params: {}
  timeout: 30s
  output:
    - functions: list of available MCP functions
  failure_action: "fallback_to_filesystem_only"

graph_mcp.list_parsers [required]
  params: {}
  timeout: 30s
  output:
    - parsers: list of language parsers available
  expected: "Check for target language parser (Python, Java, C#, etc.)"
  failure_action: "abort_with_error_if_parser_missing"

graph_mcp.list_databases [required]
  params: {}
  timeout: 30s
  output:
    - databases: list of graph databases
  failure_action: "fallback_to_filesystem_only"

graph_mcp.activate_project [required]
  params:
    project_id: string
    database: string
  timeout: 30s
  output:
    - success: boolean
  failure_action: "abort_with_error"
```

#### Step 3: Preflight Decision

```yaml
if all_mcp_checks_pass:
  proceed_to_phase_1

elif any_mcp_check_fails:
  fallback_to_filesystem_only_mode:
    steps:
      - "⚠️ MCP services unavailable or degraded"
      - "Running in filesystem-only mode with reduced confidence"
      - "Documentation will have gaps requiring manual verification"
      - "Do not use for compliance or critical documentation without review"

    logging:
      - "Running in FILESYSTEM-ONLY MODE: MCP unavailable"
      - "Analysis limited to filesystem tools only"
      - "Evidence confidence: LOW for all items"
      - "Manual verification required for completeness"
```

### Phase 1: Business Context Discovery from mind_mcp (180s timeout)

**Objective**: Extract business vocabulary, domain entities, and business rules from knowledge base.

#### 1.1 Discover Business Vocabulary

```python
mind_mcp.hybrid_search [required]
  params:
    query: "use case OR business flow OR user scenario OR workflow OR process"
    collection: "{selected_collection}"
    limit: 20
  timeout: 45s
  output:
    results:
      - id: paragraph_id
        score: relevance_score_0_to_1
        metadata:
          source_file: string
          source_type: "requirement" | "design" | "adr" | "ticket"
    expected:
      - "Business vocabulary definitions"
      - "User role definitions"
      - "Business process descriptions"

  # Example queries for business context
  example_queries:
    - "user authentication flow"
    - "payment processing workflow"
    - "order fulfillment process"
    - "data validation rules"
    - "error handling requirements"

  error_handling:
    on_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty context"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial business context retrieved, continuing with available data"
```

#### 1.2 Extract Domain Entities

```python
mind_mcp.hybrid_search [required]
  params:
    query: "{entity_name} OR {aggregate_root} OR {value_object}"
    collection: "{selected_collection}"
    limit: 20
  timeout: 45s
  output:
    results:
      - domain_entities:
          name: string
          type: "entity" | "aggregate" | "value_object"
          relationships: []
    expected:
      - "Domain entity definitions"
      - "Entity relationships"
      - "Business rules per entity"

  # Example domain entity queries
  example_queries:
    - "customer OR user OR account"
    - "order OR transaction OR payment"
    - "product OR inventory OR catalog"
    - "state machine OR lifecycle OR status transition"

  error_handling:
    on_timeout:
      action: "continue_with_available_entities"
      log: "Domain entity discovery timeout, using available entities"
```

#### 1.3 Extract Business Rules and Constraints

```python
mind_mcp.sequential_search [optional]
  params:
    query: "step by step OR user journey OR transaction flow"
    collection: "{selected_collection}"
    limit: 10
  timeout: 45s
  output:
    results:
      - ordered_procedures:
          steps: []
          sequence: integer
    expected:
      - "Ordered procedure steps"
      - "Transaction flows"
      - "State transitions"

  error_handling:
    on_timeout:
      action: "skip_procedural_extraction"
      log: "Sequential search timeout, skipping procedural rules"
      continue: true
```

#### 1.4 Get Detailed Content

```python
mind_mcp.get_paragraph_text [required]
  params:
    paragraph_ids: ["{ids_from_hybrid_search}"]
  timeout: 30s
  output:
    text:
      - id: paragraph_id
        content: string
        citation: string
    expected:
      - "Full paragraph content with citations"
      - "Source references for traceability"

  # Apply sensitive data redaction
  redaction_rules:
    - API keys: /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
    - Passwords: /password.*/gi → '[REDACTED_PASSWORD]'
    - Secrets: /secret.*/gi → '[REDACTED_SECRET]'
    - Tokens: /token.*/gi → '[REDACTED_TOKEN]'
    - License keys: /license.*/gi → '[REDACTED_LICENSE]'
    - IP addresses: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'
    - Hostnames: /\b[a-zA-Z0-9.-]+\.(?:com|net|org|io)\b/gi → '[REDACTED_HOST]'
    - URLs with creds: /\b[\w-]+:\/\/[\w-]+:[\w-]+@/gi → '[REDACTED_URL]'
    - Connection strings: /\bpostgresql:\/\/[^\s]+\b/gi → 'postgresql://[REDACTED]'
    - Email addresses: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED_EMAIL]'
    - Phone numbers: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g → '[REDACTED_PHONE]'

  error_handling:
    on_timeout:
      action: "use_search_snippets"
      log: "get_paragraph_text timeout, using search snippets"
      continue: true
```

#### 1.5 Connect Entities Across Documents

```python
mind_mcp.query_graph_rag_relation [optional]
  params:
    entity: "{domain_entity}"
    relation_types: ["relates_to", "depends_on", "contains"]
  timeout: 45s
  output:
    relations:
      - source: string
        target: string
        relation_type: string
        evidence: string
    expected:
      - "Cross-document entity relationships"
      - "Dependency mappings"

  error_handling:
    on_timeout:
      action: "skip_relation_extraction"
      log: "Relation extraction timeout, using entity co-occurrence"
      continue: true
```

#### 1.6 Cache Business Context

```yaml
cache_output:
  file: "mcp_business_context_cache.json"
  ttl: 900  # 15 minutes
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    collections: ["{collection_ids}"]
    evidence_items:
      - id: unique_id
        type: business_vocabulary | domain_entity | business_rule | constraint
        source: mind_mcp
        ref: paragraph_id
        confidence: high | medium | low
        content: summarized_content (redacted)
    redaction_log:
      - "Redacted {count} API keys"
      - "Redacted {count} passwords"
      - "Redacted {count} connection strings"

  progress_reporting:
    phase_complete:
      - "Phase 1 complete: Business context discovery"
      - "  Duration: {actual_time}s"
      - "  Business terms: {terms_count}"
      - "  Domain entities: {entities_count}"
      - "  Business rules: {rules_count}"
      - "  Evidence items: {evidence_count}"
```

### Phase 2: Entry Point Discovery from graph_mcp (240s timeout)

**Objective**: Build baseline coverage map by discovering all entry points and module structure.

#### 2.1 Activate Project Context

```python
graph_mcp.activate_project [required]
  params:
    project_id: "{project_id}"
    database: "{database}"
  timeout: 30s
  output:
    success: boolean
    project_info:
      name: string
      language: string
      parser: string

  error_handling:
    on_failure:
      action: "abort_with_error"
      log: "Failed to activate project, aborting reconstruction"
```

#### 2.2 Discover All Entry Points

```python
graph_mcp.list_up_entrypoint [required]
  params:
    file_pattern: "{module_pattern}/*.{extension}"
      # Examples:
      # - "src/**/*.py" for Python
      # - "src/main/java/**/*.java" for Java
      # - "Controllers/**/*.cs" for C#
    limit: 200
  timeout: 60s
  output:
    entry_points:
      - id: node_id
        name: string
        file: string
        type: "function" | "method" | "api_endpoint"
        signature: string
    expected:
      - "All entry points in scope"
      - "API endpoints, main functions, handlers"

  # Example patterns by language
  language_patterns:
    Python:
      - "src/**/*.py"
      - "handlers/*_handler.py"
      - "views/*.py"
      - "routes/*.py"
    Java:
      - "src/main/java/**/*.java"
      - "**/*Controller.java"
      - "**/*Service.java"
    C#:
      - "**/*Controller.cs"
      - "**/*Handler.cs"
      - "Controllers/*.cs"
    JavaScript/TypeScript:
      - "src/**/*.ts"
      - "routes/*.js"
      - "api/*.js"

  error_handling:
    on_timeout:
      action: "fallback_to_filesystem_search"
      log: "graph_mcp entry discovery timeout, using rg/grep"
      continue: true

      # Filesystem fallback commands
      fallback_commands:
        - rg --files -g "{module_pattern}" | head -200
        - rg "def (handle_|process_|execute_|on_)" {module_pattern}
        - rg "@(RequestMapping|GetMapping|PostMapping)" {module_pattern}
```

#### 2.3 Explore Module Structure

```python
graph_mcp.explore_graph [required]
  params:
    query: "{module_or_function_name}"
    limit: 100
  timeout: 60s
  output:
    nodes:
      - id: node_id
        name: string
        type: "function" | "class" | "module"
        file: string
    edges:
      - from: node_id
        to: node_id
        type: "calls" | "contains" | "imports"
    expected:
      - "Module structure"
      - "Function/class inventory"
      - "Dependency relationships"

  # Context control for large modules
  context_control:
    max_results: 100
    if_results_truncated:
      - "Summarize first 100 results"
      - "Ask user for specific sub-module focus"
      - "Process sub-modules sequentially"

  error_handling:
    on_timeout:
      action: "return_partial_results"
      log: "Graph exploration timeout, returning partial module structure"
      continue: true
```

#### 2.4 Search for Entry Points by Pattern

```python
graph_mcp.search_functions [required]
  params:
    query: "Handle* OR Process* OR Execute* OR On* OR *Controller OR *Handler"
    limit: 50
  timeout: 45s
  output:
    functions:
      - id: node_id
        name: string
        file: string
        signature: string
    expected:
      - "Entry point functions"
      - "Controller/handler methods"

  # Additional patterns for comprehensive discovery
  supplementary_queries:
    - "main OR start OR init"
    - "service OR repository OR adapter"
    - "endpoint OR route"

  error_handling:
    on_timeout:
      action: "use_list_up_entrypoint_results_only"
      log: "Function search timeout, using list_up_entrypoint results"
      continue: true
```

#### 2.5 Capture Baseline Metrics

```yaml
baseline_metrics:
  total_functions: "{count from explore_graph}"
  total_entry_points: "{count from list_up_entrypoint}"
  total_classes: "{count from explore_graph where type=class}"
  ipc_partners: "{discovered from graph edges}"
  files_in_scope: "{count from filesystem scan}"
  modules_discovered: "{count from explore_graph}"

cache_output:
  file: "mcp_tracing_cache.json"
  ttl: 1200  # 20 minutes
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    parser: "{parser}"
    evidence_items:
      - id: node_id
        type: entrypoint | function | class | module | ipc_link
        source: graph_mcp
        metadata:
          name: string
          file: string
          signature: string
        confidence: high | medium | low

  progress_reporting:
    phase_complete:
      - "Phase 2 complete: Entry point discovery"
      - "  Duration: {actual_time}s"
      - "  Entry points: {entry_count}"
      - "  Total functions: {function_count}"
      - "  Total classes: {class_count}"
      - "  IPC partners: {ipc_count}"
```

### Phase 3: Call Flow Tracing from graph_mcp (360s timeout)

**Objective**: Trace main flows, alternate branches, and error handling for each entry point.

#### 3.1 Trace Main Happy Path

```python
graph_mcp.trace_flow [required]
  params:
    start_node: "{entry_point_id}"
    max_depth: 5
    timeout: 60s
  output:
    flow:
      - step: integer
        node_id: string
        function_name: string
        file: string
        call_type: "direct" | "indirect" | "ipc"
    expected:
      - "Happy path execution trace"
      - "Function call sequence"
      - "Module boundaries crossed"

  # Context control for deep flows
  context_control:
    max_depth: 5
    if_depth_exceeded:
      - "Summarize top 5 levels"
      - "Mark deeper levels as [DEEP_TRACE_REQUIRED]"
      - "Ask user for specific deep trace target"

  # Batch processing for multiple entry points
  batch_processing:
    batch_size: 20  # Trace 20 entry points at a time
    user_confirmation_required: true
    prompt: "Tracing {batch_size} entry points, continue?"

  error_handling:
    on_timeout:
      action: "trace_main_flows_only"
      log: "Flow trace timeout for {entry_point}, skipping to next entry point"
      continue: true
    on_no_path_found:
      action: "mark_as_stub"
      log: "No flow found for {entry_point}, marking as stub requiring manual trace"
```

#### 3.2 Discover Alternate Paths

```python
graph_mcp.find_paths [required]
  params:
    start_node: "{entry_point_id}"
    end_node: "{domain_node_id}"
    max_paths: 10
  timeout: 60s
  output:
    paths:
      - path_id: integer
        nodes: [node_ids]
        length: integer
        type: "main" | "alt" | "error"
    expected:
      - "Multiple execution paths"
      - "Alternate routes through code"
      - "Conditional branches"

  # Example path discoveries
  path_examples:
    authentication_flow:
      - entry: "login_handler"
      - paths:
          - success: "login_handler → validate_credentials → create_session → redirect"
          - failure: "login_handler → validate_credentials → log_failure → redirect_login"

  error_handling:
    on_timeout:
      action: "skip_alternate_paths"
      log: "Alternate path discovery timeout for {entry_point}, using main path only"
      continue: true
```

#### 3.3 Expand Domain Entity Context

```python
graph_mcp.query_subgraph [required]
  params:
    node_id: "{domain_entity_id}"
    depth: 3
    limit: 50
  timeout: 60s
  output:
    subgraph:
      nodes:
        - id: node_id
          name: string
          type: string
      edges:
        - from: node_id
          to: node_id
          type: string
    expected:
      - "Domain entity context"
      - "Related functions"
      - "Data flow relationships"

  # Use cases for subgraph expansion
  subgraph_use_cases:
    domain_entities:
      - "Expand around Customer entity"
      - "Discover all Customer-related operations"
      - "Map Customer state transitions"

    data_access:
      - "Expand around Repository classes"
      - "Discover all database operations"
      - "Map query patterns"

  error_handling:
    on_timeout:
      action: "use_shallow_subgraph"
      log: "Subgraph expansion timeout for {node_id}, using depth=1"
      continue: true
```

#### 3.4 Discover Error Handling

```python
graph_mcp.search_functions [required]
  params:
    query: "error* OR timeout* OR retry* OR abort* OR invalid* OR exception*"
    limit: 50
  timeout: 45s
  output:
    functions:
      - id: node_id
        name: string
        file: string
        signature: string
    expected:
      - "Error handling functions"
      - "Exception handlers"
      - "Retry logic"

  # Error handling categories
  error_categories:
    validation_errors: "validate* OR check* OR verify* OR invalid*"
    timeout_errors: "timeout* OR deadline* OR expires*"
    retry_errors: "retry* OR backoff* OR attempt*"
    abort_errors: "abort* OR fail* OR terminate*"
    exception_handlers: "catch* except* raise* throw*"

  error_handling:
    on_timeout:
      action: "skip_error_branch_discovery"
      log: "Error function search timeout, marking error paths as [MANUAL_TRACE_REQUIRED]"
      continue: true
```

#### 3.5 Resolve Indirect Calls

```python
graph_mcp.list_possible_calls [optional]
  params:
    node_id: "{function_id}"
  timeout: 45s
  output:
    possible_calls:
      - target_node_id: string
        target_function: string
        call_type: "virtual" | "callback" | "delegate"
    expected:
      - "Dynamic dispatch targets"
      - "Virtual function calls"
      - "Interface method calls"

  # Use cases for indirect call resolution
  indirect_call_scenarios:
    polymorphism:
      - "Virtual method calls in C++/Java/C#"
      - "Interface method dispatch"
      - "Abstract class implementations"

    callbacks:
      - "Function pointer calls in C/C++"
      - "Callback handlers"
      - "Event handlers"

  error_handling:
    on_timeout:
      action: "mark_indirect_calls_as_unresolved"
      log: "Indirect call resolution timeout for {function_id}, marking as [INDIRECT_CALL]"
      continue: true
```

#### 3.6 Cache Flow Traces

```yaml
cache_output:
  file: "mcp_tracing_cache.json"
  ttl: 1200  # 20 minutes
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    flow_traces:
      - entry_point_id: string
        happy_path: [node_ids]
        alternate_paths: [[node_ids]]
        error_paths: [node_ids]
        unresolved_nodes: [node_ids]
        trace_confidence: high | medium | low

  progress_reporting:
    task_progress:
      - "Tracing entry points: {current}/{total} entry points"
      - "Main flows: {main_flow_count} traced"
      - "Alternate paths: {alt_path_count} discovered"
      - "Error paths: {error_path_count} discovered"

    phase_complete:
      - "Phase 3 complete: Call flow tracing"
      - "  Duration: {actual_time}s"
      - "  Entry points traced: {entry_count}"
      - "  Main flows: {main_flows}"
      - "  Alternate paths: {alt_paths}"
      - "  Error paths: {error_paths}"
      - "  Unresolved edges: {unresolved_count}"
```

### Phase 4: Use Case Consolidation (180s timeout)

**Objective**: Align business context (mind_mcp) with code flows (graph_mcp) to create traceable use cases.

#### 4.1 Align Business Terms with Code Flows

```yaml
alignment_process:
  steps:
    1. For each business entity (from mind_mcp):
       - Find related code functions (from graph_mcp)
       - Map business rules to code behavior
       - Identify entry points that implement business flows

    2. For each business process (from mind_mcp):
       - Trace corresponding code execution path
       - Map process steps to function calls
       - Identify error handling and alternate paths

    3. Apply conflict resolution rules:
       - For code structure: Trust graph_mcp over mind_mcp
       - For business intent: Trust mind_mcp over graph_mcp
       - For recent changes: Trust filesystem over MCP
       - For historical context: Trust mind_mcp (archival)

  example_alignment:
    business_entity: "Customer"
    mind_mcp_evidence:
      - "Customer has email and password"
      - "Customer can place orders"
    graph_mcp_evidence:
      - "Customer class in models/customer.py"
      - "create_order() function in services/order.py"
    aligned_use_case:
      - "UC001: Customer places order"
      - "Entry: POST /api/orders (create_order)"
      - "Business rule: Customer must be authenticated"
```

#### 4.2 Verify Use Case Completeness

```yaml
uc_verification_criteria:
  required_elements:
    business_purpose:
      source: mind_mcp
      required: true
      check: "UC has clear business goal from business context"

    code_entry_point:
      source: graph_mcp
      required: true
      check: "UC has at least one verified entry point"

    flow_evidence:
      source: graph_mcp
      required: true
      check: "UC has traced main flow from trace_flow"

    error_handling:
      source: graph_mcp | filesystem
      required: false  # Optional for simple UCs
      check: "UC has error paths documented or marked as [MANUAL]"

  confidence_rules:
    high_confidence:
      - "mind_mcp and graph_mcp agree"
      - "Direct trace_flow from entry point"
      - "Error paths documented"

    medium_confidence:
      - "Single MCP source"
      - "Partial flow trace"
      - "Error paths marked [MANUAL]"

    low_confidence:
      - "Filesystem only"
      - "Conflicting MCP sources"
      - "Unresolved edges in flow"
```

#### 4.3 Apply Use Case Taxonomy

```yaml
taxonomy_tags:
  ROLE:
    ENTRYPOINT: "API endpoints, main functions, event handlers"
    CONTROLLER: "Request handlers, orchestration logic"
    SERVICE: "Business logic, domain operations"
    REPOSITORY: "Data access, persistence operations"
    ADAPTER: "External integrations, IPC clients"
    UTILITY: "Helper functions, shared logic"

  FLOW:
    MAIN: "Happy path, primary execution flow"
    ALT: "Alternate paths, conditional branches"
    ERROR: "Error handling, exception flows"
    TIMEOUT: "Timeout handling, retry logic"
    RETRY: "Retry attempts, backoff strategies"

  RISK:
    HIGH: "Touches auth, payment, critical state, PII"
    MEDIUM: "Business logic, data modification"
    LOW: "Read operations, calculations"

  STATE:
    MUTATES: "Modifies database or external state"
    PURE: "No side effects, read-only"
    I/O: "File or network operations"
    CACHE: "Cache operations"

  # Apply tags to each UC
  tag_assignment:
    uc001_customer_places_order:
      ROLE: [ENTRYPOINT, SERVICE, REPOSITORY]
      FLOW: [MAIN, ALT, ERROR]
      RISK: HIGH
      STATE: MUTATES
      evidence: "Handles payment processing"
```

#### 4.4 Update Use Case Artifacts

```yaml
output_files:
  usecase_list:
    file: "usecase_list_{module}.md"
    content:
      - uc_id: "UC001"
        name: "Customer places order"
        role: [ENTRYPOINT, SERVICE]
        risk: HIGH
        evidence_sources: [mind_mcp, graph_mcp]
        entry_points: ["POST /api/orders"]

  usecase_metrics:
    file: "usecase_metrics_{module}.md"
    content:
      total_use_cases: integer
      high_risk_ucs: integer
      medium_risk_ucs: integer
      low_risk_ucs: integer
      mcp_evidence_percentage: float
      entry_coverage_percentage: float

  individual_uc:
    file: "uc001_{module}.md"
    content:
      uc_id: "UC001"
      name: string
      actors: [from mind_mcp]
      entry_points: [from graph_mcp]
      main_flow: [from graph_mcp trace_flow]
      alt_flows: [from graph_mcp find_paths]
      error_flows: [from graph_mcp search_functions]
      evidence_provenance:
        - business_rules: [mind_mcp paragraph_ids]
        - code_traces: [graph_mcp node_ids]
      confidence: high | medium | low

  progress_reporting:
    phase_complete:
      - "Phase 4 complete: Use case consolidation"
      - "  Duration: {actual_time}s"
      - "  Use cases discovered: {uc_count}"
      - "  High-risk UCs: {high_risk_count}"
      - "  MCP evidence coverage: {mcp_coverage}%"
```

### Phase 5: UC Artifact Generation with Diagrams (300s timeout)

**Objective**: Generate detailed use case artifacts with sequence and class diagrams.

#### 5.1 Generate Sequence Diagrams

```yaml
sequence_diagram_generation:
  source: graph_mcp trace_flow results
  format: Mermaid sequence diagram

  diagram_structure:
    participants:
      - From graph_mcp: functions, classes, modules
      - From mind_mcp: actors, external systems

    messages:
      - From trace_flow: function calls
      - Sync calls: "→"
      - Async calls: "→>"
      - Return values: "-->"

    alt_blocks:
      - From find_paths: alternate paths
      - Error blocks: From error path discovery

  # Example Mermaid diagram
  example_diagram: |
    sequenceDiagram
      actor User
      participant API as POST /api/orders
      participant Service as OrderService
      participant Repo as OrderRepository
      participant DB as Database

      User->>API: CreateOrderRequest
      API->>Service: createOrder(request)
      Service->>Repo: validateCustomer(customerId)
      Repo->>DB: SELECT * FROM customers
      DB-->>Repo: customer
      Repo-->>Service: customer

      alt Customer not found
          Service-->>API: 404 Not Found
          API-->>User: Error response
      else Customer exists
          Service->>Repo: createOrder(order)
          Repo->>DB: INSERT INTO orders
          DB-->>Repo: order
          Repo-->>Service: order
          Service-->>API: 201 Created
          API-->>User: OrderResponse
      end

  evidence_links:
    participants: "From graph_mcp node_ids"
    messages: "From trace_flow edge_ids"
    alt_blocks: "From find_paths path_ids"

  error_handling:
    on_diagram_too_large:
      action: "split_into_subdiagrams"
      log: "Sequence diagram too large, splitting by module"
      continue: true
```

#### 5.2 Generate Class Diagrams

```yaml
class_diagram_generation:
  source: graph_mcp query_subgraph + explore_graph
  format: Mermaid class diagram

  diagram_structure:
    classes:
      - From graph_mcp: class nodes
      - Attributes: From function signatures
      - Methods: From function nodes

    relationships:
      - inheritance: From graph_mcp extends edges
      - composition: From graph_mcp contains edges
      - aggregation: From ownership patterns
      - dependency: From call graph edges

  # Example Mermaid diagram
  example_diagram: |
    classDiagram
      class Customer {
          +id: UUID
          +email: string
          +password_hash: string
          +validate() boolean
          +authenticate(password) boolean
      }

      class Order {
          +id: UUID
          +customerId: UUID
          +items: List~OrderItem~
          +status: OrderStatus
          +addItem(item) void
          +calculateTotal() Money
      }

      class OrderRepository {
          +findById(id) Order
          +save(order) void
          +findByCustomer(customerId) List~Order~
      }

      class OrderService {
          +createOrder(request) Order
          +validateCustomer(customerId) boolean
      }

      Customer "1" --> "many" Order : places
      OrderService --> OrderRepository : uses
      OrderRepository --> Order : manages

  evidence_links:
    classes: "From graph_mcp class node_ids"
    methods: "From graph_mcp function node_ids"
    relationships: "From graph_mcp edge_ids"

  error_handling:
    on_too_many_classes:
      action: "filter_to_domain_entities"
      log: "Too many classes, filtering to domain entities only"
      continue: true
```

#### 5.3 Generate Activity Diagrams

```yaml
activity_diagram_generation:
  source: graph_mcp trace_flow + find_paths
  format: Mermaid activity diagram

  diagram_structure:
    actions:
      - From trace_flow: function calls
      - From find_paths: alternate branches

    decisions:
      - From conditional branches
      - From error handling paths

    parallel:
      - From concurrent execution patterns

  # Example Mermaid diagram
  example_diagram: |
    activityDiagram
      start
      :Receive CreateOrderRequest;

      :Validate customer;
      if (Customer exists?) then (yes)
        :Create order entity;
        :Calculate total;
        :Save to database;

        if (Payment successful?) then (yes)
          :Update order status;
          :Send confirmation email;
          :Return OrderResponse;
        else (no)
          :Log payment failure;
          :Return payment error;
        endif

      else (no)
        :Log validation failure;
        :Return validation error;
      endif

      stop

  evidence_links:
    actions: "From trace_flow node_ids"
    decisions: "From find_paths path_ids"

  error_handling:
    on_activity_too_complex:
      action: "simplify_to_main_flow"
      log: "Activity diagram too complex, simplifying to main flow"
      continue: true
```

#### 5.4 Evidence Provenance in Artifacts

```yaml
evidence_provenance:
  every_claim_must_include:
    source: "mind_mcp | graph_mcp | filesystem"
    ref: "paragraph_id | node_id | file_path"
    confidence: "high | medium | low"
    redaction_applied: boolean

  # Example evidence block
  example_evidence_block: |
    ## Business Rules

    **Rule 1**: Customer must be authenticated to place order
    ```yaml
    evidence:
      source: mind_mcp
      ref: paragraph_12345
      confidence: high
      quote: "Only authenticated customers can place orders"
    ```

    **Rule 2**: Order total must be positive
    ```yaml
    evidence:
      source: graph_mcp
      ref: node_67890 (OrderService.calculateTotal)
      confidence: high
      code: "if (total <= 0) throw InvalidOrderException()"
    ```

    **Rule 3**: Payment processing timeout is 30 seconds
    ```yaml
    evidence:
      source: graph_mcp
      ref: node_11111 (PaymentService.processPayment)
      confidence: high
      code: "timeout=30s"
    ```

  progress_reporting:
    task_progress:
      - "Generating UC artifacts: {current}/{total} UCs"
      - "Sequence diagrams: {seq_diagram_count}"
      - "Class diagrams: {class_diagram_count}"
      - "Activity diagrams: {activity_diagram_count}"

    phase_complete:
      - "Phase 5 complete: UC artifact generation"
      - "  Duration: {actual_time}s"
      - "  UC artifacts generated: {uc_count}"
      - "  Sequence diagrams: {seq_count}"
      - "  Class diagrams: {class_count}"
      - "  Activity diagrams: {activity_count}"
```

### Phase 6: Detail Design Derivation (600s timeout)

**Objective**: Convert validated UCs to detail design artifacts using deterministic mapping rules.

#### 6.1 Screen Design from UC Actors + Entry Points

```yaml
screen_design_mapping:
  source:
    - actors: from mind_mcp business context
    - entry_points: from graph_mcp entry discovery
    - request_response_shapes: from function signatures

  output_sections:
    screens:
      - screen_name: string
        actor: string
        entry_point: string
        fields:
          - field_name: string
            type: string
            validation: string
            evidence: node_id

    navigation:
      - from_screen: string
        to_screen: string
        trigger: string
        evidence: node_id

  # Example screen design
  example_screen_design: |
    ## Create Order Screen

    **Actor**: Customer
    **Entry Point**: POST /api/orders

    ### Input Fields
    | Field | Type | Validation | Evidence |
    |-------|------|------------|----------|
    | customerId | UUID | Required, exists | node_123 |
    | items | array | Required, min=1 | node_124 |
    | itemId | UUID | Required | node_125 |
    | quantity | integer | Required, min=1 | node_126 |

    ### Navigation
    - From: Order List Screen
    - Trigger: Click "New Order" button
    - Evidence: node_127 (OrderController.createOrder)

  consistency_checks:
    - every_field_has_evidence: true
    - every_validation_is_traced: true
    - every_navigation_is_traced: true
```

#### 6.2 API Process Design from UC Main/Alt/Error Flows

```yaml
api_design_mapping:
  source:
    - main_flow: from graph_mcp trace_flow
    - alt_flows: from graph_mcp find_paths
    - error_flows: from graph_mcp error search
    - critical_checkpoints: from flow analysis

  output_sections:
    api_endpoints:
      - endpoint: string
        method: string
        request_schema: object
        response_schema: object
        auth_required: boolean
        rate_limit: string
        critical_checkpoints: []
        evidence: [node_ids]

    checkpoint_details:
      - checkpoint: string
        type: "auth" | "validation" | "business_rule" | "audit"
        implementation: string
        evidence: node_id

  # Example API design
  example_api_design: |
    ## POST /api/orders

    ### Request
    ```json
    {
      "customerId": "uuid",
      "items": [
        {"itemId": "uuid", "quantity": 1}
      ]
    }
    ```
    Evidence: node_130 (OrderController.createOrder signature)

    ### Response (200 OK)
    ```json
    {
      "orderId": "uuid",
      "status": "PENDING",
      "total": 100.00
    }
    ```
    Evidence: node_131 (Order entity)

    ### Critical Checkpoints
    1. **Authentication**: Customer must be logged in
       Evidence: node_132 (AuthMiddleware)

    2. **Validation**: customerId must exist
       Evidence: node_133 (OrderService.validateCustomer)

    3. **Business Rule**: Customer cannot have unpaid orders
       Evidence: node_134 (OrderService.checkUnpaidOrders)

    4. **Audit**: Log order creation
       Evidence: node_135 (AuditService.logOrderCreated)

    ### Error Responses
    - 400 Invalid input
    - 401 Unauthorized
    - 404 Customer not found
    - 409 Business rule violation (unpaid orders)

  consistency_checks:
    - every_api_field_exists_in_uc: true
    - every_checkpoint_has_implementation: true
    - every_error_case_is_documented: true
```

#### 6.3 Table Design from UC Domain Entities

```yaml
table_design_mapping:
  source:
    - domain_entities: from mind_mcp entity discovery
    - data_fields: from graph_mcp class attributes
    - query_and_state_transitions: from flow analysis

  output_sections:
    tables:
      - table_name: string
        columns:
          - column_name: string
            type: string
            constraints: string
            nullable: boolean
            evidence: node_id
        indexes: []
        foreign_keys: []
        evidence: [node_ids]

  # Example table design
  example_table_design: |
    ## orders table

    ### Columns
    | Column | Type | Constraints | Nullable | Evidence |
    |--------|------|-------------|----------|----------|
    | id | UUID | PK | No | node_140 |
    | customer_id | UUID | FK → customers.id | No | node_141 |
    | status | VARCHAR(50) | | No | node_142 |
    | total | DECIMAL(10,2) | | No | node_143 |
    | created_at | TIMESTAMP | | No | node_144 |
    | updated_at | TIMESTAMP | | No | node_145 |

    ### Indexes
    - idx_orders_customer_id ON (customer_id)
      Evidence: node_146 (OrderRepository.findByCustomer)
    - idx_orders_status ON (status)
      Evidence: node_147 (OrderRepository.findByStatus)

    ### Foreign Keys
    - FK_orders_customer_id: customer_id → customers(id)
      Evidence: node_148 (Order.customer association)

  consistency_checks:
    - every_column_has_evidence: true
    - every_index_maps_to_query: true
    - every_foreign_key_maps_to_association: true
```

#### 6.4 SQL Design from UC Query Patterns

```yaml
sql_design_mapping:
  source:
    - query_patterns: from graph_mcp repository function calls
    - state_transitions: from flow analysis
    - data_filters: from function parameters

  output_sections:
    queries:
      - query_name: string
        sql: string
        parameters: []
        usage_context: string
        evidence: node_id

  # Example SQL design
  example_sql_design: |
    ## Query: findOrderById

    ### SQL
    ```sql
    SELECT o.*, c.email as customer_email
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    WHERE o.id = :orderId
    ```

    ### Parameters
    - orderId: UUID

    ### Usage Context
    - Called by: OrderService.getOrder
    - Used in: UC001 Get Order Details
    - Evidence: node_150 (OrderRepository.findById)

    ## Query: createOrder

    ### SQL
    ```sql
    INSERT INTO orders (id, customer_id, status, total, created_at, updated_at)
    VALUES (:orderId, :customerId, 'PENDING', :total, NOW(), NOW())
    RETURNING id
    ```

    ### Parameters
    - orderId: UUID
    - customerId: UUID
    - total: DECIMAL

    ### Usage Context
    - Called by: OrderService.createOrder
    - Used in: UC002 Customer places order
    - Evidence: node_151 (OrderRepository.save)

  consistency_checks:
    - every_sql_filter_maps_to_input: true
    - every_join_maps_to_association: true
    - every_parameter_is_type_safe: true
```

#### 6.5 OpenAPI Spec from UC API Designs

```yaml
openapi_mapping:
  source:
    - api_endpoints: from api_process_design
    - request_response_shapes: from function signatures
    - auth_requirements: from critical_checkpoints

  output_format: OpenAPI 3.0 YAML

  # Example OpenAPI spec
  example_openapi_spec: |
    openapi: 3.0.0
    info:
      title: Order Service API
      version: 1.0.0
      description: Generated from UC002: Customer places order
      evidence: node_160

    paths:
      /api/orders:
        post:
          summary: Create order
          operationId: createOrder
          evidence: node_161 (POST /api/orders)
          requestBody:
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/CreateOrderRequest'
                evidence: node_162
          responses:
            '201':
              description: Order created
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/OrderResponse'
              evidence: node_163
            '400':
              description: Invalid input
              evidence: node_164
            '401':
              description: Unauthorized
              evidence: node_165

    components:
      schemas:
        CreateOrderRequest:
          type: object
          required: [customerId, items]
          properties:
            customerId:
              type: string
              format: uuid
              evidence: node_166
            items:
              type: array
              items:
                $ref: '#/components/schemas/OrderItem'
          evidence: node_167

  consistency_checks:
    - every_endpoint_is_in_uc: true
    - every_schema_field_is_traced: true
    - every_response_code_is_documented: true
```

#### 6.6 Batch Process Design (if applicable)

```yaml
batch_design_mapping:
  source:
    - batch_oriented_branches: from UC alt/error flows
    - scheduled_jobs: from graph_mcp scheduled function discovery
    - async_operations: from graph_mcp async patterns

  trigger_condition:
    - exists: "UC has batch or async operations"
    - check: "graph_mcp search_functions for 'batch* OR schedule* OR async* OR job*'"

  output_sections:
    batch_processes:
      - process_name: string
        trigger: string
        input: string
        processing_logic: string
        output: string
        error_handling: string
        evidence: [node_ids]

  # Example batch design
  example_batch_design: |
    ## Batch: UpdateOrderStatus

    ### Trigger
    - Scheduled: Every 5 minutes
    - Evidence: node_170 (OrderStatusUpdater.schedule)

    ### Input
    - Query: SELECT * FROM orders WHERE status IN ('PENDING', 'PROCESSING')
    - Evidence: node_171 (OrderRepository.findPendingOrders)

    ### Processing Logic
    ```python
    for order in pending_orders:
        if order.is_expired():
            order.update_status('EXPIRED')
        elif order.is_ready():
            order.update_status('COMPLETED')
        order.save()
    ```
    - Evidence: node_172 (OrderStatusUpdater.process)

    ### Output
    - Updates orders table
    - Sends notifications
    - Evidence: node_173 (NotificationService.sendOrderUpdate)

    ### Error Handling
    - Retry on database timeout
    - Log failures for manual review
    - Evidence: node_174 (OrderStatusUpdater.handleError)

  consistency_checks:
    - every_batch_has_trigger: true
    - every_batch_has_error_handling: true
```

#### 6.7 Progress Reporting

```yaml
progress_reporting:
  task_progress:
    - "Generating design artifacts: {current}/{total} artifacts"
    - "Screen designs: {screen_count}"
    - "API designs: {api_count}"
    - "Table designs: {table_count}"
    - "SQL designs: {sql_count}"
    - "OpenAPI specs: {openapi_count}"
    - "Batch designs: {batch_count}"

  phase_complete:
    - "Phase 6 complete: Detail design derivation"
    - "  Duration: {actual_time}s"
    - "  Design artifacts generated: {artifact_count}"
    - "  Consistency checks passed: {checks_passed}/{checks_total}"
```

### Phase 7: Quality Gates and Review (120s timeout)

**Objective**: Evaluate coverage, alignment, and generate final quality report.

#### 7.1 Coverage Metrics

```yaml
coverage_metrics:
  uc_coverage:
    formula: "documented_uc / discovered_uc"
    source: "usecase_list + discovered entry points"
    threshold: 80  # Minimum 80%
    calculation:
      documented_uc: "Count of UCs with artifacts"
      discovered_uc: "Count of entry points from list_up_entrypoint"

  entry_coverage:
    formula: "traced_entries / total_entries"
    source: "list_up_entrypoint + trace_flow results"
    threshold: 90  # Minimum 90%
    calculation:
      traced_entries: "Entry points with successful trace_flow"
      total_entries: "All entry points from list_up_entrypoint"

  function_coverage:
    formula: "traced_functions / total_functions"
    source: "explore_graph + flow traces"
    threshold: 60  # Minimum 60% (realistic for large codebases)
    calculation:
      traced_functions: "Functions in flow traces"
      total_functions: "All functions from explore_graph"

  error_path_coverage:
    formula: "documented_error_paths / expected_error_paths"
    source: "error_functions + UC error flows"
    threshold: 50  # Minimum 50% (error paths vary)
    calculation:
      documented_error_paths: "UCs with error flows documented"
      expected_error_paths: "Error functions from search_functions"

  ipc_coverage:
    formula: "documented_ipc_links / discovered_ipc_links"
    source: "graph edges + UC IPC documentation"
    threshold: 70  # Minimum 70%
    calculation:
      documented_ipc_links: "IPC links documented in UCs"
      discovered_ipc_links: "IPC edges from explore_graph"

  mcp_evidence_pct:
    formula: "claims_with_mcp_source / total_claims"
    source: "All evidence tags in artifacts"
    threshold: 60  # Minimum 60%
    calculation:
      claims_with_mcp_source: "Evidence with source=mind_mcp or graph_mcp"
      total_claims: "All evidence tags"
```

#### 7.2 Risk Assessment

```yaml
risk_assessment:
  high_risk_ucs:
    criteria:
      - "Touches authentication or authorization"
      - "Handles payment or financial transactions"
      - "Modifies critical state"
      - "Processes PII or sensitive data"
    action: "Manual verification required before production use"

  incomplete_traces:
    criteria:
      - "Flow has unresolved edges"
      - "Error paths marked [MANUAL]"
      - "Indirect calls marked [UNRESOLVED]"
    action: "Document follow-up investigation"

  confidence_gaps:
    criteria:
      - "Evidence confidence = LOW"
      - "MCP evidence percentage < 60%"
      - "Filesystem-only mode used"
    action: "Add disclaimer to documentation"

  manual_verification_required:
    criteria:
      - "Items marked HANDLED=MANUAL"
      - "Conflict between evidence sources"
      - "Critical flows with incomplete traces"
    action: "Create follow-up task list"
```

#### 7.3 Quality Gates

```yaml
quality_gates:
  gate_1_mcp_evidence_threshold:
    threshold: 60
    check: "mcp_evidence_pct >= 60"
    on_fail:
      action: "report_gaps_and_continue"
      add_warning: true
      log: "MCP evidence threshold not met, documentation may have gaps"

  gate_2_uc_coverage_threshold:
    threshold: 80
    check: "uc_coverage >= 80"
    on_fail:
      action: "report_missing_ucs"
      add_warning: true
      log: "UC coverage below threshold, some entry points not documented"

  gate_3_entry_coverage_threshold:
    threshold: 90
    check: "entry_coverage >= 90"
    on_fail:
      action: "report_untraced_entries"
      add_warning: true
      log: "Entry coverage below threshold, some flows not traced"

  gate_4_critical_flows_must_have_trace:
    threshold: 100
    check: "all_high_risk_ucs_have_trace"
    on_fail:
      action: "block_and_require_manual_trace"
      log: "Critical flows missing trace, manual trace required"

  gate_5_consistency_checks:
    threshold: 95
    check: "consistency_checks_passed >= 95%"
    on_fail:
      action: "report_inconsistencies"
      add_warning: true
      log: "Consistency checks failed, review evidence alignment"
```

#### 7.4 Final Quality Report

```yaml
quality_report_output:
  file: "quality_report_{module}.md"
  sections:
    executive_summary:
      - module_name: string
        reconstruction_date: ISO8601
        depth_preference: "quick" | "deep"
        overall_status: "PASS" | "PASS_WITH_WARNINGS" | "FAIL"

    coverage_summary:
      uc_coverage: percentage
      entry_coverage: percentage
      function_coverage: percentage
      error_path_coverage: percentage
      ipc_coverage: percentage
      mcp_evidence_percentage: percentage

    risk_summary:
      high_risk_ucs: integer
      incomplete_traces: integer
      confidence_gaps: integer
      manual_verification_required: integer

    quality_gate_results:
      - gate_name: string
        status: "PASS" | "FAIL"
        actual_value: numeric
        threshold: numeric

    follow_up_actions:
      - priority: "HIGH" | "MEDIUM" | "LOW"
        action: string
        owner: string
        due_date: string

    evidence_provenance_summary:
      mind_mcp_claims: integer
      graph_mcp_claims: integer
      filesystem_claims: integer
      redaction_events: integer

  # Example quality report
  example_report: |
    # Quality Report: Order Management Module

    **Reconstruction Date**: 2025-04-16T10:30:00Z
    **Depth**: Deep
    **Overall Status**: PASS_WITH_WARNINGS

    ## Coverage Summary
    - UC Coverage: 85% (17/20 entry points)
    - Entry Coverage: 92% (23/25 entry points)
    - Function Coverage: 65% (130/200 functions)
    - Error Path Coverage: 55% (11/20 error functions)
    - IPC Coverage: 75% (3/4 IPC links)
    - MCP Evidence Percentage: 72% (288/400 claims)

    ## Risk Summary
    - High-Risk UCs: 5
    - Incomplete Traces: 3
    - Confidence Gaps: 2
    - Manual Verification Required: 4

    ## Quality Gate Results
    ✅ Gate 1: MCP Evidence (72% >= 60%) - PASS
    ✅ Gate 2: UC Coverage (85% >= 80%) - PASS
    ✅ Gate 3: Entry Coverage (92% >= 90%) - PASS
    ✅ Gate 4: Critical Flows - PASS
    ⚠️  Gate 5: Consistency Checks (93% < 95%) - FAIL

    ## Follow-Up Actions
    1. [HIGH] Manual trace for UC018 (Refund processing)
       - Owner: TBD
       - Due: 2025-04-23

    2. [MEDIUM] Resolve 3 incomplete traces in payment flows
       - Owner: TBD
       - Due: 2025-04-20

    3. [LOW] Investigate confidence gaps in notification service
       - Owner: TBD
       - Due: 2025-04-30

    ## Evidence Provenance
    - mind_mcp claims: 120
    - graph_mcp claims: 168
    - filesystem claims: 112
    - Redaction events: 5 (2 API keys, 3 connection strings)

  progress_reporting:
    final_summary:
      - "Documentation reconstruction complete"
      - "Total duration: {total_duration}s"
      - "Use cases discovered: {uc_count}"
      - "Design artifacts generated: {artifact_count}"
      - "Evidence coverage: {mcp_coverage}%"
      - "Quality gate status: {overall_status}"
      - "Output: {output_files}"
```

## 3. Filesystem Fallback Mode (MCP Unavailable)

**Trigger**: All MCP checks fail or timeout

**Mode**: filesystem_analysis_with_manual_verification

### 3.1 Module Inventory

```bash
# Use rg for module inventory
rg --files -g "{module_pattern}/**/*.{ext}" | head -5000

# Count by file type
rg --files -g "{module_pattern}/**/*.py" | wc -l
rg --files -g "{module_pattern}/**/*.java" | wc -l
```

### 3.2 Entry Point Discovery

```bash
# Find entry points by pattern
rg "def (handle_|process_|execute_|on_)" {module_pattern}
rg "@(RequestMapping|GetMapping|PostMapping)" {module_pattern}
rg "class.*Controller" {module_pattern}
rg "def main" {module_pattern}
```

### 3.3 Function Discovery

```bash
# Find function definitions
rg "^\s*(def|func|function)\s+\w+" {module_pattern}
rg "^\s*public\s+\w+\s+\w+\(" {module_pattern}

# Find class definitions
rg "^class\s+\w+" {module_pattern}
rg "^public\s+class\s+\w+" {module_pattern}
```

### 3.4 Error Handling Discovery

```bash
# Find error handling patterns
rg "throw|raise|catch|except|error|timeout|retry" {module_pattern}
rg "Exception|Error|Timeout" {module_pattern}
```

### 3.5 IPC Discovery

```bash
# Find IPC patterns
rg "http\.|requests\.|fetch\(|axios" {module_pattern}
rg "publish|emit|send|queue" {module_pattern}
rg "@FeignClient|@RestClient|WebClient" {module_pattern}
```

### 3.6 Conservative Use Case Construction

```yaml
filesystem_uc_rules:
  business_purpose:
    - "Use function and class names as business hints"
    - "Mark as [INFERRED_FROM_NAMES]"
    - "Confidence: LOW"

  code_entry_point:
    - "Use discovered entry points"
    - "Mark as [DISCOVERED_BY_PATTERN]"
    - "Confidence: MEDIUM"

  flow_evidence:
    - "Use call patterns from grep"
    - "Cannot trace deep flows"
    - "Mark as [MANUAL_TRACE_REQUIRED]"
    - "Confidence: LOW"

  diagrams:
    - "Create simple text diagrams"
    - "Mark as [MANUAL_VERIFICATION_REQUIRED]"
    - "Do not generate Mermaid (unreliable)"

  evidence_provenance:
    - "All evidence: source=filesystem, confidence=low"
    - "Add disclaimer to every generated document"

disclaimer_text: |
  ⚠️ **WARNING**: This documentation was generated in FILESYSTEM-ONLY MODE due to MCP unavailability.

  **Limitations**:
  - Business context inferred from code names only
  - Call flows are incomplete and may be inaccurate
  - Error paths may be missing
  - Diagrams are simplified and require manual verification

  **Required Actions**:
  - Manual verification of all business rules
  - Manual trace of critical flows
  - Manual verification of all error handling
  - Manual review of all diagrams

  **Do NOT use** for:
  - Compliance or audit documentation
  - Critical system documentation
  - Production deployment decisions
  - Stakeholder communication without review
```

## 4. Performance Optimization Strategies

### 4.1 Context Control for Large Codebases

```yaml
context_control_strategy:
  query_by_module:
    rule: "Use module-specific terms, not entire project"
    example: "OrderService NOT 'service'"
    benefit: "Reduces result count by 10-100x"

  limit_results:
    rule: "Limit to 20-50 items per query"
    if_truncated:
      - "Summarize first 20-50 results"
      - "Ask user for specific focus"
      - "Process sub-modules sequentially"

  batch_processing:
    rule: "Batch node_details in groups of 10-20"
    user_confirmation: true
    prompt: "Processing {batch_size} nodes, continue?"

  traversal_limits:
    max_depth: 5
    max_modules: 50
    max_entry_points: 200
    if_exceeded:
      - "Summarize top results"
      - "Mark deeper levels as [REQUIRES_FOCUS]"
      - "Ask user for specific sub-module"
```

### 4.2 Caching Strategy

```yaml
cache_strategy:
  business_context_cache:
    enabled: true
    ttl: 900  # 15 minutes
    file: "mcp_business_context_cache.json"
    invalidation: "on_workflow_start"

  tracing_cache:
    enabled: true
    ttl: 1200  # 20 minutes
    file: "mcp_tracing_cache.json"
    invalidation: "on_repo_change"

  use_case_cache:
    enabled: true
    ttl: 1800  # 30 minutes
    file: "use_case_cache.json"
    invalidation: "on_uc_approval"

  shared_cache:
    enabled: true
    ttl: 2400  # 40 minutes
    file: "shared_reconstruction_cache.json"
    invalidation: "on_workflow_end"
```

### 4.3 Timeout Strategy

```yaml
timeout_strategy:
  mcp_call_timeout: 30s
  query_timeout: 45s
  batch_timeout: 60s
  phase_timeout:
    phase_0: 30s
    phase_1: 180s
    phase_2: 240s
    phase_3: 360s
    phase_4: 180s
    phase_5: 300s
    phase_6: 600s
    phase_7: 120s
  total_workflow_timeout: 1800s  # 30 minutes

  on_timeout:
    action: "return_partial_and_continue"
    log: "Timeout exceeded, returning partial results"
    add_warning: true
```

## 5. Error Handling Patterns

### 5.1 MCP Timeout Handling

```yaml
on_mcp_timeout:
  mind_mcp:
    action: "return_cached_or_empty"
    log: "mind_mcp timeout, using cached results or empty context"
    continue: true

  graph_mcp:
    action: "return_partial_or_fallback"
    log: "graph_mcp timeout, returning partial results or filesystem fallback"
    continue: true
```

### 5.2 Evidence Conflict Resolution

```yaml
conflict_resolution_rules:
  priority:
    1. "For code structure: Trust graph_mcp over mind_mcp"
    2. "For business intent: Trust mind_mcp over graph_mcp"
    3. "For recent changes: Trust filesystem over MCP"
    4. "For historical context: Trust mind_mcp (archival)"

  on_conflict:
    action: "apply_priority_rules"
    log: "Conflict detected, applying resolution rules"
    if_unresolved:
      action: "report_both_with_disclaimer"
      format: |
        CONFLICT DETECTED:
        - mind_mcp says: {mind_mcp_claim} (confidence: {confidence})
        - graph_mcp says: {graph_mcp_claim} (confidence: {confidence})
        - Resolution: {resolution}
        Recommendation: Manual verification required
```

### 5.3 Partial Recovery Strategies

```yaml
partial_recovery:
  on_partial_results:
    action: "continue_with_partial"
    log: "Partial results retrieved, continuing with available data"

  on_missing_alternate_paths:
    action: "document_main_flow_only"
    log: "Alternate paths unavailable, documenting main flow only"
    add_tag: "[ALT_PATHS_REQUIRED]"

  on_incomplete_error_traces:
    action: "mark_error_paths_as_manual"
    log: "Error trace incomplete, marking as manual verification required"
    add_tag: "[MANUAL_TRACE_REQUIRED]"
```

## 6. Integration with SKILL.md

This playbook is fully integrated with the enhanced SKILL.md (v2.0.0) and implements:

- ✅ **Security & Privacy**: Path validation, sensitive data redaction
- ✅ **Performance & UX**: Timeout configuration, progress feedback, caching
- ✅ **Reliability & Resilience**: Fallback strategy, conflict resolution, error recovery
- ✅ **Observability**: Metrics tracking, health monitoring, evidence provenance

For complete details, refer to:
- `<repo_root>/reverse-doc-reconstruction/SKILL.md`
- `<repo_root>/reverse-doc-reconstruction/references/usecase-to-detail-design-map.md`
