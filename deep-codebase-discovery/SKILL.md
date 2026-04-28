---
name: deep-codebase-discovery
description: Orchestrate end-to-end deep codebase discovery by combining mind_mcp project knowledge retrieval, graph_mcp semantic and call-graph exploration, and structured synthesis across repo-recon, tech-build-audit, and module-summary-report skills. Use when you need a complete onboarding-quality technical assessment with module mapping, stack/build/platform analysis, critical flows, and prioritized risks.
version: 2.0.0
last_updated: 2025-04-16
---

# Deep Codebase Discovery

Coordinate MCP-first discovery in a strict multi-phase pipeline with comprehensive security hardening, operational resilience, and evidence-based synthesis.

## When To Use

- First-time onboarding to a large or unfamiliar codebase.
- Need an end-to-end technical assessment across structure, stack, flows, and risks.
- Need one orchestrated output that chains recon + build audit + summary.
- Preparing architecture reviews, handover documentation, or migration assessments.
- Building understanding for new team members or external stakeholders.

## Avoid Using When

- You only need one narrow answer (module map only, bug impact only, or stack only).
- Repo scope is tiny and a quick manual scan is enough.
- You cannot access MCP and only need a fast high-level note.
- Analyzing a single isolated function or bug (use bug-impact-analyzer instead).

## Required Inputs

- Repository root path.
- Target project identifier for MCP contexts (database/collection/source id if known).
- Scope preference: `full`, `backend`, `frontend`, `infra`, or `focused`.
- Optional audience: `engineering`, `management`, or `mixed`.

## Input Validation & Security

### Path Validation

- **Repository path**: Must exist, be within allowed scope, and be readable by current user
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **Path sanitization**: Remove null bytes, limit to 1000 characters, whitelist allowed characters
- **Access verification**: Verify user has read access to repository before analysis

**Validation rules**:
```yaml
path_validation:
  - repository_path must be a valid directory
  - repository_path must be a git repository (optional, for Git-specific features)
  - Block path traversal: reject if contains "../" or absolute path
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max length: 1000 characters
  - Must be readable: os.access(path, os.R_OK)
```

### Project Identifier Validation

- **Project ID**: Format validation (alphanumeric with hyphens/underscores)
- **Collection IDs**: Validate against available collections
- **Database/Parser**: Validate against available graph databases

**Validation rules**:
```yaml
project_id_validation:
  - Format: /^[a-zA-Z0-9_-]+$/
  - Max length: 100 characters
  - Check against available mind_mcp collections
  - Check against available graph_mcp databases

collection_id_validation:
  - Must exist in list_qdrant_collections output
  - Must be accessible: test with hybrid_search(limit=1)
  - Optional: if not provided, use default collection
```

### Scope Parameter Validation

- **Scope values**: Must be one of `full`, `backend`, `frontend`, `infra`, `focused`
- **Audience values**: Must be one of `engineering`, `management`, `mixed`

**Validation rules**:
```yaml
scope_validation:
  allowed_values: ["full", "backend", "frontend", "infra", "focused"]
  default: "full"
  error_message: "Invalid scope. Must be one of: full, backend, frontend, infra, focused"

audience_validation:
  allowed_values: ["engineering", "management", "mixed"]
  default: "mixed"
  error_message: "Invalid audience. Must be one of: engineering, management, mixed"
```

### Sensitive Data Redaction

When processing code and documentation that may contain sensitive information:

**Redaction patterns (apply in this order)**:
```regex
# API Keys and Tokens
API keys:           /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
Bearer tokens:      /Bearer\s+[A-Za-z0-9\-._~+/]+=*/gi → 'Bearer [REDACTED]'
Authorization:     /Authorization:\s*[A-Za-z0-9\-._~+/]+/gi → 'Authorization: [REDACTED]'
API keys in URLs:  /\?key=[A-Za-z0-9\-._~+/]+/gi → '?key=[REDACTED]'

# Credentials
Passwords:          /password.*/gi → '[REDACTED_PASSWORD]'
Secrets:            /secret.*/gi → '[REDACTED_SECRET]'
Tokens:             /token.*/gi → '[REDACTED_TOKEN]'

# Personal Data
Email addresses:    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED_EMAIL]'
Phone numbers:      /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g → '[REDACTED_PHONE]'
SSN:                /\b\d{3}-\d{2}-\d{4}\b/g → '[REDACTED_SSN]'
IP addresses:       /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'

# Database URLs
Database URLs:      /\bpostgresql:\/\/[^\s]+\b/gi → 'postgresql://[REDACTED]'
                    /\bmongodb:\/\/[^\s]+\b/gi → 'mongodb://[REDACTED]'
                    /\bredis:\/\/[^\s]+\b/gi → 'redis://[REDACTED]'
```

