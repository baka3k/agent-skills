# MCP Recon Playbook

Use this sequence for repository reconnaissance with comprehensive security hardening, operational resilience, and evidence-based decision making.

## 1. Objective

Build a structural understanding of an unfamiliar repository by combining project knowledge-base retrieval from mind_mcp with semantic code exploration from graph_mcp, with security hardening, performance optimization, and fallback strategies.

## 2. MCP-First Tool Order with Detailed Signatures

### Phase 0: Preflight and Validation (Required, 30s timeout)

**Objective**: Verify MCP capabilities, validate inputs, and configure reconnaissance environment.

#### Step 1: Input Validation (Required)

```yaml
validation_checks:
  repository_path:
    - repository_path must exist: os.path.exists(repo_path)
    - repository_path must be readable: os.access(repo_path, os.R_OK)
    - Block path traversal: reject if contains "../" or absolute path
    - Character whitelist: [a-zA-Z0-9_\-./]
    - Max length: 10000 characters

  focus_scope:
    allowed_values: ["backend", "frontend", "infra", "data", "all"]
    default: "all"
    validation: "Scope module discovery to specified area"

  depth_preference:
    allowed_values: ["quick", "standard", "deep"]
    default: "standard"
    quick_depth: "Module boundaries and entry points only"
    standard_depth: "Module boundaries, entry points, and key functions"
    deep_depth: "All standard + call graph expansion and integration boundaries"
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
  expected: "Check for target language parser"
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
      - "Module boundaries may not match architectural intent"
      - "Manual verification required for critical modules"

    logging:
      - "Running in FILESYSTEM-ONLY MODE: MCP unavailable"
      - "Analysis limited to filesystem recon script only"
      - "Evidence confidence: LOW for all items"
```

### Phase 1: mind_mcp Knowledge Base Context (120s timeout)

**Objective**: Load project context, architecture overview, and module descriptions from knowledge base.

#### 1.1 Discover Architecture and Module Terms

```python
mind_mcp.hybrid_search [required]
  params:
    query: "system architecture OR module responsibilities OR service boundaries OR entry points OR runtime topology"
    collection: "{selected_collection}"
    limit: 20
  timeout: 45s
  output:
    results:
      - id: paragraph_id
        score: relevance_score_0_to_1
        metadata:
          source_file: string
          source_type: "adr" | "doc" | "design" | "ticket"
    expected:
      - "Architecture overview documents"
      - "Module responsibility descriptions"
      - "Service boundary definitions"
      - "Entry point documentation"
      - "Runtime topology descriptions"

  # Example queries for project context
  example_queries:
    - "system architecture overview"
    - "module responsibilities"
    - "service boundaries"
    - "entry points"
    - "runtime topology"
    - "domain driven design"
    - "microservices architecture"
    - "component structure"

  # Apply sensitive data redaction
  redaction_rules:
    - API keys: /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
    - Passwords: /password.*/gi → '[REDACTED_PASSWORD]'
    - Secrets: /secret.*/gi → '[REDACTED_SECRET]'
    - Tokens: /token.*/gi → '[REDACTED_TOKEN]'
    - Connection strings: /\bpostgresql:\/\/[^\s]+\b/gi → 'postgresql://[REDACTED]'
    - URLs with creds: /\b[\w-]+:\/\/[\w-]+:[\w-]+@/gi → '[REDACTED_URL]'

  error_handling:
    on_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty context"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial project context retrieved, continuing with available data"
```

#### 1.2 Discover Procedural Architecture Descriptions

