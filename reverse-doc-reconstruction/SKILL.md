---
name: reverse-doc-reconstruction
description: Reconstruct technical documentation from source code by tracing entry points, call flows, IPC links, and domain entities, then produce requirements/use case/detail design artifacts aligned with the project templates. Use when reverse engineering legacy repositories, rebuilding missing specs, or preparing migration-ready docs from implementation-first systems.
version: 2.0.0
last_updated: 2025-04-16
---

# Reverse Doc Reconstruction

Build documentation from code evidence first, then map evidence into template-driven artifacts with comprehensive security hardening, operational resilience, and evidence-based decision making.

## When To Use

- Legacy or implementation-first system lacks reliable requirements/design docs
- You need traceable use case and detail design artifacts generated from source evidence
- You are preparing migration, handover, or compliance documentation
- Requirements or design documents are outdated or missing
- Audit or compliance requires traceable documentation from code to artifacts

## Avoid Using When

- Existing documentation is already complete and only needs minor edits
- The request is limited to code structure mapping (use repo-recon)
- You only need a short executive summary (use module-summary-report)
- Quick informal documentation without formal requirements

## Required Inputs

- Repository root path
- Output root path for generated documents
- Module or business scope to analyze
- Preferred depth: `quick` or `deep`
- Optional owner and target date for document metadata

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
  - repository_path must be a git repository (optional, for Git-specific features)
  - repository_path must be readable: os.access(repo_path, os.R_OK)
  - Block path traversal: reject if contains "../" or absolute path
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max length: 10000 characters

output_path_validation:
  - output_path must be creatable: os.access(parent_dir, os.W_OK)
  - output_path must be within allowed directories
  - Block path traversal: reject if contains "../" or absolute path
  - Max length: 10000 characters
```

### Module/Scope Validation

- **Module scope**: Must be valid alphanumeric identifier
- **Business scope**: Must match available modules in repository
- **Depth preference**: Must be one of `quick` or `deep`

**Validation rules**:
```yaml
module_scope_validation:
  allowed_characters: /^[a-zA-Z0-9_-]+$/
  max_length: 100 characters
  check_module_exists: verify module exists in repository (optional)

depth_validation:
  allowed_values: ["quick", "deep"]
  default: "quick"
  quick_scope: "High-level flows and main UCs only"
  deep_scope: "All flows including alt/error paths and edge cases"
```

### Sensitive Data Redaction

When reconstructing documentation from code that may contain sensitive information:

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

# Personal Data
Email addresses:    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED_EMAIL]'
Phone numbers:      /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g → '[REDACTED_PHONE]'
```

**Documentation redaction**:
```yaml
logging_redaction:
  - Log all redactions in trace evidence: "Redacted 3 API keys from source code"
  - Never log original sensitive data
  - Store only redacted evidence in generated documents
  - Apply redaction before writing to output files
```

### Access Boundaries

- **Repository scope**: Limit analysis to specified repository path
- **Module scoping**: Respect module parameter
- **Output access**: Verify write access to output directory
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
  bootstrap_timeout: 60s             # Script bootstrap_reverse_doc_workspace.py
  business_context_timeout: 180s     # mind_mcp context discovery
  call_graph_tracing_timeout: 300s   # graph_mcp flow tracing
  uc_consolidation_timeout: 120s     # Use case consolidation
  doc_generation_timeout: 180s       # Document generation

  # Phase timeouts
  phase_0_preflight_timeout: 30s      # Preflight and context setup
  phase_1_business_context_timeout: 180s # mind_mcp context discovery
  phase_2_entry_map_timeout: 240s    # graph_mcp entry point discovery
  phase_3_call_flows_timeout: 360s    # graph_mcp call flow tracing
  phase_4_uc_consolidation_timeout: 180s # Use case consolidation
  phase_5_uc_artifacts_timeout: 300s  # UC artifact generation
  phase_6_design_artifacts_timeout: 600s # Detail design artifact generation
  phase_7_quality_gates_timeout: 120s # Review and quality gates

  # Total workflow timeout
  total_workflow_timeout: 1800s     # Entire reconstruction (30 minutes)
