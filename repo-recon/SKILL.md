---
name: repo-recon
description: Build a structural understanding of an unfamiliar repository by combining project knowledge-base retrieval from mind_mcp with semantic code exploration from graph_mcp, then produce a module inventory and entry-point map. Use when onboarding to a new codebase, preparing architecture reviews, planning refactors, or creating handover documentation.
version: 2.0.0
last_updated: 2025-04-16
---

# Repo Recon

Build structural understanding from MCP evidence first, filesystem scan second, with comprehensive security hardening, operational resilience, and evidence-based decision making.

## When To Use

- You need a fast structural understanding of a new repository
- You need module boundaries and likely entry points before deeper analysis
- You are preparing for refactor/audit/documentation and need a stable inventory
- You are onboarding to a new codebase with no existing documentation
- You need to create handover documentation or architecture reviews

## Avoid Using When

- You already have a current module inventory and need synthesis only (use module-summary-report)
- You are debugging one known bug path (use bug-impact-analyzer)
- The request is stack/build-centric (use tech-build-audit)
- You need end-to-end technical assessment (use deep-codebase-discovery)

## Required Inputs

- Repository root path
- Optional focus scope: `backend`, `frontend`, `infra`, `data`, or `all`
- Optional depth preference: `quick`, `standard`, or `deep`

## Input Validation & Security

### Path Validation

- **Repository path**: Must exist, be within allowed scope, and be readable by current user
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **Path sanitization**: Remove null bytes, limit to 10000 characters, whitelist allowed characters
- **Access verification**: Verify read access before analysis

**Validation rules**:
```yaml
repository_path_validation:
  - repository_path must exist: os.path.exists(repo_path)
  - repository_path must be readable: os.access(repo_path, os.R_OK)
  - Block path traversal: reject if contains "../" or absolute path
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max length: 10000 characters
```

### Focus Scope Validation

- **Focus scope**: Must be valid scope type
- **Depth preference**: Must be one of `quick`, `standard`, or `deep`

**Validation rules**:
```yaml
focus_scope_validation:
  allowed_values: ["backend", "frontend", "infra", "data", "all"]
  default: "all"
  validation: "Scope module discovery to specified area"

depth_validation:
  allowed_values: ["quick", "standard", "deep"]
  default: "standard"
  quick_depth: "Module boundaries and entry points only"
  standard_depth: "Module boundaries, entry points, and key functions"
  deep_depth: "All standard + call graph expansion and integration boundaries"
```

### Sensitive Data Redaction

When scanning repositories that may contain sensitive information in code or configuration:

**Redaction patterns (apply in this order)**:
```regex
# Credentials and Secrets
API keys:           /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
Passwords:          /password.*/gi → '[REDACTED_PASSWORD]'
Secrets:            /secret.*/gi → '[REDACTED_SECRET]'
Tokens:             /token.*/gi → '[REDACTED_TOKEN]'
License keys:       /license.*/gi → '[REDACTED_LICENSE]'

# Network Information
IP addresses:       /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'
Hostnames:          /\b[a-zA-Z0-9.-]+\.(?:com|net|org|io)\b/gi → '[REDACTED_HOST]'
URLs with creds:    /\b[\w-]+:\/\/[\w-]+:[\w-]+@/gi → '[REDACTED_URL]'

# Database Strings
Connection strings:  /\bpostgresql:\/\/[^\s]+\b/gi → 'postgresql://[REDACTED]'
                    /\bmongodb:\/\/[^\s]+\b/gi → 'mongodb://[REDACTED]'
                    /\bmysql:\/\/[^\s]+\b/gi → 'mysql://[REDACTED]'

# Cloud Keys
AWS keys:           /\bAKIA[0-9A-Z]{16}\b/g → '[REDACTED_AWS_KEY]'
GCP keys:           /\b[0-9a-f]{32}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi → '[REDACTED_GCP_KEY]'
Azure keys:         /\b[0-9a-zA-Z+/]{86,}=*\b/g → '[REDACTED_AZURE_KEY]'

# Personal Data
Email addresses:    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED_EMAIL]'
Phone numbers:      /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g → '[REDACTED_PHONE]'
```