```python
mind_mcp.sequential_search [optional]
  params:
    query: "system architecture step by step OR module flow OR service topology OR startup sequence"
    collection: "{selected_collection}"
    limit: 10
  timeout: 45s
  output:
    results:
      - ordered_procedures:
          steps: []
          sequence: integer
    expected:
      - "Ordered architecture descriptions"
      - "Module interaction flows"
      - "Startup sequences"
      - "Service topology flows"

  # Example procedural queries
  example_queries:
    - "step 1 OR step 2 OR phase 1 OR phase 2"
    - "startup sequence OR initialization flow"
    - "module interaction OR service communication"
    - "request flow OR data flow"

  error_handling:
    on_timeout:
      action: "skip_procedural_extraction"
      log: "Sequential search timeout, skipping procedural flows"
      continue: true
```

#### 1.3 Get Detailed Content

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

  # Apply comprehensive redaction
  redaction_rules:
    # Credentials
    - API keys: /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
    - Passwords: /password.*/gi → '[REDACTED_PASSWORD]'
    - Secrets: /secret.*/gi → '[REDACTED_SECRET]'
    - Tokens: /token.*/gi → '[REDACTED_TOKEN]'

    # Network
    - IP addresses: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'
    - Hostnames: /\b[a-zA-Z0-9.-]+\.(?:com|net|org|io)\b/gi → '[REDACTED_HOST]'

    # Cloud
    - AWS keys: /\bAKIA[0-9A-Z]{16}\b/g → '[REDACTED_AWS_KEY]'
    - GCP keys: /\b[0-9a-f]{32}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi → '[REDACTED_GCP_KEY]'

  error_handling:
    on_timeout:
      action: "use_search_snippets"
      log: "get_paragraph_text timeout, using search snippets"
      continue: true
```

#### 1.4 Correlate Entities and Modules

```python
mind_mcp.query_graph_rag_relation [optional]
  params:
    entity: "{module_name} OR {domain_entity}"
    relation_types: ["contains", "depends_on", "communicates_with"]
  timeout: 45s
  output:
    relations:
      - source: string
        target: string
        relation_type: string
        evidence: string
    expected:
      - "Cross-module relationships"
      - "Entity dependencies"
      - "Module communication patterns"

  # Example correlation queries
  example_queries:
    - "auth module depends_on user module"
    - "order service communicates_with payment service"
    - "api gateway contains backend services"

  error_handling:
    on_timeout:
      action: "skip_relation_extraction"
      log: "Relation extraction timeout, using co-occurrence"
      continue: true
```

#### 1.5 Cache Project Context

```yaml
cache_output:
  file: "mcp_project_context_cache.json"
  ttl: 900  # 15 minutes
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    collections: ["{collection_ids}"]
    evidence_items:
      - id: unique_id
        type: architecture_overview | domain_term | module_description | service_boundary
        source: mind_mcp
        ref: paragraph_id
        confidence: high | medium | low
        content: summarized content (redacted)
    redaction_log:
      - "Redacted {count} API keys"
      - "Redacted {count} passwords"
      - "Redacted {count} connection strings"

  progress_reporting:
    phase_complete:
      - "Phase 1 complete: Project context loading"
      - "  Duration: {actual_time}s"
      - "  Architecture items: {arch_count}"
      - "  Module descriptions: {module_count}"
      - "  Service boundaries: {boundary_count}"
      - "  Evidence items: {evidence_count}"
```

### Phase 2: graph_mcp Semantic Code Map (240s timeout)

**Objective**: Build semantic module map with code structure and entry points.

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
      log: "Failed to activate project, aborting reconnaissance"
```

#### 2.2 Explore Module Boundaries

```python
graph_mcp.explore_graph [required]
  params:
    query: "{module_name} OR {domain_term} OR 'controller' OR 'service' OR 'repository'"
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
      - "Module boundaries"
      - "Key functions and classes"
      - "Dependency relationships"

  # Example module queries
  example_queries:
    - "auth OR authentication OR login"
    - "user OR customer OR account"
    - "order OR payment OR invoice"
    - "controller OR service OR repository"
    - "api OR handler OR endpoint"

  # Context control for large modules
  context_control:
    max_results: 100
    if_results_truncated:
      - "Summarize first 100 results"
      - "Ask user for specific module focus"
      - "Process modules sequentially"

  error_handling:
    on_timeout:
      action: "return_partial_results"
      log: "Graph exploration timeout, returning partial module map"
      continue: true
```