```

### Resource Limits

```yaml
resource_limits:
  # Repository size limits
  max_repository_size: 1GB           # Prevent memory issues
  max_files_to_analyze: 5000         # Limit for large repos
  max_file_size: 10MB                # Skip files larger than 10MB

  # Analysis limits
  max_entry_points: 200              # Limit for entry point discovery
  max_functions_to_trace: 1000       # Limit for call graph tracing
  max_uc_to_generate: 50             # Limit for use case generation
  max_design_artifacts: 100          # Limit for design artifacts

  # Output limits
  max_document_size: 5MB             # Single document max size
  max_total_output_size: 500MB       # Total output max size
```

### Progress Feedback

```yaml
progress_reporting:
  # Phase-level progress
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"
    - "  Module: {module_name}"
    - "  Depth: {depth_preference}"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Results: {results_summary}"
    - "  Evidence items: {evidence_count}"

  phase_error:
    - "Phase {N} error: {phase_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  # Task-level progress (for long operations)
  task_progress:
    - "Discovering business context: {terms_count} terms found"
    - "Tracing entry points: {current}/{total} entry points"
    - "Consolidating use cases: {current}/{total} UCs"
    - "Generating design artifacts: {current}/{total} artifacts"

  # UC-level progress
  uc_progress:
    - "Use Case {uc_id}: {uc_name}"
    - "  Entry points: {entry_count}"
    - "  Flow steps: {flow_steps}"
    - "  Status: {status}"

  # Final summary
  final_summary:
    - "Documentation reconstruction complete"
    - "Total duration: {total_duration}s"
    - "Use cases discovered: {uc_count}"
    - "Design artifacts generated: {artifact_count}"
    - "Evidence coverage: {mcp_coverage}%"
    - "Output: {output_files}"
```

### Caching Strategy

```yaml
cache:
  # mind_mcp business context cache
  business_context_cache:
    enabled: true
    ttl: 900                          # 15 minutes
    file: "mcp_business_context_cache.json"
    cache_content:
      - business_vocabulary
      - domain_terms
      - business_rules
      - constraints
    invalidation: "on_workflow_start"

  # graph_mcp tracing cache
  tracing_cache:
    enabled: true
    ttl: 1200                         # 20 minutes
    file: "mcp_tracing_cache.json"
    cache_content:
      - entry_points
      - call_graph_structure
      - flow_traces
      - ipc_links
    invalidation: "on_repo_change"

  # Use case cache
  use_case_cache:
    enabled: true
    ttl: 1800                         # 30 minutes
    file: "use_case_cache.json"
    cache_content:
      - discovered_use_cases
      - uc_evidence_mapping
      - uc_taxonomy_tags
    invalidation: "on_uc_approval"

  # Shared evidence cache
  shared_cache:
    enabled: true
    ttl: 2400                         # 40 minutes
    file: "shared_reconstruction_cache.json"
    cache_content:
      - all_mcp_evidence
      - use_cases
      - design_artifacts
    invalidation: "on_workflow_end"

  # Cache hit tracking
  cache_metrics:
    track_cache_hits: true
    track_cache_misses: true
    report_in_summary: true
```

## Error Handling & Fallback Strategy

### Preflight Checks

Before starting reconstruction:

```yaml
preflight:
  - check: "repository_validation"
    verify:
      - repository_path_exists
      - repository_is_readable
      - repository_is_valid_git_repo
      - repository_within_size_limit
    action_on_failure: "abort_with_error"

  - check: "output_path_validation"
    verify:
      - output_path_CREATABLE
      - output_path_within_allowed_directories
      - sufficient_disk_space (estimated output size * 2)
    action_on_failure: "abort_with_error"

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
      - trace_flow
    action_on_failure: "fallback_to_filesystem_only"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  filesystem_only_mode:
    mode: "filesystem_analysis_with_manual_verification"

    steps:
      1. Skip MCP queries entirely
      2. Use filesystem tools (rg, grep, find) for code structure discovery
      3. Use manual code reading for domain knowledge extraction
      4. Build conservative use cases with explicit unknowns
      5. Mark all evidence as low confidence
      6. Set unresolved links: HANDLED=MANUAL
      7. Add disclaimer to all generated documents

    logging:
      - "Running in FILESYSTEM-ONLY MODE: MCP unavailable"
      - "Analysis limited to filesystem tools only"
      - "Evidence confidence: LOW for all items"
      - "Manual verification required for completeness"

    notification:
      - "⚠️ MCP services unavailable or degraded"
      - "Running in filesystem-only mode with reduced confidence"
      - "Documentation will have gaps requiring manual verification"
      - "Do not use for compliance or critical documentation without review"

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
    on_output_path_invalid:
      action: "abort_with_error"
      log: "Output path validation failed, aborting"

  phase_1_business_context:
    on_mcp_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty context"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial business context retrieved, continuing with available data"

  phase_2_entry_map:
    on_mcp_timeout:
      action: "fallback_to_filesystem"
      log: "graph_mcp timeout, using rg/grep for entry point discovery"
      continue: true

  phase_3_call_flows:
    on_mcp_timeout:
      action: "trace_main_flows_only"
      log: "graph_mcp timeout, tracing main flows only, skipping alt/error"
      continue: true

  phase_4_uc_consolidation:
    on_evidence_conflict:
      action: "apply_conflict_resolution_rules"
      log: "Evidence conflict detected, applying resolution rules"
    on_incomplete_evidence:
      action: "mark_unresolved"
      log: "Incomplete evidence, marking unresolved with HANDLED=MANUAL"

  phase_5_uc_artifacts:
    on_diagram_generation_failure:
      action: "create_text_diagrams"
      log: "Diagram generation failed, creating text-based diagrams"
      continue: true

  phase_6_design_artifacts:
    on_mapping_failure:
      action: "document_mapping_gaps"
      log: "UC to design mapping failed, documenting gaps"
      continue: true

  phase_7_quality_gates:
    on_coverage_threshold_not_met:
      action: "report_gaps_and_continue"
      log: "Coverage threshold not met, reporting gaps"
      add_warning: true
      continue: true