**Logging redaction**:
```yaml
logging_redaction:
  - Log all redactions in evidence trace: "Redacted 3 API keys from config file"
  - Never log original sensitive data
  - Store only redacted evidence in output files
  - Apply redaction before caching to MCP cache files
```

### Access Boundaries

- **Repository scope**: Limit analysis to specified repository path
- **Module scoping**: Respect scope parameter (full/backend/frontend/infra/focused)
- **Permission checks**: Verify read access before each filesystem operation
- **Network restrictions**: No external network calls except to MCP servers
- **MCP access**: Only access collections/databases user is authorized to access

**Access control verification**:
```yaml
access_control:
  repository_access:
    - Verify read access: os.access(repo_path, os.R_OK)
    - List directory: os.listdir(repo_path)
    - Check for .git directory (optional)

  mcp_access:
    - mind_mcp: Verify collection access with list_qdrant_collections
    - graph_mcp: Verify database access with list_databases
    - If unauthorized: Log warning and skip that source
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # MCP call timeouts
  mcp_call_timeout: 30s              # Per MCP function call
  query_timeout: 45s                  # Per complex query (hybrid_search, explore_graph)
  batch_timeout: 60s                  # Per batch processing operation

  # Phase timeouts
  phase_0_preflight_timeout: 30s      # Preflight and health check
  phase_1_knowledge_sweep_timeout: 180s # mind_mcp knowledge sweep
  phase_2_semantic_mapping_timeout: 300s # graph_mcp semantic mapping
  phase_3_skill_chain_timeout: 600s    # Skill chain execution
  phase_4_reconciliation_timeout: 60s  # Evidence reconciliation
  phase_5_bundle_generation_timeout: 60s # Bundle generation

  # Total workflow timeout
  total_workflow_timeout: 900s        # Entire analysis (15 minutes)

  # Timeout handling
  on_timeout:
    action: "return_partial_results"
    log: "Phase timeout reached, returning partial results"
    notify_user: "Analysis incomplete due to timeout. Results may be incomplete."
    continue_next_phase: true
```

### Context Control Limits

```yaml
context_control:
  # For large codebases (>100k LOC)
  max_results_per_query:
    search_functions: 50              # Limit search_functions results
    explore_graph: 100                # Limit explore_graph results
    hybrid_search: 20                 # Limit hybrid_search results
    query_subgraph: 50                # Limit query_subgraph results

  batch_processing:
    batch_size: 20                    # Process 20 nodes at a time
    get_node_details_batch: 20        # Batch node details requests
    user_confirmation_required: true  # Require confirmation for deep expansion

  traversal_limits:
    max_depth: 5                      # Call graph traversal depth
    max_modules: 50                   # Maximum modules to analyze
    max_entry_points: 100             # Maximum entry points to trace
```

### Caching Strategy

```yaml
cache:
  # mind_mcp knowledge cache
  knowledge_cache:
    enabled: true
    ttl: 600                          # 10 minutes
    file: "mcp_knowledge_cache.json"
    cache_content:
      - architecture_intent
      - module_definitions
      - platform_constraints
      - build_process_docs
    invalidation: "on_workflow_start"

  # graph_mcp graph cache
  graph_cache:
    enabled: true
    ttl: 900                          # 15 minutes
    file: "mcp_graph_cache.json"
    cache_content:
      - module_boundaries
      - entry_points
      - call_graphs
      - api_dependencies
    invalidation: "on_repo_change"

  # Shared evidence cache (for skill chain)
  shared_cache:
    enabled: true
    ttl: 1200                         # 20 minutes
    file: "shared_evidence_cache.json"
    cache_content:
      - all_mcp_evidence
      - reconciled_evidence
    invalidation: "on_workflow_end"

  # Cache hit tracking
  cache_metrics:
    track_cache_hits: true
    track_cache_misses: true
    report_in_bundle: true
```

### Progress Feedback

```yaml
progress_reporting:
  # Phase-level progress
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"
    - "  Context: {context_description}"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Results: {results_summary}"
    - "  Cache hit rate: {cache_hit_rate}%"

  phase_error:
    - "Phase {N} error: {phase_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  # Task-level progress (for long operations)
  task_progress:
    - "Processing batch {batch_num}/{total_batches}"
    - "Analyzed {current}/{total} modules"
    - "Cached {cache_hits} items, {cache_misses} cache misses"

  # Final summary
  final_summary:
    - "Discovery analysis complete"
    - "Total duration: {total_duration}s"
    - "Total claims: {total_claims}"
    - "MCP-sourced claims: {mcp_claims} ({percentage}%)"
    - "Cache hit rate: {cache_hit_rate}%"
    - "Output: {output_files}"
```