#### 2.3 Search for Key Functions

```python
graph_mcp.search_functions [required]
  params:
    query: "main OR init OR controller OR service OR repository OR handler"
    limit: 50
  timeout: 45s
  output:
    functions:
      - id: node_id
        name: string
        file: string
        signature: string
    expected:
      - "Key functions by module"
      - "Entry point candidates"
      - "Service layer functions"
      - "Repository functions"

  # Example function queries
  example_queries:
    - "main OR start OR init OR bootstrap"
    - "controller OR handler OR endpoint"
    - "service OR domain OR usecase"
    - "repository OR dao OR persistence"

  error_handling:
    on_timeout:
      action: "use_explore_graph_results_only"
      log: "Function search timeout, using explore_graph results"
      continue: true
```

#### 2.4 Search for Implementation Patterns

```python
graph_mcp.search_by_code [optional]
  params:
    query: "class.*Controller OR def.*service OR @Repository OR @Service"
    limit: 50
  timeout: 45s
  output:
    code_snippets:
      - id: node_id
        code: string
        file: string
        language: string
    expected:
      - "Implementation patterns"
      - "Framework annotations"
      - "Class structure"

  # Example pattern queries
  example_queries:
    - "class.*Controller" # Spring MVC
    - "@RestController OR @Controller" # Spring annotations
    - "def.*service|class.*Service" # Service layer
    - "@Repository|interface.*Repository" # Repository pattern
    - "@Component|@Service" # Component annotations

  error_handling:
    on_timeout:
      action: "skip_pattern_search"
      log: "Pattern search timeout, using function names only"
      continue: true
```

#### 2.5 Discover Entry Points

```python
graph_mcp.list_up_entrypoint [required]
  params:
    file_pattern: "{focus_scope_pattern}/**/*.{py,js,ts,java,go,rs}"
    limit: 200
  timeout: 60s
  output:
    entry_points:
      - id: node_id
        name: string
        file: string
        type: "function" | "method" | "api_endpoint"
    expected:
      - "API endpoints"
      - "Main functions"
      - "CLI entry points"
      - "Worker entry points"

  # Use entry points for runtime classification
  use_case:
    - "API runtime: HTTP endpoints"
    - "Worker runtime: Queue consumers"
    - "CLI runtime: Command-line interfaces"
    - "Library runtime: Package exports"

  error_handling:
    on_timeout:
      action: "use_filesystem_entry_patterns"
      log: "Entry point discovery timeout, using filesystem patterns"
      continue: true
```

#### 2.6 Expand Call Graph Around Key Functions

```python
graph_mcp.query_subgraph [optional]
  params:
    node_id: "{key_function_id}"
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
      - "Call graph around key functions"
      - "Function dependencies"
      - "Module interactions"

  # Example subgraph expansion
  example_targets:
    - "Expand around main entry point"
    - "Expand around high-centrality functions"
    - "Expand around service layer functions"

  error_handling:
    on_timeout:
      action: "skip_subgraph_expansion"
      log: "Subgraph expansion timeout, using surface-level evidence"
      continue: true
```

#### 2.7 Trace Runtime Flows

```python
graph_mcp.trace_flow [optional]
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
    expected:
      - "Runtime flow from entry points"
      - "Module interactions"
      - "Integration paths"

  # Use for runtime classification
  use_case:
    - "Trace to database layer → backend service"
    - "Trace to queue → worker/batch"
    - "Trace to static files → web frontend"

  error_handling:
    on_timeout:
      action: "skip_flow_tracing"
      log: "Flow tracing timeout, using surface-level evidence"
      continue: true
```

#### 2.8 Cache Semantic Map