**Code analysis redaction**:
```yaml
logging_redaction:
  - Log all redactions in evidence: "Redacted {count} API keys from source code"
  - Never log original sensitive data
  - Store only redacted evidence in inventory
  - Apply redaction before writing to output files

code_snippet_redaction:
  - Apply to all code snippets in evidence
  - Apply to function signatures with sensitive params
  - Apply to configuration examples
```

### Access Boundaries

- **Repository scope**: Limit analysis to specified repository path
- **Module scoping**: Respect focus scope parameter
- **File access**: Read-only access to source files
- **Network restrictions**: No external network calls during analysis (except to MCP servers)
- **MCP access**: Only access collections/databases user is authorized to access

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # MCP call timeouts
  mcp_call_timeout: 30s              # Per MCP function call
  query_timeout: 45s                  # Per complex query
  batch_timeout: 60s                  # Per batch processing operation

  # Analysis timeouts
  context_loading_timeout: 120s       # mind_mcp context loading
  semantic_mapping_timeout: 240s      # graph_mcp module mapping
  filesystem_scan_timeout: 180s       # Filesystem recon scan
  entry_point_discovery_timeout: 120s # Entry point discovery
  integration_analysis_timeout: 180s  # Integration boundary analysis

  # Phase timeouts
  phase_0_preflight_timeout: 30s      # Preflight and context setup
  phase_1_mind_mcp_timeout: 120s      # mind_mcp project context
  phase_2_graph_mcp_timeout: 240s     # graph_mcp semantic mapping
  phase_3_filesystem_timeout: 180s    # Filesystem cross-check
  phase_4_entry_points_timeout: 120s  # Entry point identification
  phase_5_inventory_timeout: 60s      # Inventory artifact generation

  # Total workflow timeout
  total_workflow_timeout: 900s        # Entire recon (15 minutes)
```

### Resource Limits

```yaml
resource_limits:
  # Repository size limits
  max_repository_size: 1GB            # Prevent memory issues
  max_files_to_scan: 5000             # Limit for large repos
  max_file_size: 10MB                 # Skip files larger than 10MB

  # Analysis limits
  max_modules_to_discover: 100         # Limit for module discovery
  max_entry_points: 200               # Limit for entry point discovery
  max_integration_boundaries: 50      # Limit for integration analysis
  max_functions_per_module: 500       # Limit for module expansion

  # Output limits
  max_inventory_size: 5MB             # Single inventory max size
  max_total_output_size: 100MB        # Total output max size
```

### Progress Feedback

```yaml
progress_reporting:
  # Phase-level progress
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"
    - "  Repository: {repo_name}"
    - "  Scope: {focus_scope}"
    - "  Depth: {depth_preference}"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Results: {results_summary}"
    - "  Modules discovered: {module_count}"

  phase_error:
    - "Phase {N} error: {phase_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  # Task-level progress (for long operations)
  task_progress:
    - "Loading project context: {current}/{total} documents"
    - "Discovering modules: {module_count} modules found"
    - "Analyzing module structure: {current}/{total} modules"
    - "Discovering entry points: {entry_count} entry points"
    - "Mapping integration boundaries: {boundary_count} boundaries"

  # Module-level progress
  module_progress:
    - "Module {module_name}: {purpose}"
    - "  Files: {file_count}"
    - "  Functions: {function_count}"
    - "  Entry points: {entry_count}"
    - "  Status: {status}"

  # Final summary
  final_summary:
    - "Repository reconnaissance complete"
    - "Total duration: {total_duration}s"
    - "Modules discovered: {module_count}"
    - "Entry points identified: {entry_count}"
    - "Integration boundaries: {boundary_count}"
    - "Evidence coverage: {mcp_coverage}%"
    - "Output: {output_files}"