## Error Handling & Fallback Strategy

### Preflight Checks

Before starting analysis:

```yaml
preflight:
  - check: "mcp_capability_check"
    mind_mcp_functions:
      - list_qdrant_collections
      - list_source_ids
      - hybrid_search
      - get_paragraph_text
      - query_graph_rag_relation [optional]
      - query_worksheet [optional]
    graph_mcp_functions:
      - list_mcp_functions
      - list_parsers
      - list_databases
      - activate_project
      - explore_graph
      - list_up_entrypoint
    action_on_failure: "fallback_to_degraded_mode"

  - check: "repository_access_check"
    verify:
      - repository_path_exists
      - repository_is_readable
      - repository_has_code (at least 1 source file)
    action_on_failure: "abort_with_error"

  - check: "input_validation"
    validate:
      - repository_path_format
      - project_id_format
      - scope_parameter_valid
      - audience_parameter_valid
    action_on_failure: "sanitize_or_abort"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  degraded_mode:
    mode: "filesystem_scan_with_reduced_confidence"

    steps:
      1. Skip MCP queries and use filesystem-only analysis
      2. Use grep/find for code structure discovery
      3. Use manual documentation review (README, docs/)
      4. Run skill chain with reduced functionality:
         - repo-recon: Filesystem scan only
         - tech-build-audit: Config file analysis only
         - module-summary-report: Synthesize available evidence
      5. Set all confidence levels: HIGH → MEDIUM, MEDIUM → LOW
      6. Add disclaimer to output

    logging:
      - "Running in DEGRADED MODE: MCP unavailable"
      - "Analysis limited to filesystem scan only"
      - "Evidence confidence reduced: HIGH → MEDIUM, MEDIUM → LOW"
      - "Cache files not created"

    notification:
      - "⚠️ MCP services unavailable or degraded"
      - "Running in filesystem-only mode with reduced confidence"
      - "Results may be incomplete. Consider retrying when MCP is available"

  recovery:
    auto_retry: 2                    # Retry 2 times before fallback
    retry_delay: 5s                  # Wait 5s between retries
    backoff_multiplier: 1.5          # Reduce backoff for faster retry
    max_retry_time: 30s              # Total retry time before fallback
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_0_preflight:
    on_mcp_unavailable:
      action: "fallback_to_degraded_mode"
      log: "MCP unavailable in preflight, entering degraded mode"
    on_repo_inaccessible:
      action: "abort_with_error"
      log: "Repository inaccessible, aborting discovery"

  phase_1_knowledge_sweep:
    on_mcp_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty knowledge"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial knowledge retrieved, continuing with available data"

  phase_2_semantic_mapping:
    on_mcp_timeout:
      action: "return_cached_or_empty"
      log: "graph_mcp timeout, using cached results or empty graph"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial graph retrieved, continuing with available data"

  phase_3_skill_chain:
    on_skill_failure:
      action: "continue_to_next_skill"
      log: "Skill {skill_name} failed, continuing to next skill"
      continue: true

  phase_4_reconciliation:
    on_evidence_conflict:
      action: "apply_conflict_resolution_rules"
      log: "Evidence conflict detected, applying resolution rules"

  phase_5_bundle_generation:
    on_incomplete_evidence:
      action: "generate_partial_bundle"
      log: "Incomplete evidence, generating partial bundle"
      add_warning: true
```

## Conflict Resolution Rules

When evidence sources conflict:

```yaml
conflict_resolution:
  priority_rules:
    1. "For code structure and implementation: Trust graph_mcp over mind_mcp"
       - Example: Function exists in graph but not in docs → Use graph
      - Example: Module boundaries in graph vs docs → Use graph

    2. "For domain concepts and business rules: Trust mind_mcp over graph_mcp"
       - Example: Business logic interpretation → Use docs
      - Example: Module purpose descriptions → Use docs

    3. "For recent changes: Trust graph_mcp (current state)"
       - Example: Function signature changed → Use actual code
      - Example: New modules added → Use graph

    4. "For historical context and architecture intent: Trust mind_mcp (archival)"
       - Example: Why this was implemented → Use docs/ADRs
      - Example: Original design decisions → Use docs

    5. "For build and deployment configuration: Trust filesystem (actual files)"
       - Example: Build system type → Check actual build files
      - Example: Dependencies → Check package.json/requirements.txt

    6. "For test coverage: Trust graph_mcp (actual tests)"
       - Example: Which functions are tested → Use test file analysis
      - Example: Test types (unit/integration) → Use test structure

  tiebreaker:
    when: "both sources have equal confidence but disagree"
    action: "report_both_with_disclaimer"
    format: |
      CONFLICT DETECTED:
      - mind_mcp says: {mind_mcp_claim} (confidence: {confidence})
      - graph_mcp says: {graph_mcp_claim} (confidence: {confidence})
      Resolution: Manual verification required
      Recommendation: {recommendation}

  filesystem_integration:
    when: "filesystem evidence differs from MCP"
    rules:
      - "If MCP unavailable: Use filesystem as primary source"
      - "If filesystem disagrees with graph_mcp: Trust filesystem for configs, graph for code"
      - "If filesystem disagrees with mind_mcp: Trust filesystem for current state, docs for intent"

  logging:
    log_all_conflicts: true
    include_in_report: true
    severity_levels: ["RESOLVED_BY_PRIORITY", "MANUAL_VERIFICATION_NEEDED", "UNRESOLVED"]
```