```

## Conflict Resolution Rules

When evidence sources conflict during documentation decisions:

```yaml
conflict_resolution:
  priority_rules:
    1. "For current code structure and behavior: Trust graph_mcp over mind_mcp"
       - Example: Function exists in graph but not in docs → Use graph
      - Example: API signature in graph vs docs → Use graph

    2. "For business intent and domain concepts: Trust mind_mcp over graph_mcp"
       - Example: Business logic interpretation → Use docs
      - Example: Domain entity relationships → Use docs

    3. "For recent changes: Trust filesystem (actual files) over MCP"
       - Example: Recent commits not yet in MCP → Use filesystem
      - Example: Local modifications → Use filesystem

    4. "For historical context and architecture: Trust mind_mcp (archival knowledge)"
       - Example: Why this was implemented → Use docs/ADRs
      - Example: Original design decisions → Use docs

    5. "For call graph structure: Trust graph_mcp (current code truth)"
       - Example: Function calls and dependencies → Use graph
      - Example: Module boundaries → Use graph

  documentation_conflicts:
    when: "code behavior differs from documentation"
    rules:
      - "If code behavior differs from documented intent: Document both, flag as inconsistency"
      - "If documentation unclear: Use code analysis as primary, document ambiguity"
      - "If both unclear: Mark as unknown, require manual investigation"

  tiebreaker:
    when: "both sources have equal confidence but disagree"
    action: "report_both_with_disclaimer"
    format: |
      CONFLICT DETECTED:
      - mind_mcp says: {mind_mcp_claim} (confidence: {confidence})
      - graph_mcp says: {graph_mcp_claim} (confidence: {confidence})
      - Documentation decision: Document both with conflict note
      Recommendation: Manual verification required

  logging:
    log_all_conflicts: true
    include_in_docs: true
    severity_levels: ["RESOLVED_BY_PRIORITY", "MANUAL_VERIFICATION_NEEDED", "DOCUMENTED_INCONSISTENCY"]
```

## Workflow

### Phase 0: Preflight MCP Context Setup (30s)

```yaml
steps:
  1. Validate all inputs (repo path, output path, module scope, depth)
  2. Check MCP capabilities via preflight checks
  3. Verify repository and output access
  4. Initialize shared context map
  5. Configure timeouts, limits, and caching
  6. Report: "Preflight complete, starting documentation reconstruction"

shared_context:
  repository_path: "{repo_path}"
  output_root: "{output_path}"
  module_name: "{module_name}"
  business_scope: "{business_scope}"
  depth_preference: "{quick|deep}"
  owner: "{owner_name}"
  target_date: "{target_date}"

mcp_functions:
  - list_qdrant_collections [required]
  - list_source_ids [optional]
  - list_mcp_functions [required]
  - list_parsers [required]
  - list_databases [required]
  - activate_project [required]