```

### Caching Strategy

```yaml
cache:
  # mind_mcp project context cache
  project_context_cache:
    enabled: true
    ttl: 900                          # 15 minutes
    file: "mcp_project_context_cache.json"
    cache_content:
      - architecture_overview
      - domain_terms
      - module_descriptions
      - service_boundaries
    invalidation: "on_workflow_start"

  # graph_mcp semantic map cache
  semantic_map_cache:
    enabled: true
    ttl: 1200                         # 20 minutes
    file: "mcp_semantic_map_cache.json"
    cache_content:
      - module_boundaries
      - key_functions
      - entry_points
      - integration_paths
    invalidation: "on_repo_change"

  # Module inventory cache
  module_inventory_cache:
    enabled: true
    ttl: 1800                         # 30 minutes
    file: "module_inventory_cache.json"
    cache_content:
      - discovered_modules
      - module_boundaries
      - key_symbols
      - ownership_hints
    invalidation: "on_inventory_approval"

  # Shared evidence cache
  shared_cache:
    enabled: true
    ttl: 2400                         # 40 minutes
    file: "shared_recon_cache.json"
    cache_content:
      - all_mcp_evidence
      - modules
      - entry_points
      - integration_boundaries
    invalidation: "on_workflow_end"

  # Cache hit tracking
  cache_metrics:
    track_cache_hits: true
    track_cache_misses: true
    report_in_summary: true
```

## Error Handling & Fallback Strategy

### Preflight Checks

Before starting reconnaissance:

```yaml
preflight:
  - check: "repository_validation"
    verify:
      - repository_path_exists
      - repository_is_readable
      - repository_is_valid_directory
      - repository_within_size_limit
    action_on_failure: "abort_with_error"

  - check: "focus_scope_validation"
    verify:
      - focus_scope_is_valid
      - depth_preference_is_valid
    action_on_failure: "use_default_settings"

  - check: "mcp_capability_check"
    mind_mcp_functions:
      - list_qdrant_collections
      - list_source_ids
      - hybrid_search
      - get_paragraph_text
    graph_mcp_functions:
      - list_mcp_functions
      - list_parsers
      - list_databases
      - activate_project
      - explore_graph
      - list_up_entrypoint
    action_on_failure: "fallback_to_filesystem_only"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  filesystem_only_mode:
    mode: "filesystem_scan_with_manual_verification"

    steps:
      1. Skip MCP queries entirely
      2. Use filesystem recon script for module discovery
      3. Use directory structure for module boundaries
      4. Use grep/rg patterns for entry point discovery
      5. Mark all evidence as low confidence
      6. Add disclaimer to inventory report

    logging:
      - "Running in FILESYSTEM-ONLY MODE: MCP unavailable"
      - "Analysis limited to filesystem recon script only"
      - "Evidence confidence: LOW for all items"
      - "Module boundaries may be inaccurate"

    notification:
      - "⚠️ MCP services unavailable or degraded"
      - "Running in filesystem-only mode with reduced confidence"
      - "Module boundaries may not match architectural intent"
      - "Manual verification required for critical modules"

  recovery:
    auto_retry: 1                    # Retry 1 time before fallback
    retry_delay: 10s                 # Wait 10s before retry
    backoff_multiplier: 1.0          # No backoff
    max_retry_time: 30s              # Total retry time before fallback
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_0_preflight:
    on_repo_invalid:
      action: "abort_with_error"
      log: "Repository validation failed, aborting"
    on_scope_invalid:
      action: "use_default_scope"
      log: "Invalid scope specified, using default 'all'"

  phase_1_mind_mcp:
    on_mcp_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty context"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial project context retrieved, continuing with available data"

  phase_2_graph_mcp:
    on_mcp_timeout:
      action: "fallback_to_filesystem_scan"
      log: "graph_mcp timeout, using filesystem recon script"
      continue: true
    on_parser_unavailable:
      action: "skip_semantic_analysis"
      log: "Required parser unavailable, using directory-based module detection"
      continue: true

  phase_3_filesystem:
    on_scan_timeout:
      action: "return_partial_results"
      log: "Filesystem scan timeout, returning partial results"
      continue: true
    on_directory_access_error:
      action: "skip_directory_and_log"
      log: "Directory access error, skipping directory"
      continue: true

  phase_4_entry_points:
    on_discovery_timeout:
      action: "use_basic_patterns"
      log: "Entry point discovery timeout, using basic file patterns"
      continue: true

  phase_5_inventory:
    on_report_generation_failure:
      action: "fallback_to_json_output"
      log: "Markdown report generation failed, using JSON output"
      continue: true