## Orchestration Workflow

### Phase 0: Preflight and Health Check (30s)

```yaml
steps:
  1. Validate all inputs (paths, project ID, scope, audience)
  2. Check MCP capabilities via preflight checks
  3. Verify repository access and permissions
  4. Initialize shared context map
  5. Configure timeouts, limits, and caching
  6. Report: "Preflight complete, starting discovery"

shared_context:
  project_id: "{project_id}"
  collection_ids: "{list from mind_mcp}"
  graph_database: "{database from graph_mcp}"
  parser: "{parser from graph_mcp}"
  analysis_timestamp: "{ISO8601}"
  scope: "{scope parameter}"
  audience: "{audience parameter}"

mcp_functions:
  - list_qdrant_collections [required]
  - list_source_ids [optional]
  - list_mcp_functions [required]
  - list_parsers [required]
  - list_databases [required]
  - activate_project [required]

on_failure: "abort or fallback to degraded mode"
```

### Phase 1: Knowledge Sweep with mind_mcp (Cached, 3min)

```yaml
steps:
  1. Query architecture intent and domain terms
  2. Extract module definitions and responsibilities
  3. Retrieve build/release process documentation
  4. Get runtime environment and deployment model
  5. Capture platform constraints and operational considerations
  6. Cache results to mcp_knowledge_cache.json
  7. Report progress: "Phase 1 complete: {count} knowledge items cached"

mcp_functions:
  - list_qdrant_collections [required]
    params: {}
    output:
      - collections: list of available collections
      expected: "List of accessible collections"

  - list_source_ids [optional]
    params: {}
    output:
      - source_ids: list of available source IDs
      expected: "List of accessible sources"

  - hybrid_search [required]
    params:
      query: "{architecture_intent_query}"
      collection: "{selected_collection}"
      limit: 20
    output:
      - results: list of relevant documents
      - scores: relevance scores
      expected: "Architecture documentation"

  - sequential_search [optional]
    params:
      query: "{process_query}"
      collection: "{selected_collection}"
      limit: 10
    output:
      - results: ordered procedure documents
      expected: "Build/release process docs"

  - get_paragraph_text [required]
    params:
      paragraph_ids: ["{ids_from_hybrid_search}"]
    output:
      - text: actual paragraph content
      - citations: source references
      expected: "Detailed content with citations"

  - query_graph_rag_relation [optional]
    params:
      entity: "{module_or_component}"
      relation_types: ["depends_on", "implements", "related_to"]
    output:
      - relations: cross-entity/document relationships
      expected: "Cross-reference relationships"

  - query_worksheet [optional]
    params:
      worksheet_id: "{worksheet_id}"
      query: "{structured_query}"
    output:
      - rows: structured worksheet data
      expected: "Structured data retrieval"

cache_output:
  file: "mcp_knowledge_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    collections: ["{collection_ids}"]
    evidence_items:
      - id: unique_id
        type: architecture_intent | module_def | platform_constraint | process_doc
        source: mind_mcp
        ref: paragraph_id or result_id
        confidence: high | medium | low
        content: summarized content

fallback:
  on_mcp_unavailable: "Skip knowledge sweep, set knowledge_cache = {}"
  on_timeout: "Return partial results, cache partial knowledge"
```

### Phase 2: Semantic and Flow Mapping with graph_mcp (Cached, 5min)