on_failure: "abort or fallback to filesystem-only mode"
```

### Phase 1: Discover Business Context from mind_mcp (Cached, 3min)

```yaml
steps:
  1. Query for business vocabulary and domain terms
  2. Extract domain entities and their relationships
  3. Capture business rules and constraints
  4. Store as evidence with citations
  5. Cache results to mcp_business_context_cache.json
  6. Report progress: "Phase 1 complete: {count} business context items cached"

mcp_functions:
  - hybrid_search [required]
    params:
      query: "{business_term_query}"
      collection: "{selected_collection}"
      limit: 20
    output:
      - results: list of relevant documents
      - scores: relevance scores
      expected: "Business vocabulary and domain terms"

  - sequential_search [optional]
    params:
      query: "{process_flow_query}"
      collection: "{selected_collection}"
      limit: 10
    output:
      - results: ordered procedure documents
      expected: "Step-by-step process flows"

  - get_paragraph_text [required]
    params:
      paragraph_ids: ["{ids_from_hybrid_search}"]
    output:
      - text: actual paragraph content
      - citations: source references
      expected: "Detailed content with citations"

  - query_graph_rag_relation [optional]
    params:
      entity: "{domain_entity}"
      relation_types: ["relates_to", "depends_on", "contains"]
    output:
      - relations: entity relationships
      expected: "Domain entity relationships"

cache_output:
  file: "mcp_business_context_cache.json"
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
        content: summarized content

fallback:
  on_mcp_unavailable: "Skip business context discovery, set context_cache = {}"
  on_timeout: "Return partial results, cache partial context"
```

### Phase 2: Bootstrap output package (1min)

```yaml
steps:
  1. Run bootstrap script to create folder structure
  2. Copy template files to output directory
  3. Initialize metadata files
  4. Report progress: "Phase 2 complete: Output package bootstrapped"

bootstrap_script:
  script: "scripts/bootstrap_reverse_doc_workspace.py"
  params:
    target_root: "{repository_path}"
    module: "{module_name}"
    owner: "{owner_name}"
  expected_output:
    folder_structure:
      - "00_requirements/"
      - "01_usecase/"
      - "02_detail_design/"
      - "03_trace_evidence/"
    template_files:
      # All templates copied from /template/ directory at agent-skill root
      - "00_requirements/tpl_requirements_spec.md"
      - "00_requirements/tpl_feature_list.md"
      - "01_usecase/tpl_usecase_list.md"
      - "01_usecase/tpl_usecase_metrics.md"
      - "01_usecase/tpl_usecase_detail.md"  # Renamed to ucXXX_{module}_template.md
      - "02_detail_design/tpl_screen_design.md"
      - "02_detail_design/tpl_api_process_design.md"
      - "02_detail_design/tpl_openapi_spec.yaml"
      - "02_detail_design/tpl_table_design.md"
      - "02_detail_design/tpl_sql_design.md"
      - "02_detail_design/tpl_batch_process_design.md"
```

### Phase 3: Discover Business Context from mind_mcp (Cached, 3min)

[See Phase 1 above - cached results used]

### Phase 4: Build coverage baseline and entry map (4min)

```yaml
steps:
  1. Use graph_mcp to discover entry points and structure
  2. Capture baseline metrics
  3. Document unknown or low-confidence areas
  4. Cache results to mcp_tracing_cache.json
  5. Report progress: "Phase 4 complete: {entry_count} entry points discovered"

mcp_functions:
  - list_up_entrypoint [required]
    params:
      file_pattern: "{module_pattern}/*.cpp"  # or *.py, *.java, etc.
      limit: 200
    output:
      - entry_points: API endpoints, main functions
      expected: "Entry point discovery"

  - explore_graph [required]
    params:
      query: "{module_or_function}"
      limit: 100
    output:
      - nodes: discovered nodes
      - edges: connections
      expected: "Module/function enumeration"

  - search_functions [required]
    params:
      query: "{entry_point_pattern}"
      limit: 50
    output:
      - functions: matching functions
      expected: "Entry point discovery"

baseline_metrics:
  total_functions: "{count from explore_graph}"
  total_entry_points: "{count from list_up_entrypoint}"
  ipc_partners: "{discovered from graph edges}"
  files_in_scope: "{count from filesystem scan}"

cache_output:
  file: "mcp_tracing_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    parser: "{parser}"
    evidence_items:
      - id: node_id
        type: entrypoint | function | module | ipc_link
        source: graph_mcp
        metadata: {name, file, signature}
        confidence: high | medium | low