```

## Conflict Resolution Rules

When evidence sources conflict during module boundary decisions:

```yaml
conflict_resolution:
  priority_rules:
    1. "For current code structure and module boundaries: Trust graph_mcp over mind_mcp"
       - Example: Module exists in graph but not in docs → Use graph
      - Example: Module boundary in graph vs docs → Use graph

    2. "For architectural intent and domain terms: Trust mind_mcp over graph_mcp"
       - Example: Module purpose and responsibilities → Use docs
      - Example: Domain concepts and terminology → Use docs

    3. "For recent code changes: Trust filesystem (actual files) over MCP"
       - Example: New modules not yet in MCP → Use filesystem
      - Example: Local modifications → Use filesystem

    4. "For historical context and architecture: Trust mind_mcp (archival knowledge)"
       - Example: Why modules are organized this way → Use docs/ADRs
      - Example: Original architectural decisions → Use docs

    5. "For entry points and runtime surfaces: Trust graph_mcp (current code truth)"
       - Example: Entry point functions → Use graph
      - Example: Runtime dependencies → Use graph

  module_boundary_conflicts:
    when: "documented module boundaries differ from actual code structure"
    rules:
      - "If code structure differs from docs: Use code, document discrepancy"
      - "If docs unclear: Use code analysis as primary, document ambiguity"
      - "If both unclear: Mark as unknown, require manual investigation"

  entry_point_conflicts:
    when: "documented entry points differ from discovered entry points"
    rules:
      - "If entry points exist in code but not docs: Use code, add to inventory"
      - "If docs mention entry points not in code: Document as planned/removed"

  logging:
    log_all_conflicts: true
    include_in_inventory: true
    severity_levels: ["RESOLVED_BY_PRIORITY", "MANUAL_VERIFICATION_NEEDED", "DOCUMENTED_INCONSISTENCY"]
```

## Workflow

### Phase 0: Preflight and Context Setup (30s timeout)

```yaml
steps:
  1. Validate all inputs (repo path, focus scope, depth)
  2. Check MCP capabilities via preflight checks
  3. Verify repository and file access
  4. Initialize shared context map
  5. Configure timeouts, limits, and caching
  6. Report: "Preflight complete, starting repository reconnaissance"

shared_context:
  repository_path: "{repo_path}"
  focus_scope: "{backend|frontend|infra|data|all}"
  depth_preference: "{quick|standard|deep}"
  discovered_modules: []

mcp_functions:
  - list_qdrant_collections [required]
  - list_source_ids [optional]
  - list_mcp_functions [required]
  - list_parsers [required]
  - list_databases [required]
  - activate_project [required]

on_failure: "abort or fallback to filesystem-only mode"
```

### Phase 1: Load Project Context from mind_mcp (120s timeout)

```yaml
steps:
  1. Discover available knowledge collections and source ids
  2. Query domain and architecture terms from project knowledge base
  3. Recover procedural sequences when docs contain step-based flows
  4. Apply sensitive data redaction to all extracted content
  5. Store as evidence with citations
  6. Cache results to project_context_cache
  7. Report progress: "Phase 1 complete: {count} context items loaded"

mcp_functions:
  - hybrid_search [required]
    params:
      query: "system architecture OR module responsibilities OR service boundaries OR entry points"
      collection: "{selected_collection}"
      limit: 20
    output:
      - results: list of relevant documents
      - scores: relevance scores
    expected: "Architecture overview, module descriptions, service boundaries"

  - sequential_search [optional]
    params:
      query: "system architecture step by step OR module flow OR service topology"
      collection: "{selected_collection}"
      limit: 10
    output:
      - results: ordered procedure documents
    expected: "Step-by-step architecture descriptions"

  - get_paragraph_text [required]
    params:
      paragraph_ids: ["{ids_from_hybrid_search}"]
    output:
      - text: actual paragraph content
      - citations: source references
    expected: "Detailed content with citations (redacted)"

cache_output:
  file: "mcp_project_context_cache.json"
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

fallback:
  on_mcp_unavailable: "Skip project context loading, set project_context_cache = {}"
  on_timeout: "Return partial results, cache partial context"