```yaml
steps:
  1. Discover module boundaries via semantic graph exploration
  2. Identify entry points (API endpoints, CLI commands, main functions)
  3. Search for key functions by domain (auth, payment, scheduler, etc.)
  4. Search for concrete implementation patterns (SQL, HTTP client, env usage)
  5. Query subgraphs around critical functions
  6. Trace runtime flows and identify critical call paths
  7. Detect API boundary violations (direct driver calls)
  8. Capture high-centrality functions and cross-module coupling
  9. Cache results to mcp_graph_cache.json
  10. Report progress: "Phase 2 complete: {count} graph items cached"

mcp_functions:
  - list_mcp_functions [preflight]
    params: {}
    output:
      - functions: list of available graph_mcp functions
      expected: "Function catalog"

  - list_parsers [required]
    params: {}
    output:
      - parsers: list of available parsers
      expected: "Parser options"

  - list_databases [required]
    params: {}
    output:
      - databases: list of available databases
      expected: "Database options"

  - activate_project [required]
    params:
      project_id: "{project_id}"
      database: "{selected_database}"
      parser: "{selected_parser}"
    output:
      - status: activated
      - node_count: total nodes
      - edge_count: total edges
      expected: "Project activated"

  - explore_graph [required]
    params:
      query: "{module_or_function}"
      limit: 100
    output:
      - nodes: discovered nodes
      - edges: connections
      expected: "Module/function discovery"

  - list_up_entrypoint [required]
    params:
      file_pattern: "{scope_filter}"  # e.g., "*.py" for backend
      limit: 100
    output:
      - entry_points: API endpoints, main functions
      expected: "Entry point discovery"

  - search_functions [required]
    params:
      query: "{domain_term}"  # e.g., "auth", "payment"
      limit: 50
    output:
      - functions: matching functions
      expected: "Domain-specific function discovery"

  - search_by_code [optional]
    params:
      code_pattern: "{pattern}"  # e.g., "SELECT", "http.get", "os.getenv"
      limit: 50
    output:
      - locations: code locations matching pattern
      expected: "Implementation pattern discovery"

  - query_subgraph [required]
    params:
      node_id: "{critical_function_id}"
      depth: 3
      limit: 50
    output:
      - subgraph: nodes and edges around function
      expected: "Context around critical functions"

  - trace_flow [optional]
    params:
      start_node: "{entry_point_id}"
      max_depth: 5
    output:
      - flow: execution path
      expected: "Runtime flow tracing"

  - find_paths [optional]
    params:
      start_node: "{start_id}"
      end_node: "{end_id}"
      max_paths: 10
    output:
      - paths: paths between nodes
      expected: "Path discovery"

  - find_path_between_module [optional]
    params:
      start_module: "{module_a}"
      end_module: "{module_b}"
      max_depth: 5
    output:
      - paths: cross-module paths
      expected: "Cross-module boundary discovery"

  - trace_flow_between_module [optional]
    params:
      start_module: "{module_a}"
      end_module: "{module_b}"
      max_depth: 5
    output:
      - flows: cross-module flows
      expected: "Cross-module flow tracing"

  - get_node_details [required]
    params:
      node_ids: ["{node_ids}"]  # Batch 10-20 at a time
    output:
      - details: node metadata
      expected: "Node detail retrieval"

  - get_symbol [optional]
    params:
      symbol_id: "{symbol_id}"
    output:
      - symbol: symbol details
      expected: "Symbol detail retrieval"

  - find_callers_of_endpoint [optional]
    params:
      endpoint_id: "{endpoint_id}"
      limit: 50
    output:
      - callers: endpoint callers
      expected: "API caller discovery"

  - get_api_call_chain [optional]
    params:
      endpoint_id: "{endpoint_id}"
      max_depth: 5
    output:
      - chain: API call chain
      expected: "API call chain discovery"

  - find_workflows_containing [optional]
    params:
      node_id: "{function_id}"
    output:
      - workflows: workflows containing function
      expected: "Workflow discovery"

  - analyze_workflow_impact [optional]
    params:
      workflow_id: "{workflow_id}"
    output:
      - impact: workflow impact analysis
      expected: "Workflow impact assessment"

api_warning_subflow:
  steps:
    1. Discover API entry nodes (controller/handler/routes)
    2. Discover driver/DB nodes
    3. Run path search entry → driver
    4. Flag HIGH when path bypasses service/repository nodes
    5. Enrich with find_callers_of_endpoint and get_api_call_chain
    6. Cache warnings with path evidence

cache_output:
  file: "mcp_graph_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    parser: "{parser}"
    evidence_items:
      - id: node_id
        type: function | class | module | entrypoint
        source: graph_mcp
        metadata: {name, file, signature}
        neighbors: [node_ids]
        detail_level: compact

fallback:
  on_mcp_unavailable: "Skip semantic mapping, set graph_cache = {}"
  on_timeout: "Return partial results, cache partial graph"
```

### Phase 3: Run Skill Chain with Evidence Injection (10min)