```yaml
cache_output:
  file: "mcp_semantic_map_cache.json"
  ttl: 1200  # 20 minutes
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    evidence_items:
      - id: node_id
        type: module | function | entry_point | integration_path
        source: graph_mcp
        metadata:
          name: string
          file: string
          signature: string
        confidence: high | medium | low

  progress_reporting:
    phase_complete:
      - "Phase 2 complete: Semantic module mapping"
      - "  Duration: {actual_time}s"
      - "  Modules discovered: {module_count}"
      - "  Key functions: {function_count}"
      - "  Entry points: {entry_count}"
      - "  Integration paths: {integration_count}"
```

### Phase 3: Filesystem Cross-Check (180s timeout)

**Objective**: Detect blind spots between graph extraction and raw files.

#### 3.1 Execute Recon Script

```bash
python scripts/repo_recon.py /path/to/repo \
  --json /tmp/repo-recon.json \
  --md /tmp/repo-recon.md
```

#### 3.2 Module Discovery from Directory Structure

```yaml
module_discovery_rules:
  directory_based:
    - "src/auth/* → auth module"
    - "src/user/* → user module"
    - "src/order/* → order module"
    - "services/* → service modules"
    - "controllers/* → API layer"
    - "models/* → data models"

  package_based:
    - "com.example.auth → auth package"
    - "com.example.service → service package"
    - "org.myapp.module → module package"

  namespace_based:
    - "namespace Auth { } → Auth namespace"
    - "module User → User module"
    - "package Order → Order package"

  confidence:
    directory_based: high
    package_based: high
    namespace_based: medium
```

#### 3.3 Language Detection

```yaml
language_detection_rules:
  file_extensions:
    - ".py → Python"
    - ".js, .ts, .jsx, .tsx → JavaScript/TypeScript"
    - ".java → Java"
    - ".go → Go"
    - ".rs → Rust"
    - ".cpp, .cc, .cxx → C++"
    - ".c → C"
    - ".rb → Ruby"
    - ".php → PHP"

  config_files:
    - "package.json → Node.js"
    - "requirements.txt, pyproject.toml → Python"
    - "pom.xml, build.gradle → Java"
    - "go.mod → Go"
    - "Cargo.toml → Rust"
    - "Gemfile → Ruby"
    - "composer.json → PHP"
```

#### 3.4 Entry Point Detection from Filesystem

```yaml
entry_point_patterns:
  api_runtime:
    - "app.py, main.py, server.py (Python)"
    - "index.js, server.js, app.js (Node.js)"
    - "Application.java, Main.java (Java)"
    - "main.go (Go)"
    - "controllers/*Controller.java (Java Spring)"

  worker_runtime:
    - "worker.py, consumer.py (Python)"
    - "worker.js, consumer.js (Node.js)"
    - "Worker.java, Consumer.java (Java)"
    - "worker.go, consumer.go (Go)"

  cli_runtime:
    - "cli.py, main.py with argparse (Python)"
    - "cli.js, bin/* (Node.js)"
    - "Main.java with args (Java)"
    - "main.go with flags (Go)"

  library_runtime:
    - "__init__.py (Python package)"
    - "index.ts, main.ts (TypeScript library)"
    - "lib/* (Any language)"
    - "No entry point, only exports"

  progress_reporting:
    phase_complete:
      - "Phase 3 complete: Filesystem cross-check"
      - "  Duration: {actual_time}s"
      - "  Files scanned: {file_count}"
      - - "Languages detected: {language_count}"
      - "  Directory-based modules: {dir_module_count}"
```

### Phase 4: Entry Point Identification (120s timeout)

**Objective**: Identify and classify entry points by runtime type.

#### 4.1 Entry Point Classification Rules