```

### Phase 2: Build Semantic Module Map with graph_mcp (240s timeout)

```yaml
steps:
  1. Activate parser/database context first
  2. Use semantic and hybrid graph exploration for module boundaries
  3. Use semantic and hybrid graph exploration for key functions/classes
  4. Use semantic and hybrid graph exploration for upstream entry points
  5. Use semantic and hybrid graph exploration for candidate integration paths
  6. Expand call context around high-centrality functions
  7. Cache results
  8. Report progress: "Phase 2 complete: {count} modules discovered"

mcp_functions:
  - activate_project [required]
    params:
      project_id: "{project_id}"
      database: "{database}"
    output:
      - success: boolean
      - project_info: project metadata

  - explore_graph [required]
    params:
      query: "{module_name} OR {domain_term}"
      limit: 100
    output:
      - nodes: discovered nodes
      - edges: connections
    expected: "Module boundaries and key functions"

  - search_functions [required]
    params:
      query: "main OR init OR controller OR service OR repository"
      limit: 50
    output:
      - functions: matching functions
    expected: "Key functions by module"

  - search_by_code [optional]
    params:
      query: "class.*Controller OR def.*service OR @Repository"
      limit: 50
    output:
      - code_snippets: matching code
    expected: "Implementation patterns"

  - list_up_entrypoint [required]
    params:
      file_pattern: "{focus_scope_pattern}/**/*.{ext}"
      limit: 200
    output:
      - entry_points: API endpoints, main functions
    expected: "Entry points by runtime type"

  - query_subgraph [optional]
    params:
      node_id: "{key_function_id}"
      depth: 3
      limit: 50
    output:
      - subgraph: nodes and edges around key function
    expected: "Call graph around high-centrality functions"

  - trace_flow [optional]
    params:
      start_node: "{entry_point_id}"
      max_depth: 5
    output:
      - flow: execution path
    expected: "Runtime flow from entry points"

cache_output:
  file: "mcp_semantic_map_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    evidence_items:
      - id: node_id
        type: module | function | entry_point | integration_path
        source: graph_mcp
        metadata: {name, file, signature}
        confidence: high | medium | low

fallback:
  on_mcp_unavailable: "Skip semantic mapping, continue to filesystem scan"
  on_timeout: "Return partial results, continue to filesystem scan"
```

### Phase 3: Cross-Check with Filesystem Scan (180s timeout)

```yaml
steps:
  1. Run filesystem recon script for module/language/entry-point scan
  2. Detect blind spots between graph extraction and raw files
  3. Verify directory structure matches module boundaries
  4. Apply sensitive data redaction to all discovered code
  5. Report progress: "Phase 3 complete: {count} files scanned"

recon_script:
  command: |
    python scripts/repo_recon.py /path/to/repo \
      --json /tmp/repo-recon.json \
      --md /tmp/repo-recon.md

  timeout: 180s
  output:
    - modules: discovered modules from directory structure
    - languages: detected programming languages
    - entry_points: discovered entry points from file patterns
    - files: scanned file inventory

  module_discovery:
    - "Directory structure → Module boundaries"
    - "File naming patterns → Module purpose"
    - "Package/namespace structure → Module organization"

  language_detection:
    - "File extensions → Programming languages"
    - "Config files → Build systems and frameworks"

  entry_point_detection:
    - "main/index/app files → Entry points"
    - "Controller/handler files → API entry points"
    - "Worker/consumer files → Background job entry points"

  redaction_applied:
    - All credentials redacted from code snippets
    - All API keys redacted from configs
    - All connection strings redacted

fallback:
  on_script_failure: "Use manual directory traversal for module discovery"
  on_timeout: "Return partial results, document coverage gap"
```

### Phase 4: Identify Entry Points and Runtime Surfaces (120s timeout)

```yaml
steps:
  1. Prefer graph_mcp entry-point functions and traced calls
  2. Augment with filesystem-only startup files when graph coverage is incomplete
  3. Classify entry points by runtime type (API, worker, CLI, library)
  4. Verify entry points have call graph evidence when possible
  5. Report progress: "Phase 4 complete: {count} entry points identified"