```yaml
steps:
  1. Load cached MCP evidence (mcp_knowledge_cache.json, mcp_graph_cache.json)
  2. Run repo-recon with evidence injection
  3. Run tech-build-audit with evidence injection
  4. Run module-summary-report with all evidence
  5. Merge outputs and evidence tags
  6. Report progress: "Phase 3 complete: {skills_count} skills executed"

skill_1_repo_recon:
  input:
    - mcp_knowledge_cache.json
    - mcp_graph_cache.json
  workflow:
    1. Load cached evidence first
    2. Use cached results to scope queries
    3. Run filesystem scan only for gaps
    4. Merge cached evidence with filesystem evidence
  output:
    - repo_recon.json (with evidence tags)
    - repo_recon.md (with evidence tags)

skill_2_tech_build_audit:
  input:
    - mcp_knowledge_cache.json
    - mcp_graph_cache.json
  workflow:
    1. Load cached evidence first
    2. Use cached results to identify build/runtime surfaces
    3. Run filesystem audit only for config validation
    4. Merge cached evidence with config evidence
  output:
    - tech_build_audit.json (with evidence tags)
    - tech_build_audit.md (with evidence tags)

skill_3_module_summary_report:
  input:
    - mcp_knowledge_cache.json
    - mcp_graph_cache.json
    - repo_recon.*
    - tech_build_audit.*
  workflow:
    1. Load all evidence sources
    2. Reconcile conflicts using priority rules
    3. Synthesize into stakeholder-facing summary
  output:
    - summary.md (with comprehensive evidence tags)

fallback:
  on_skill_failure: "Continue to next skill, log error"
  on_cache_unavailable: "Run skills without cache (reduced efficiency)"
```

### Phase 4: Evidence Reconciliation (1min)

```yaml
steps:
  1. Load all evidence sources
  2. Attach source tags to each claim (mind_mcp, graph_mcp, filesystem)
  3. Track cache_hit for each claim (for MCP efficiency metrics)
  4. Apply conflict resolution rules
  5. Mark unresolved conflicts for follow-up
  6. Report progress: "Phase 4 complete: {claims_count} claims reconciled"

evidence_tags:
  source_type: mind_mcp | graph_mcp | filesystem
  source_ref: tool/result id or file path
  confidence: high | medium | low
  cache_hit: true | false

conflict_resolution:
  rules:
    - Implementation truth: graph_mcp
    - Domain/process truth: mind_mcp
    - Configuration truth: filesystem
  unresolved_action: "Create follow-up action"
```

### Phase 5: Produce Discovery Bundle (1min)

```yaml
steps:
  1. Load discovery-bundle-template.md
  2. Fill in all sections with reconciled evidence
  3. Generate machine-readable discovery_bundle.json
  4. Attach efficiency metrics
  5. Add evidence provenance metadata
  6. Report progress: "Phase 5 complete: Discovery bundle generated"

output_files:
  - discovery_summary.md: final stakeholder-facing summary
  - discovery_bundle.json: machine-readable artifact index
  - mcp_knowledge_cache.json: cached mind_mcp evidence
  - mcp_graph_cache.json: cached graph_mcp evidence
  - repo_recon.*: optional supporting files
  - tech_build_audit.*: optional supporting files
  - summary.md: optional comprehensive summary

bundle_structure: discovery-bundle-template.md
```

## Quality Gates

### Evidence Quality

- Every major section **must** contain MCP evidence references
- At least one critical runtime flow **must** be derived from graph_mcp path/query
- Build/deploy claims **must** include explicit knowledge or file evidence
- API dependency warnings **must** include severity and mitigation recommendation
- Final risks **must** be prioritized with impact and confidence
- Unknowns **must** include concrete next probe actions

### Source Attribution

- Each claim **must** have source_type tag (mind_mcp, graph_mcp, filesystem)
- Each claim **must** have confidence level (high, medium, low)
- Each claim **must** track cache_hit (for efficiency metrics)
- Conflicting evidence **must** be flagged and resolved

### Output Completeness

- Module inventory **must** include purpose and key symbols
- Technology/build/platform matrix **must** have evidence references
- Critical call flows **must** trace from entry point to implementation
- API dependency warnings **must** include severity and suggested fixes
- Top risks **must** be prioritized by impact and confidence

### Efficiency Tracking