```yaml
entry_point_classification:
  api_runtime:
    required:
      - "HTTP server initialization"
      - "API route definitions"
    indicators:
      - "app.listen, server.start, application.run"
      - "@app.route, @RequestMapping, @GetMapping"
      - "controllers/, handlers/, routes/"
    evidence:
      - graph_mcp: "Call graph from HTTP initialization"
      - filesystem: "Route handler files"

  worker_runtime:
    required:
      - "Queue consumer initialization"
      - "Job/worker registration"
    indicators:
      - "consumer.subscribe, worker.start"
      - "@Scheduled, @Consumer, @Worker"
      - "worker/, consumer/, jobs/"
    evidence:
      - graph_mcp: "Call graph from queue initialization"
      - filesystem: "Worker/consumer files"

  cli_runtime:
    required:
      - "Command-line argument parsing"
      - "main() function with CLI args"
    indicators:
      - "argparse, click, commander, yargs"
      - "if __name__ == '__main__'"
      - "main() with sys.argv"
    evidence:
      - graph_mcp: "Call graph from main()"
      - filesystem: "CLI entry files"

  library_runtime:
    required:
      - "Package exports"
      - "No standalone entry point"
    indicators:
      - "package.json main field"
      - "__init__.py exports"
      - "module.exports"
    evidence:
      - filesystem: "Package configuration files"
```

#### 4.2 Entry Point Verification

```yaml
verification_rules:
  graph_mcp_preferred:
    - "Entry points from list_up_entrypoint are high confidence"
    - "Traced calls from entry points confirm runtime type"
    - "Call graph depth indicates API vs worker vs CLI"

  filesystem_fallback:
    - "File patterns when graph_mcp unavailable"
    - "Directory structure for module boundaries"
    - "Reduced confidence (medium/low)"

  confidence_levels:
    high:
      - "graph_mcp entry point + traced call graph"
      - "Filesystem pattern matches graph_mcp"
    medium:
      - "graph_mcp entry point without trace"
      - "Filesystem pattern without graph_mcp confirmation"
    low:
      - "Filesystem pattern only"
      - "Inferred from module name"
```

#### 4.3 Cache Entry Points

```yaml
cache_output:
  file: "entry_point_cache.json"
  content:
    timestamp: "{ISO8601}"
    entry_points:
      - id: entry_point_id
        type: api | worker | cli | library
        name: string
        file: string
        evidence_source: graph_mcp | filesystem
        confidence: high | medium | low

  progress_reporting:
    phase_complete:
      - "Phase 4 complete: Entry point identification"
      - "  Duration: {actual_time}s"
      - "  API entry points: {api_count}"
      - "  Worker entry points: {worker_count}"
      - "  CLI entry points: {cli_count}"
      - "  Library entry points: {library_count}"
```

### Phase 5: Inventory Artifact Generation (60s timeout)

**Objective**: Generate comprehensive module inventory with all findings.

#### 5.1 Inventory Structure

```yaml
inventory_sections:
  context:
    - repository: string
    - commit/branch: string
    - scan_date: ISO8601
    - scope: string
    - duration_seconds: integer

  top_level_modules:
    rows:
      - module: string
        purpose: string (from mind_mcp or inferred)
        key_files: []
        dominant_languages: []
        notes: string
        evidence_source: mind_mcp | graph_mcp | filesystem

    example_row:
      - module: "auth-service"
        purpose: "Authentication and authorization"
        key_files: ["src/auth/AuthController.java", "src/auth/AuthService.java"]
        dominant_languages: ["Java"]
        notes: "High-risk module, handles user credentials"
        evidence_source: mind_mcp

  entry_points:
    rows:
      - runtime: api | worker | cli | library
        file/path: string
        trigger: string
        notes: string
        evidence_source: graph_mcp | filesystem

    example_row:
      - runtime: api
        file/path: "src/auth/AuthController.java"
        trigger: "HTTP POST /auth/login"
        notes: "Main authentication endpoint"
        evidence_source: graph_mcp

  integration_boundaries:
    rows:
      - module: string
        inbound_interfaces: []
        outbound_dependencies: []
        risk: low | medium | high
        evidence_source: graph_mcp

    example_row:
      - module: "order-service"
        inbound_interfaces: ["REST API", "gRPC"]
        outbound_dependencies: ["payment-service", "inventory-service"]
        risk: high
        evidence_source: graph_mcp

  unknowns_and_next_probes:
    - unknown: string
      why_uncertain: string
      suggested_probe: string

    example:
      - unknown: "Module X purpose unclear"
        why_uncertain: "No documentation found, code structure ambiguous"
        suggested_probe: "Manual review of Module X or interview with team"

  progress_reporting:
    final_summary:
      - "Repository reconnaissance complete"
      - "Total duration: {total_duration}s"
      - "Modules discovered: {module_count}"
      - "Entry points identified: {entry_count}"
      - "Integration boundaries: {boundary_count}"
      - "Evidence coverage: {mcp_coverage}%"
      - "Output: {output_files}"
```