entry_point_classification:
  api_runtime:
    indicators:
      - "HTTP server initialization (app.listen, server.start)"
      - "API route definitions (@app.route, @RequestMapping)"
      - "Controller/handler files"
    evidence: "graph_mcp call graph + filesystem patterns"

  worker_runtime:
    indicators:
      - "Queue consumer initialization"
      - "Job/worker registration"
      - "Scheduler configuration"
    evidence: "graph_mcp call graph + filesystem patterns"

  cli_runtime:
    indicators:
      - "Command-line argument parsing"
      - "main() function with CLI args"
      - "CLI framework usage (click, argparse)"
    evidence: "graph_mcp call graph + filesystem patterns"

  library_runtime:
    indicators:
      - "Package exports"
      - "Public API definitions"
      - "No entry point (library/package)"
    evidence: "package.json + module exports"

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

fallback:
  on_mcp_unavailable: "Use filesystem-only entry point patterns"
  on_timeout: "Use basic file pattern matching"
```

### Phase 5: Produce Inventory Artifact (60s timeout)

```yaml
steps:
  1. Use module-inventory-template.md for consistent report format
  2. Include module list with purpose, ownership hint, and key symbols
  3. Include entry points by runtime type with graph evidence
  4. Include knowledge-base context links from mind_mcp
  5. Include open questions and assumptions
  6. Report progress: "Phase 5 complete: Inventory artifact generated"

inventory_sections:
  context:
    - repository: string
    - commit/branch: string
    - scan_date: ISO8601
    - scope: string

  top_level_modules:
    columns:
      - module: string
      - purpose: string
      - key_files: []
      - dominant_languages: []
      - notes: string

  entry_points:
    columns:
      - runtime: api | worker | cli | library
      - file/path: string
      - trigger: string
      - notes: string

  integration_boundaries:
    columns:
      - module: string
      - inbound_interfaces: []
      - outbound_dependencies: []
      - risk: low | medium | high

  unknowns_and_next_probes:
    - unknown: string
    - why_uncertain: string
    - suggested_probe: string

output_files:
  - "repo_recon.json": Machine-readable structure for follow-up tooling
  - "repo_recon.md": Concise human-readable inventory
  - "mcp_evidence.md": Captured MCP query outputs and confidence notes (optional)

fallback:
  on_report_generation_failure: "Fallback to JSON output only"
```

## Output Contract

### Document Package Structure

```yaml
output_location: "<target>/.github/repo-recon/"

mandatory_outputs:
  inventory:
    - "repo_recon.json" - Machine-readable structure
    - "repo_recon.md" - Human-readable inventory

  optional_outputs:
    - "mcp_evidence.md" - MCP query logs and confidence notes
    - "module_graph.json" - Module dependency graph
    - "entry_points_detail.json" - Detailed entry point analysis
```

## Non-Negotiable Rules

- ✅ Never invent modules or entry points without evidence
- ✅ Never assume module boundaries without verification
- ✅ Always validate inputs before analysis (security)
- ✅ Always redact sensitive data before writing to output (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always cache MCP evidence to improve efficiency (performance)
- ✅ Always include evidence source tags in every claim (traceability)
- ✅ Always mark conflicting evidence with resolution rules (consistency)

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  recon_progress:
    - total_phases: "Total workflow phases"
    - completed_phases: "Completed phases"
    - current_phase: "Current phase in progress"

  module_coverage:
    - modules_discovered: "Modules discovered"
    - modules_with_purpose: "Modules with documented purpose"
    - modules_with_ownership: "Modules with ownership hints"
    - modules_with_entry_points: "Modules with entry points"

  entry_point_coverage:
    - api_entry_points: "API entry points discovered"
    - worker_entry_points: "Worker entry points discovered"
    - cli_entry_points: "CLI entry points discovered"
    - library_entry_points: "Library entry points discovered"

  evidence_quality:
    - total_claims: "Total inventory claims"
    - mcp_sourced_claims: "Claims with MCP evidence"
    - mind_mcp_sourced_claims: "Claims from mind_mcp"
    - graph_mcp_sourced_claims: "Claims from graph_mcp"
    - filesystem_sourced_claims: "Claims from filesystem"
    - mcp_evidence_percentage: "MCP coverage percentage"

  integration_analysis:
    - integration_boundaries: "Integration boundaries discovered"
    - high_risk_boundaries: "High-risk integration points"
    - circular_dependencies: "Circular dependency warnings"

  mcp_performance:
    - mind_mcp_calls_total: "Total mind_mcp calls"
    - mind_mcp_calls_successful: "Successful mind_mcp calls"
    - mind_mcp_calls_failed: "Failed mind_mcp calls"
    - graph_mcp_calls_total: "Total graph_mcp calls"
    - graph_mcp_calls_successful: "Successful graph_mcp calls"
    - graph_mcp_calls_failed: "Failed graph_mcp calls"
    - cache_hit_rate: "Percentage of cache hits"
```