fallback:
  on_mcp_unavailable: "Use rg --files for module inventory"
  on_timeout: "Return partial results, document coverage gap"
```

### Phase 5: Trace call flows with graph_mcp (6min)

```yaml
steps:
  1. Trace main flows from each entry point
  2. Discover alternate and error branches
  3. Verify indirect calls and IPC
  4. Apply context-control strategy for large codebases
  5. Cache results
  6. Report progress: "Phase 5 complete: {flows_count} flows traced"

mcp_functions:
  - trace_flow [required]
    params:
      start_node: "{entry_point_id}"
      max_depth: 5
    output:
      - flow: execution path
      expected: "Happy path tracing"

  - find_paths [required]
    params:
      start_node: "{entry_point_id}"
      end_node: "{domain_node_id}"
      max_paths: 10
    output:
      - paths: paths between nodes
      expected: "Path discovery"

  - query_subgraph [required]
    params:
      node_id: "{domain_entity_id}"
      depth: 3
      limit: 50
    output:
      - subgraph: nodes and edges
      expected: "Domain entity context"

  - search_functions [required]
    params:
      query: "error OR timeout OR retry OR abort"
      limit: 50
    output:
      - functions: error handling functions
      expected: "Error branch discovery"

  - list_possible_calls [optional]
    params:
      node_id: "{function_id}"
    output:
      - possible_calls: dynamic dispatch targets
      expected: "Indirect call resolution"

context_control:
  query_by_module: "Use module-specific terms, not entire project"
  limit_results: "Limit to 20-50 items per query"
  batch_processing: "Batch node_details in groups of 10-20"

fallback:
  on_mcp_unavailable: "Use rg for pattern search, skip flow tracing"
  on_timeout: "Trace main flows only, skip alt/error paths"
```

### Phase 6: Discover and consolidate use cases (3min)

```yaml
steps:
  1. Align business terms (mind_mcp) with code flows (graph_mcp)
  2. Verify each UC has business purpose + code entry point + flow evidence
  3. Group flows into UC units
  4. Update usecase_list and usecase_metrics
  5. Tag each UC with evidence provenance
  6. Report progress: "Phase 6 complete: {uc_count} use cases consolidated"

uc_verification:
  business_purpose: "From mind_mcp business context"
  code_entry_point: "From graph_mcp entry point discovery"
  flow_evidence: "From graph_mcp trace results"
  taxonomy_tags:
    - ROLE: ENTRYPOINT, CONTROLLER, SERVICE, REPOSITORY
    - FLOW: MAIN, ALT, ERROR, TIMEOUT, RETRY
    - RISK: HIGH, MEDIUM, LOW
    - STATE: MUTATES, PURE, I/O, CACHE

uc_output_files:
  - usecase_list_{module}.md
  - usecase_metrics_{module}.md
  - uc001_{module}.md (duplicate per discovered UC)
```

### Phase 7: Produce UC detail artifacts with diagrams (5min)

```yaml
steps:
  1. For each UC, fill UC template with evidence
  2. Generate sequence and class diagrams (Mermaid)
  3. Add tags and evidence links
  4. Report progress: "Phase 7 complete: {uc_count} UC artifacts generated"

uc_artifact_content:
  from_mind_mcp:
    - actors: "User roles and external systems"
    - preconditions: "Business rules and constraints"
    - postconditions: "Expected outcomes"

  from_graph_mcp:
    - main_flow: "Happy path from trace_flow"
    - alt_flows: "Alternate paths from find_paths"
    - error_flows: "Error handling from search_functions"

  diagrams:
    - sequence_diagram: "Mermaid diagram with graph_mcp node_ids"
    - class_diagram: "Mermaid diagram with class relationships"
    - activity_diagram: "Activity diagram with flow steps"

  evidence_links:
    - mind_mcp_refs: "Paragraph IDs from business context"
    - graph_mcp_refs: "Node IDs from flow tracing"
    - confidence_levels: "High/Medium/Low per claim"
```

### Phase 8: Derive detail design artifacts from validated UCs (10min)

```yaml
steps:
  1. Convert validated UCs to design artifacts
  2. Use mapping rules from usecase-to-detail-design-map.md
  3. Generate all design artifacts:
     - screen design
     - API process design + OpenAPI spec
     - table design + SQL design
     - batch process design (if batch flows exist)
  4. Apply consistency checks
  5. Report progress: "Phase 8 complete: {artifact_count} design artifacts generated"