- Report total_claims vs mcp_sourced_claims
- Report cache_hit_rate (target: >70%)
- Report cache_miss_queries (for optimization)
- Report context_control_batches (for large codebases)

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  workflow_duration:
    - phase_0_duration_seconds
    - phase_1_duration_seconds
    - phase_2_duration_seconds
    - phase_3_duration_seconds
    - phase_4_duration_seconds
    - phase_5_duration_seconds
    - total_workflow_duration_seconds

  evidence_quality:
    - total_claims
    - mcp_sourced_claims
    - mind_mcp_sourced_claims
    - graph_mcp_sourced_claims
    - filesystem_sourced_claims
    - cache_hit_rate
    - cache_miss_queries
    - conflicting_evidence_count

  analysis_scope:
    - modules_analyzed
    - functions_discovered
    - entry_points_found
    - api_warnings_detected
    - critical_paths_traced

  mcp_performance:
    - mind_mcp_calls_total
    - mind_mcp_calls_successful
    - mind_mcp_calls_failed
    - mind_mcp_calls_timeout
    - graph_mcp_calls_total
    - graph_mcp_calls_successful
    - graph_mcp_calls_failed
    - graph_mcp_calls_timeout
    - total_cache_hits
    - total_cache_misses

  efficiency_metrics:
    - total_analysis_time
    - mcp_query_time
    - filesystem_scan_time
    - skill_chain_time
    - reconciliation_time
```

### Logging

```yaml
logging:
  log_level: "INFO"  # DEBUG for development, INFO for production
  log_format: "structured_json"  # For parsing and analysis

  log_all_phases:
    - phase_start: timestamp, phase_number, phase_name
    - phase_complete: timestamp, phase_number, results_summary
    - phase_error: timestamp, phase_number, error_details

  log_mcp_calls:
    - function_name: "hybrid_search|explore_graph|etc"
    - params: "sanitized_params"
    - duration_ms: "call_duration"
    - success: true/false
    - cache_hit: true/false
    - result_count: "number_of_results"

  log_cache_operations:
    - cache_operation: "read|write|hit|miss"
    - cache_file: "knowledge_cache|graph_cache"
    - cache_key: "query_hash"
    - result_count: "cached_items"

  log_redactions:
    - redaction_type: "API_KEY|PASSWORD|TOKEN|etc"
    - count: "number_of_redactions"
    - source: "config_file|code_file|documentation"
```

### Health Monitoring

```yaml
health_checks:
  mcp_health:
    endpoint: "/health/mcp"
    check_interval: 60s
    alert_on:
      - mind_mcp_unavailable: "mind_mcp down for >30s"
      - graph_mcp_unavailable: "graph_mcp down for >30s"
      - mcp_degraded: "MCP response time >10s for >5min"
      - mcp_error_rate: "MCP error rate >10% for >5min"

  workflow_health:
    endpoint: "/health/workflow"
    check_interval: 300s
    alert_on:
      - timeout_rate: "Workflow timeout rate >5% for >10min"
      - failure_rate: "Workflow failure rate >10% for >10min"
      - degraded_mode: "Running in degraded mode for >15min"

  output_quality:
    endpoint: "/health/quality"
    check_interval: 600s
    alert_on:
      - low_mcp_coverage: "MCP-sourced claims <50% for >20min"
      - high_conflict_rate: "Conflict rate >20% for >20min"
      - cache_efficiency: "Cache hit rate <60% for >20min"
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
- ✅ Enhanced fallback strategy with degraded mode
- ✅ Added conflict resolution rules for mind_mcp vs graph_mcp vs filesystem
- ✅ Added specific MCP function names with parameters and outputs
- ✅ Added observability metrics and health monitoring
- ✅ Added version history and changelog

**Improvements:**
- Enhanced MCP integration with specific function names
- Added preflight checks for MCP capability validation
- Enhanced error handling with specific recovery strategies per phase
- Added progress reporting after each phase
- Added conflict resolution rules with priority-based arbitration
- Added health monitoring and alerting

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on MCP down)
- Fixed: No conflict resolution (contradictory evidence unresolved)
- Fixed: No progress feedback (poor UX for long operations)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update health monitoring integration if using custom endpoints

### Version 1.0.0 (Initial Release)

- Initial orchestration workflow for deep discovery
- Basic MCP integration (mind_mcp, graph_mcp)
- Evidence caching and sharing across skills
- Basic output templates

## Known Limitations

### Current Limitations

```yaml
limitations:
  mcp_dependent:
    - "Requires both mind_mcp and graph_mcp for full functionality"
    - "Degraded mode has significantly reduced accuracy and confidence"
    - "Historical context unavailable if mind_mcp is down"

  performance:
    - "Very large repositories (>500k files) may exceed timeouts"
    - "Deep call graphs (>10 levels) hit traversal limits"
    - "Complex multi-module systems may exceed max_results limits"
    - "Skill chain execution time increases linearly with repo size"

  analysis_scope:
    - "Only analyzes code in specified repository"
    - "Cannot analyze external dependencies without source code"
    - "Cannot analyze runtime behavior without execution traces"
    - "Limited to static analysis (no dynamic execution)"

  language_support:
    - "Best support for: Python, JavaScript, TypeScript, Java, C#"
    - "Partial support for: C, C++, Go, Rust"
    - "Limited support for: Dynamic languages without type info"
    - "Limited support for: Microservices and distributed systems"

  skill_chain:
    - "Requires companion skills (repo-recon, tech-build-audit, module-summary-report)"
    - "If companion skills fail, synthesis may be incomplete"
    - "Skill chain execution time can be long for large repos"
```