#### 5.2 Output Files

```yaml
output_files:
  repo_recon_json:
    format: JSON
    content:
      - context: {}
      - modules: []
      - entry_points: []
      - integration_boundaries: []
      - evidence_sources: []
    purpose: "Machine-readable structure for tooling"

  repo_recon_md:
    format: Markdown
    content:
      - "# Repository Recon"
      - "## Context"
      - "## Top-Level Modules"
      - "## Entry Points"
      - "## Integration Boundaries"
      - "## Unknowns and Next Probes"
    purpose: "Human-readable inventory"

  mcp_evidence_md:
    format: Markdown (optional)
    content:
      - "# MCP Evidence"
      - "## mind_mcp Queries"
      - "## graph_mcp Traces"
      - "## Confidence Notes"
    purpose: "Query logs and evidence notes"

  progress_reporting:
    phase_complete:
      - "Phase 5 complete: Inventory artifact generation"
      - "  Duration: {actual_time}s"
      - "  JSON output: {json_path}"
      - "  Markdown output: {md_path}"
```

## 3. Filesystem Fallback Mode (MCP Unavailable)

**Trigger**: All MCP checks fail or timeout

**Mode**: filesystem_scan_with_manual_verification

### 3.1 Module Discovery (Filesystem Only)

```bash
# Use directory structure for module discovery
find /path/to/repo -type d -maxdepth 3 | head -100

# Detect language from file extensions
find /path/to/repo -name "*.py" | wc -l
find /path/to/repo -name "*.java" | wc -l
find /path/to/repo -name "*.js" -o -name "*.ts" | wc -l
```

### 3.2 Entry Point Discovery (Filesystem Only)

```bash
# Find entry points by pattern
find /path/to/repo -name "main.py" -o -name "app.py" -o -name "index.js"
find /path/to/repo -name "*Controller.java"
find /path/to/repo -name "main.go" -o -name "main.c"
```

### 3.3 Conservative Module Rules

```yaml
filesystem_evidence_rules:
  module_boundaries:
    - "Use directory structure as module boundaries"
    - "Mark as [INFERRED_FROM_STRUCTURE]"
    - "Confidence: MEDIUM"

  module_purpose:
    - "Infer from directory and file names"
    - "Mark as [PURPOSE_INFERRED]"
    - "Confidence: LOW"

  entry_points:
    - "Detect from file patterns only"
    - "Mark as [FILESYSTEM_DETECTED]"
    - "Confidence: MEDIUM"

  integration_boundaries:
    - "Skipped (requires graph_mcp)"
    - "Document as [ANALYSIS_UNAVAILABLE]"
    - "Recommend manual review"

disclaimer_text: |
  ⚠️ **WARNING**: This reconnaissance was generated in FILESYSTEM-ONLY MODE due to MCP unavailability.

  **Limitations**:
  - Module boundaries inferred from directory structure only
  - Module purpose inferred from file and directory names
  - Entry points detected from file patterns only
  - Integration boundaries NOT available (requires graph_mcp)
  - No semantic code analysis performed

  **Required Actions**:
  - Manual verification of all module boundaries
  - Manual verification of module purposes
  - Manual verification of entry point classifications
  - Manual review of integration dependencies

  **Do NOT use** for:
  - Critical architecture decisions without review
  - Refactor planning without verification
  - Module ownership assignment without manual review
```