mapping_rules:
  from usecase_to_detail_design:
    actors + entry_points: "screen_design"
    main_flow_steps: "api_process_design"
    alt_error_flows: "api_process_design (error handling)"
    critical_checkpoints: "api_process_design (auth, validation)"
    domain_entities + data_fields: "table_design"
    query_and_state_transitions: "sql_design"
    api_request_response_shape: "openapi_spec"
    batch_oriented_branches: "batch_process_design"

consistency_checks:
  - every_api_field_exists_in_uc: "No invented APIs"
  - every_sql_filter_maps_to_input: "No invented queries"
  - every_checkpoint_appears_in_design: "No missing security"
  - every_diagram_participant_maps_to_component: "Traceable actors"

output_files:
  - screen_design_{module}.md
  - api_process_design_{module}.md
  - openapi_spec_{module}.yaml
  - table_design_{module}.md
  - sql_design_{module}.md
  - batch_process_design_{module}.md (if applicable)
```

### Phase 9: Run review and quality gates (2min)

```yaml
steps:
  1. Evaluate coverage and risk thresholds
  2. Check alignment between UCs, diagrams, and design docs
  3. Mark unresolved gaps with follow-up actions
  4. Generate final quality report
  5. Report progress: "Phase 9 complete: Quality gates evaluated"

quality_metrics:
  coverage_metrics:
    uc_coverage: "documented_uc / discovered_uc"
    entry_coverage: "traced_entries / total_entries"
    function_coverage: "traced_functions / total_functions"
    error_path_coverage: "documented_error_paths / expected_error_paths"
    ipc_coverage: "documented_ipc_links / discovered_ipc_links"
    mcp_evidence_pct: "claims_with_mcp_source / total_claims"

  risk_assessment:
    high_risk_ucs: "UCs touching auth, payment, critical state"
    incomplete_traces: "Flows with unresolved edges"
    confidence_gaps: "Areas with low evidence coverage"
    manual_verification_required: "Items marked HANDLED=MANUAL"

quality_gates:
  minimum_mcp_evidence_pct: 60
  minimum_uc_coverage: 80
  minimum_entry_coverage: 90
  critical_flows_must_have_trace: true

output_file:
  format: "Markdown"
  output: "quality_report_{module}.md"
```

## Output Contract

### Document Package Structure

```yaml
output_location: "<target>/.github/reverse_reconstruction/<module>/"

mandatory_outputs:
  requirements:
    - "00_requirements/requirements_spec_{module}.md"
    - "00_requirements/feature_list_{module}.md"

  usecases:
    - "01_usecase/usecase_list_{module}.md"
    - "01_usecase/usecase_metrics_{module}.md"
    - "01_usecase/uc001_{module}.md"  # Duplicate per UC

  detail_design:
    - "02_detail_design/screen_design_{module}.md"
    - "02_detail_design/api_process_design_{module}.md"
    - "02_detail_design/openapi_spec_{module}.yaml"
    - "02_detail_design/table_design_{module}.md"
    - "02_detail_design/sql_design_{module}.md"
    - "02_detail_design/batch_process_design_{module}.md"  # If applicable

  trace_evidence:
    - "03_trace_evidence/trace_plan_{module}.md"
```

## Non-Negotiable Rules

- ✅ Never invent functions, IPC messages, or database objects without evidence
- ✅ Never create APIs that are not backed by UC flows
- ✅ Never introduce tables without traceable entity evidence
- ✅ Always validate inputs before analysis (security)
- ✅ Always redact sensitive data before writing to output (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always cache MCP evidence to improve efficiency (performance)
- ✅ Always include evidence source tags in every claim (traceability)

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  reconstruction_progress:
    - total_phases: "Total workflow phases"
    - completed_phases: "Completed phases"
    - current_phase: "Current phase in progress"

  documentation_coverage:
    - total_use_cases: "Total use cases discovered"
    - documented_use_cases: "Use cases with artifacts"
    - total_design_artifacts: "Design artifacts generated"
    - generated_artifacts: "Artifacts created"

  evidence_quality:
    - total_claims: "Total documentation claims"
    - mcp_sourced_claims: "Claims with MCP evidence"
    - mind_mcp_sourced_claims: "Claims from mind_mcp"
    - graph_mcp_sourced_claims: "Claims from graph_mcp"
    - filesystem_sourced_claims: "Claims from filesystem"
    - mcp_evidence_percentage: "MCP coverage percentage"

  trace_coverage:
    - uc_coverage: "Documented UCs / Discovered UCs"
    - entry_coverage: "Traced entries / Total entries"
    - function_coverage: "Traced functions / Total functions"
    - error_path_coverage: "Documented error paths / Expected error paths"
    - ipc_coverage: "Documented IPC links / Discovered IPC links"

  mcp_performance:
    - mind_mcp_calls_total: "Total mind_mcp calls"
    - mind_mcp_calls_successful: "Successful mind_mcp calls"
    - mind_mcp_calls_failed: "Failed mind_mcp calls"
    - graph_mcp_calls_total: "Total graph_mcp calls"
    - graph_mcp_calls_successful: "Successful graph_mcp calls"
    - graph_mcp_calls_failed: "Failed graph_mcp calls"
    - cache_hit_rate: "Percentage of cache hits"
```