### TODO / Future Enhancements

```yaml
todo:
  short_term:
    - "Add parallel skill execution (repo-recon + tech-build-audit)"
    - "Add incremental discovery (discover modules on-demand)"
    - "Add visual dependency graph rendering"

  medium_term:
    - "Add integration with IDEs (VS Code, JetBrains)"
    - "Add collaborative review and commenting"
    - "Add integration with documentation generators"

  long_term:
    - "Add automated architecture decision extraction"
    - "Add automated risk assessment with ML"
    - "Add cross-repository dependency analysis"
```

## Output Contract

### Standard Outputs

```yaml
discovery_summary.md:
  format: "Markdown"
  sections:
    - executive_findings: "3-5 lines summary"
    - module_inventory: "Complete module list with purposes"
    - technology_build_platform_matrix: "Stack/build/platform analysis"
    - critical_call_flows: "Key runtime flows with tracing"
    - top_risks_and_actions: "Prioritized risks with mitigation"
    - api_dependency_warnings: "API boundary violations"
    - unknowns_and_next_probes: "Unresolved issues"

discovery_bundle.json:
  format: "JSON"
  content:
    - metadata: "Project, timestamp, MCP sources"
    - evidence_provenance: "Claims, sources, confidence"
    - artifacts: "Output file references"
    - mcp_caches: "Cache file references"
    - efficiency_metrics: "Cache hit rate, query counts"

mcp_knowledge_cache.json:
  format: "JSON"
  content:
    - timestamp: "Cache creation time"
    - project_id: "Project identifier"
    - collections: "Source collections"
    - evidence_items: "Cached knowledge items"

mcp_graph_cache.json:
  format: "JSON"
  content:
    - timestamp: "Cache creation time"
    - project_id: "Project identifier"
    - database: "Graph database"
    - parser: "Graph parser"
    - evidence_items: "Cached graph items"
```

### Optional Outputs

```yaml
repo_recon.json:
  format: "JSON"
  content: "Module inventory and entry points"

repo_recon.md:
  format: "Markdown"
  content: "Human-readable repo structure"

tech_build_audit.json:
  format: "JSON"
  content: "Stack/build/platform analysis"

tech_build_audit.md:
  format: "Markdown"
  content: "Human-readable build analysis"

summary.md:
  format: "Markdown"
  content: "Comprehensive synthesis with evidence tags"
```

## Resources

- `references/mcp-orchestration-playbook.md`: End-to-end MCP query plan with evidence caching and context control
- `references/discovery-bundle-template.md`: Standard output structure
- `scripts/run_discovery_pipeline.py`: Optional local helper that runs `repo-recon` + `tech-build-audit` companion scripts and writes a stage manifest
- Uses companion skills:
  - `../repo-recon`
  - `../tech-build-audit`
  - `../module-summary-report`

## Support & Troubleshooting

### Common Issues

**Issue**: "MCP timeout during knowledge sweep"
- **Cause**: Large collection or slow query
- **Solution**: Reduce query limits, use specific queries
- **Workaround**: Use cached results from previous run

**Issue**: "Graph activation fails"
- **Cause**: Invalid project ID or database not found
- **Solution**: Verify project ID, check available databases
- **Workaround**: Run in degraded mode (filesystem-only)

**Issue**: "Skill chain fails at repo-recon"
- **Cause**: repo-recon skill not available or failed
- **Solution**: Verify repo-recon installation, check error logs
- **Workaround**: Continue with tech-build-audit and module-summary-report

**Issue**: "Cache miss rate >80%"
- **Cause**: Cache not being reused, queries not matching cache
- **Solution**: Check cache keys, verify cache is being shared across skills
- **Workaround**: Accept lower efficiency, optimize query patterns

**Issue**: "Evidence reconciliation finds too many conflicts"
- **Cause**: Outdated documentation or recent code changes
- **Solution**: Apply conflict resolution rules, prioritize appropriately
- **Workaround**: Mark conflicts as unresolved, create follow-up actions

### Getting Help

- Check evidence trace: `discovery_bundle.json` for detailed evidence provenance
- Review metrics in observability section for performance issues
- Consult MCP documentation for function-specific issues
- Check companion skill documentation for skill chain issues
- Open issue with: SKILL.md version, MCP runtime version, evidence bundle attached