## 4. Performance Optimization Strategies

### 4.1 Context Control for Large Codebases

```yaml
context_control_strategy:
  process_by_module:
    rule: "Process modules sequentially, not all at once"
    example: "for module in ['auth', 'payment', 'order']: explore_graph(query=module)"
    benefit: "Reduces context size by 10-100x"

  limit_results:
    rule: "Limit to 20-50 results per query"
    if_truncated:
      - "Summarize first 20-50 results"
      - "Ask user for specific module focus"

  batch_processing:
    rule: "Batch node details in groups of 10-20"
    user_confirmation: true
    prompt: "Processing {batch_size} nodes, continue?"

  scope_by_module:
    example: |
      # Process one module at a time
      for module in ["auth", "payment", "order"]:
          explore_graph(query=module, limit=50)
          # Summarize before moving to next module
```

### 4.2 Caching Strategy

```yaml
cache_strategy:
  project_context_cache:
    enabled: true
    ttl: 900  # 15 minutes
    invalidation: "on_workflow_start"

  semantic_map_cache:
    enabled: true
    ttl: 1200  # 20 minutes
    invalidation: "on_repo_change"

  module_inventory_cache:
    enabled: true
    ttl: 1800  # 30 minutes
    invalidation: "on_inventory_approval"

  shared_cache:
    enabled: true
    ttl: 2400  # 40 minutes
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
    phase_1: 120s
    phase_2: 240s
    phase_3: 180s
    phase_4: 120s
    phase_5: 60s
  total_workflow_timeout: 900s  # 15 minutes

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
    1. "For current code structure and module boundaries: Trust graph_mcp over mind_mcp"
    2. "For architectural intent and domain terms: Trust mind_mcp over graph_mcp"
    3. "For recent code changes: Trust filesystem (actual files) over MCP"
    4. "For historical context and architecture: Trust mind_mcp (archival knowledge)"
    5. "For entry points and runtime surfaces: Trust graph_mcp (current code truth)"

  on_conflict:
    action: "apply_priority_rules"
    log: "Conflict detected, applying resolution rules"
    if_unresolved:
      action: "report_both_with_disclaimer"
      format: |
        CONFLICT DETECTED:
        - mind_mcp says: {mind_mcp_claim}
        - graph_mcp says: {graph_mcp_claim}
        - Resolution: {resolution}
        Recommendation: Manual verification required
```

### 5.3 Partial Recovery Strategies

```yaml
partial_recovery:
  on_partial_results:
    action: "continue_with_partial"
    log: "Partial results retrieved, continuing with available data"

  on_missing_module_boundaries:
    action: "use_directory_structure"
    log: "Module boundaries not explicit, using directory structure"
    add_tag: "[INFERRED_FROM_STRUCTURE]"

  on_missing_entry_points:
    action: "use_filesystem_patterns"
    log: "Entry points not in graph, using filesystem patterns"
    add_tag: "[FILESYSTEM_DETECTED]"
```

## 6. Integration with SKILL.md

This playbook is fully integrated with the enhanced SKILL.md (v2.0.0) and implements:

- ✅ **Security & Privacy**: Path validation, sensitive data redaction
- ✅ **Performance & UX**: Timeout configuration, progress feedback, caching
- ✅ **Reliability & Resilience**: Fallback strategy, conflict resolution, error recovery
- ✅ **Observability**: Metrics tracking, quality gates, evidence provenance

For complete details, refer to:
- `<repo_root>/repo-recon/SKILL.md`
- `<repo_root>/repo-recon/references/module-inventory-template.md`