## Version History & Changelog

### Version 2.0.0 (2025-04-16)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration (was unlimited, now 30min max)
- Enhanced fallback strategy (was implicit, now explicit with rules)

**New Features:**
- ✅ Added Security & Privacy section with validation and redaction
- ✅ Added Performance & UX section with timeouts, progress feedback, caching
- ✅ Enhanced fallback strategy with filesystem-only mode
- ✅ Added conflict resolution rules for evidence sources
- ✅ Added specific MCP function names with parameters and outputs
- ✅ Added observability metrics and health monitoring
- ✅ Added version history and changelog

**Improvements:**
- Enhanced MCP integration with specific function names
- Added preflight checks for MCP and path validation
- Enhanced error handling with specific recovery strategies per phase
- Added progress reporting after each phase
- Added conflict resolution rules with conservative documentation
- Added health monitoring and alerting

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on MCP down)
- Fixed: No conflict resolution (evidence contradictions unresolved)
- Fixed: No progress feedback (poor UX for long documentation processes)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update bootstrap script if using custom output structure

### Version 1.0.0 (Initial Release)

- Initial workflow for documentation reconstruction from code
- Basic MCP integration (mind_mcp, graph_mcp)
- Evidence-based use case discovery
- Template-driven artifact generation
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
    - "Deep call graphs (>10 levels) hit traversal limits"
    - "Complex multi-module systems may exceed max_results limits"

  analysis_scope:
    - "Only analyzes specified repository and module"
    - "Cannot analyze external dependencies without source code"
    - "Cannot capture runtime behavior without execution traces"

  documentation_quality:
    - "Cannot capture informal knowledge not in code or docs"
    - "May miss edge cases not covered by existing tests"
    - "Requires manual verification for completeness"

  language_support:
    - "Best support for: Python, Java, C#, JavaScript, TypeScript"
    - "Partial support for: C, C++, Go, Rust"
    - "Limited support for: Dynamic languages without type info"
```

## Deliverables

- Requirements specification (with feature list)
- Use case artifacts (list, metrics, individual UC files with diagrams)
- Detail design artifacts (screen, API, database, batch process)
- OpenAPI specifications (for REST APIs)
- Trace evidence documentation
- Quality gate report with coverage metrics

## References

### Standard Templates

All documentation templates are sourced from `/template/` directory at agent-skill root:

**Requirements (template/00_requirements/)**:
- `tpl_requirements_spec.md` - Requirements specification template
- `tpl_feature_list.md` - Feature list template

**Use Case (template/01_usecase/)**:
- `tpl_usecase_list.md` - Use case list template
- `tpl_usecase_metrics.md` - Use case metrics template
- `tpl_usecase_detail.md` - Individual use case template (used for UC001, UC002, etc.)

**Detail Design (template/02_detail_design/)**:
- `tpl_screen_design.md` - Screen design template
- `tpl_api_process_design.md` - API process design template
- `tpl_openapi_spec.yaml` - OpenAPI specification template
- `tpl_table_design.md` - Table design template
- `tpl_sql_design.md` - SQL design template
- `tpl_batch_process_design.md` - Batch process design template

### Skill-Specific References

- `scripts/bootstrap_reverse_doc_workspace.py`: Bootstrap workspace and copy templates from template/ directory
- `references/reverse-trace-playbook.md`: MCP-first tracing strategy
- `references/usecase-to-detail-design-map.md`: Deterministic mapping from UC to design
- `references/quality-gates.md`: Exit criteria and review checklist
- `references/source-material-index.md`: Canonical source files used