## Quality Gates

```yaml
quality_gates:
  gate_1_evidence_coverage:
    threshold: 60
    check: "mcp_evidence_percentage >= 60"
    on_fail:
      action: "report_gaps_and_continue"
      add_warning: true

  gate_2_module_claims:
    threshold: 100
    check: "all_module_claims_have_evidence"
    on_fail:
      action: "flag_unsubstantiated_claims"
      add_warning: true

  gate_3_entry_point_capture:
    check: "entry_points_captured_per_runtime"
    on_fail:
      action: "document_missing_entry_points"
      add_note: true

  gate_4_conflict_resolution:
    check: "all_conflicts_resolved_or_documented"
    on_fail:
      action: "add_manual_verification_flag"
      add_warning: true
```

## Version History & Changelog

### Version 2.0.0 (2025-04-16)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration (was unlimited, now 15min max)
- Enhanced fallback strategy (was implicit, now explicit with rules)

**New Features:**
- ✅ Added Security & Privacy section with validation and redaction
- ✅ Added Performance & UX section with timeouts, progress feedback, caching
- ✅ Enhanced fallback strategy with filesystem-only mode
- ✅ Added conflict resolution rules for module boundary decisions
- ✅ Added specific MCP function names with parameters and outputs
- ✅ Added observability metrics and quality gates
- ✅ Added version history and changelog

**Improvements:**
- Enhanced MCP integration with specific function names
- Added preflight checks for MCP and path validation
- Enhanced error handling with specific recovery strategies per phase
- Added progress reporting after each phase
- Added conflict resolution rules with conservative documentation
- Added quality gates for evidence coverage and module claims
- Enhanced integration boundary analysis

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on MCP down)
- Fixed: No conflict resolution (module boundary contradictions unresolved)
- Fixed: No progress feedback (poor UX for long scans)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update inventory template if using custom output format

### Version 1.0.0 (Initial Release)

- Initial workflow for repository reconnaissance
- Basic MCP integration (mind_mcp, graph_mcp)
- Evidence-based module discovery
- Filesystem recon script integration
- Module inventory and entry point mapping
- Basic quality gates and coverage metrics

## Known Limitations

```yaml
limitations:
  mcp_dependent:
    - "Requires both mind_mcp and graph_mcp for full functionality"
    - "Filesystem-only mode has significantly reduced accuracy and confidence"
    - "Historical context unavailable if mind_mcp is down"

  performance:
    - "Very large repositories (>500k files) may exceed timeouts"
    - "Monorepos with many modules may hit max_modules limit"
    - "Deep call graph expansion may timeout on large codebases"

  analysis_scope:
    - "Only analyzes specified repository"
    - "Cannot analyze external dependencies without source code"
    - "Cannot capture runtime behavior without execution traces"

  module_detection:
    - "Best effort detection based on directory structure and code patterns"
    - "May miss implicit modules or cross-cutting concerns"
    - "May misclassify modules in non-standard layouts"

  entry_point_detection:
    - "Requires graph_mcp for accurate call graph-based entry points"
    - "May miss dynamic or configuration-driven entry points"
    - "Filesystem-only mode has reduced accuracy"

  integration_analysis:
    - "Limited to explicit dependencies in code"
    - "May miss runtime or data dependencies"
    - "Cannot detect integration through shared databases or queues"
```

## Deliverables

- Module inventory with purpose and ownership hints
- Entry point map by runtime type
- Integration boundary analysis
- Knowledge-base context links
- Open questions and assumptions documentation

## References

- `scripts/repo_recon.py`: Automated module/language/entry-point scan
- `references/module-inventory-template.md`: Report structure for consistent summaries
- `references/mcp-recon-playbook.md`: Query recipes for mind_mcp and graph_mcp
- `references/quality-gates.md`: Exit criteria and review checklist
- `references/source-material-index.md`: Canonical source files used
