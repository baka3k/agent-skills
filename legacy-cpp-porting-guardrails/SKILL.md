---
name: legacy-cpp-porting-guardrails
description: Port and modernize very large legacy C/C++ classes or functions while preserving behavior with explicit guardrails, slice-by-slice migration, and parity tests. Use when files are thousands of lines, functions are hundreds to thousands of lines, logic is stateful or side-effect-heavy, and existing tests are weak or missing.
version: 2.0.0
last_updated: 2025-04-16
---

# Legacy C++ Porting Guardrails

Port safely first, optimize later. Lock behavior before refactor.

Use this skill to avoid logic drift when porting very long legacy classes/functions with comprehensive security hardening, operational resilience, and evidence-based decision making.

## When To Use

- Porting or modernizing very large legacy C/C++ code (files >1000 lines, functions >100 lines)
- Existing tests are weak and parity needs explicit gates per migration slice
- Code has heavy side effects, status-code contracts, or unclear historical constraints
- High behavior risk requiring comprehensive analysis and verification
- Need auditable, reversible migration process for critical legacy systems

## Avoid Using When

- File/function is small enough for direct refactor with standard tests
- Goal is performance tuning only without behavior-preservation constraints
- You do not have any way to run parity checks (legacy or target side)
- Quick prototype or throwaway code without production requirements

## Required Inputs

- Source file(s) to port (C/C++ files with full path)
- Target language/runtime and coding constraints
- Build/test command for legacy code (if runnable)
- Build/test command for the target port (if available)

## Input Validation & Security

### Path Validation

- **Source files**: Must exist, be readable, and have valid C/C++ extensions
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **File sanitization**: Limit to 10000 characters, whitelist allowed characters
- **Access verification**: Verify read access before analysis

**Validation rules**:
```yaml
source_file_validation:
  - file_path must exist: os.path.exists(file_path)
  - file must be readable: os.access(file_path, os.R_OK)
  - file must have valid extension: [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"]
  - Block path traversal: reject if contains "../" or absolute path
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max path length: 10000 characters
  - Max file size: 10MB (prevent memory issues)
```

### Build/Test Command Validation

- **Command format**: Must be valid shell command or build system command
- **Command sanitization**: Remove dangerous operations (rm,rf, format, etc.)
- **Timeout specification**: Commands must have timeout limits
- **Output validation**: Command output paths must be within allowed directories

**Validation rules**:
```yaml
command_validation:
  allowed_commands:
    - build systems: [make, cmake, bazel, ninja, msbuild, xcodebuild]
    - test runners: [ctest, googletest, catch2, boost.test]
    - compilers: [gcc, g++, clang, cl, icc]
    - linkers: [ld, link, lld]

  blocked_patterns:
    - "rm -rf"  # Prevent destructive operations
    - "format"  # Prevent disk formatting
    - "del /"   # Prevent Windows deletion
    - "> /dev/" # Allow only with explicit permission

  timeout_requirements:
    - build_commands: max 30 minutes
    - test_commands: max 10 minutes
    - analysis_commands: max 5 minutes
```

### Target Language/Runtime Validation

- **Language support**: Must support C++ interoperability or have clear migration path
- **Runtime compatibility**: Must verify runtime version and dependencies
- **Library availability**: Must verify required libraries are accessible

**Validation rules**:
```yaml
target_language_validation:
  supported_languages:
    - Modern C++: C++11, C++14, C++17, C++20
    - Rust: with C++ FFI bindings
    - Go: with cgo and C++ bindings
    - Java: with JNI (for non-performance-critical code)
    - C#: with P/Invoke (for Windows platforms)

  runtime_validation:
    - Verify compiler version: g++ >= 7, clang >= 5, MSVC >= 2017
    - Verify standard library version: libstdc++ >= GLIBCXX_3.4.25
    - Verify dependency availability: pthread, libm, etc.
```

### Sensitive Data Redaction

When analyzing legacy code that may contain sensitive information:

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
SSN:                /\b\d{3}-\d{2}-\d{4}\b/g → '[REDACTED_SSN]'
```

**Logging redaction**:
```yaml
logging_redaction:
  - Log all redactions in analysis report: "Redacted 3 API keys from source file"
  - Never log original sensitive data
  - Store only redacted evidence in port plan and behavior contracts
  - Apply redaction before caching to MCP cache files
```

### Access Boundaries

- **Repository scope**: Limit analysis to specified source files and directories
- **Build system access**: Verify access to build tools and test infrastructure
- **Network restrictions**: No external network calls during analysis (except to MCP servers)
- **MCP access**: Only access collections/databases user is authorized to access

**Access control verification**:
```yaml
access_control:
  source_code_access:
    - Verify read access: os.access(file_path, os.R_OK)
    - Verify parent directory access: os.access(parent_dir, os.R_OK)
    - List directory contents: os.listdir(parent_dir)

  build_system_access:
    - Verify build tool availability: which make/cmake/etc.
    - Verify compiler availability: which gcc/clang/cl
    - Verify test runner availability: which ctest/etc.

  mcp_access:
    - mind_mcp: Verify collection access with list_qdrant_collections
    - graph_mcp: Verify database access and C++ parser availability
    - If unauthorized: Log warning and skip that source
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # MCP call timeouts
  mcp_call_timeout: 30s              # Per MCP function call
  query_timeout: 45s                  # Per complex query
  batch_timeout: 60s                  # Per batch processing operation

  # Analysis timeouts
  filesystem_analysis_timeout: 300s   # Script analyze_cpp_scope.py
  scope_analysis_timeout: 180s        # Graph analysis with graph_mcp
  behavior_contract_timeout: 120s     # Contract creation

  # Build/test timeouts
  legacy_build_timeout: 1800s         # 30 minutes max for legacy build
  legacy_test_timeout: 600s           # 10 minutes max for legacy tests
  target_build_timeout: 1800s         # 30 minutes max for target build
  target_test_timeout: 600s           # 10 minutes max for target tests

  # Phase timeouts
  phase_0_preflight_timeout: 30s      # Preflight and context setup
  phase_1_context_discovery_timeout: 180s # mind_mcp context discovery
  phase_2_scope_analysis_timeout: 300s   # graph_mcp + filesystem analysis
  phase_3_behavior_contract_timeout: 120s # Behavior contract creation
  phase_4_parity_harness_timeout: 180s    # Parity test creation
  phase_5_port_slice_timeout: 600s        # Per slice porting
  phase_6_verification_timeout: 180s      # Post-port verification

  # Timeout handling
  on_timeout:
    action: "return_partial_results"
    log: "Operation timeout reached, returning partial results"
    notify_user: "Analysis incomplete due to timeout. Results may be incomplete."
    continue_next_phase: true
```

### Resource Limits

```yaml
resource_limits:
  # File size limits
  max_source_file_size: 10MB         # Prevent memory issues
  max_total_analysis_size: 100MB     # Total source files to analyze

  # Analysis limits
  max_functions_per_file: 500        # Limit for large files
  max_classes_per_file: 100          # Limit for complex files
  max_depth_call_graph: 10           # Call graph traversal depth
  max_side_effects_per_function: 50  # Side effect tracing limit

  # Memory limits
  max_memory_per_analysis: 2GB       # Memory limit per analysis script
  max_cache_size: 100MB              # MCP evidence cache size
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
    - "  Functions analyzed: {function_count}"
    - "  Risk assessment: {high_risk_count} high-risk functions"

  phase_error:
    - "Phase {N} error: {phase_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  # Task-level progress (for long operations)
  task_progress:
    - "Analyzing function {current}/{total}: {function_name}"
    - "Building parity test cases: {current}/{total} cases"
    - "Porting slice {current}/{total}: {slice_name}"
    - "Running parity tests: {passed}/{total} passed"

  # Slice-level progress
  slice_progress:
    - "Slice {slice_id}: {functions_count} functions to port"
    - "  Estimated complexity: {complexity}"
    - "  Parity cases: {parity_case_count}"
    - "  Status: {status}"

  # Final summary
  final_summary:
    - "Porting analysis complete"
    - "Total duration: {total_duration}s"
    - "Functions ported: {ported_functions}/{total_functions}"
    - "Parity rate: {parity_rate}%"
    - "High-risk items: {high_risk_count}"
    - "Output: {output_files}"
```

### Caching Strategy

```yaml
cache:
  # mind_mcp context cache
  context_cache:
    enabled: true
    ttl: 900                          # 15 minutes
    file: "mcp_context_cache.json"
    cache_content:
      - historical_context
      - business_constraints
      - known_issues
      - technical_constraints
    invalidation: "on_workflow_start"

  # graph_mcp analysis cache
  analysis_cache:
    enabled: true
    ttl: 1200                         # 20 minutes
    file: "mcp_analysis_cache.json"
    cache_content:
      - call_graph_structure
      - side_effect_analysis
      - class_hierarchy
      - dependency_mapping
    invalidation: "on_source_change"

  # Filesystem analysis cache
  filesystem_cache:
    enabled: true
    ttl: 1800                         # 30 minutes
    file: "filesystem_analysis_cache.json"
    cache_content:
      - function_metrics
      - complexity_analysis
      - code_structure
    invalidation: "on_file_modification"

  # Shared evidence cache (for all phases)
  shared_cache:
    enabled: true
    ttl: 2400                         # 40 minutes
    file: "shared_porting_cache.json"
    cache_content:
      - all_mcp_evidence
      - behavior_contracts
      - port_plan
    invalidation: "on_workflow_end"

  # Cache hit tracking
  cache_metrics:
    track_cache_hits: true
    track_cache_misses: true
    report_in_summary: true
```

## Error Handling & Fallback Strategy

### Preflight Checks

Before starting porting analysis:

```yaml
preflight:
  - check: "source_file_validation"
    verify:
      - source_files_exist
      - source_files_readable
      - source_files_valid_cpp
      - source_files_within_size_limit
    action_on_failure: "abort_with_error"

  - check: "build_system_validation"
    verify:
      - legacy_build_command_available
      - target_build_command_available
      - compilers_accessible
      - test_runners_accessible
    action_on_failure: "continue_with_reduced_scope"

  - check: "mcp_capability_check"
    mind_mcp_functions:
      - list_qdrant_collections
      - list_source_ids
      - hybrid_search
      - get_paragraph_text
    graph_mcp_functions:
      - list_mcp_functions
      - list_parsers (check for C++ parser)
      - list_databases
      - activate_project
      - explore_graph
      - search_functions
      - query_subgraph
      - trace_flow
    action_on_failure: "fallback_to_filesystem_only"

  - check: "target_language_validation"
    verify:
      - target_language_supported
      - compiler_version_compatible
      - required_libraries_available
    action_on_failure: "warn_and_continue"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  filesystem_only_mode:
    mode: "filesystem_analysis_with_reduced_confidence"

    steps:
      1. Skip MCP queries entirely
      2. Use filesystem-only analysis (analyze_cpp_scope.py)
      3. Use grep/ctags for code structure discovery
      4. Use manual documentation review (README, docs/)
      5. Set all confidence levels: HIGH → MEDIUM, MEDIUM → LOW
      6. Add disclaimer to all outputs

    logging:
      - "Running in FILESYSTEM-ONLY MODE: MCP unavailable"
      - "Analysis limited to static analysis only"
      - "Evidence confidence reduced: HIGH → MEDIUM, MEDIUM → LOW"
      - "Cache files not created"

    notification:
      - "⚠️ MCP services unavailable or degraded"
      - "Running in filesystem-only mode with reduced confidence"
      - "Port plan will have less context and higher risk"
      - "Consider manual review and extra testing"

  recovery:
    auto_retry: 1                    # Retry 1 time before fallback
    retry_delay: 10s                 # Wait 10s before retry
    backoff_multiplier: 1.0          # No backoff
    max_retry_time: 30s              # Total retry time before fallback
```

### Build/Test Failure Handling

```yaml
build_test_failure_handling:
  on_legacy_build_failure:
    action: "continue_without_legacy_parity"
    log: "Legacy build failed, cannot establish baseline parity"
    mitigation:
      - "Port based on code analysis only"
      - "Add extra regression tests"
      - "Document higher risk profile"
      - "Require additional testing before deployment"

  on_legacy_test_failure:
    action: "continue_without_golden_cases"
    log: "Legacy tests failed, cannot establish golden cases"
    mitigation:
      - "Create test cases from code analysis"
      - "Use assertions from code as test expectations"
      - "Add exploratory testing phase"
      - "Document test gaps"

  on_target_build_failure:
    action: "stop_and_fix_build"
    log: "Target build failed, must fix before continuing"
    mitigation:
      - "Fix build errors first"
      - "Verify dependencies and configuration"
      - "Do not proceed to testing until build succeeds"

  on_target_test_failure:
    action: "debug_and_retry"
    log: "Target tests failed, investigate and fix"
    mitigation:
      - "Compare with legacy behavior"
      - "Investigate test failures"
      - "Fix port or update tests (if incorrect)"
      - "Re-run until parity achieved"
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_0_preflight:
    on_source_file_invalid:
      action: "abort_with_error"
      log: "Source file validation failed, aborting"
    on_build_system_unavailable:
      action: "warn_and_continue"
      log: "Build system unavailable, continuing without build/test verification"

  phase_1_context_discovery:
    on_mcp_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty context"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial context retrieved, continuing with available data"

  phase_2_scope_analysis:
    on_mcp_timeout:
      action: "fallback_to_filesystem_only"
      log: "graph_mcp timeout, using filesystem analysis only"
      continue: true
    on_filesystem_analysis_timeout:
      action: "return_partial_analysis"
      log: "Filesystem analysis timeout, returning partial results"
      continue: true

  phase_3_behavior_contract:
    on_incomplete_evidence:
      action: "flag_incomplete_contracts"
      log: "Incomplete evidence, marking contracts as incomplete"
      add_warning: true
      continue: true

  phase_4_parity_harness:
    on_test_generation_failure:
      action: "create_manual_test_cases"
      log: "Automated test generation failed, creating manual test cases"
      continue: true

  phase_5_port_slice:
    on_parity_failure:
      action: "stop_and_debug"
      log: "Parity tests failed, stop and debug"
      continue: false
      required_action: "Fix port until parity achieved"

  phase_6_verification:
    on_verification_failure:
      action: "document_divergence"
      log: "Post-port verification failed, documenting divergence"
      continue: true
      add_warning: true
```

## Conflict Resolution Rules

When evidence sources conflict during porting decisions:

```yaml
conflict_resolution:
  priority_rules:
    1. "For current code behavior: Trust graph_mcp over mind_mcp"
       - Example: Function signature in graph vs docs → Use graph
      - Example: Side effects in graph vs docs → Use graph

    2. "For business intent and constraints: Trust mind_mcp over graph_mcp"
       - Example: Business logic interpretation → Use docs
      - Example: Platform requirements → Use docs

    3. "For recent changes: Trust filesystem (actual files) over MCP"
       - Example: Recent commits not yet in MCP → Use filesystem
      - Example: Local modifications → Use filesystem

    4. "For historical context: Trust mind_mcp (archival knowledge)"
       - Example: Why this was implemented → Use docs/ADRs
      - Example: Original design decisions → Use docs

    5. "For build and configuration: Trust filesystem (actual build files)"
       - Example: Build system type → Check actual CMakeLists.txt/Makefile
      - Example: Dependencies → Check actual package lists

  porting_decision_conflicts:
    when: "behavior contract conflicts with code analysis"
    rules:
      - "If code behavior differs from documentation: Flag as legacy quirk, preserve in port"
      - "If documentation unclear: Use code analysis as primary source, document ambiguity"
      - "If both unclear: Mark as high-risk slice, require manual investigation"

  tiebreaker:
    when: "both sources have equal confidence but disagree"
    action: "report_both_with_disclaimer"
    format: |
      CONFLICT DETECTED:
      - mind_mcp says: {mind_mcp_claim} (confidence: {confidence})
      - graph_mcp says: {graph_mcp_claim} (confidence: {confidence})
      - Porting decision: Conservative approach (preserve existing behavior)
      Recommendation: Manual verification required, document rationale

  logging:
    log_all_conflicts: true
    include_in_port_plan: true
    severity_levels: ["RESOLVED_BY_PRIORITY", "MANUAL_VERIFICATION_NEEDED", "CONSERVATIVE_APPROACH"]
```

## Workflow

### Phase 0: Preflight MCP Context Setup (30s)

```yaml
steps:
  1. Validate all inputs (source files, target language, build/test commands)
  2. Check MCP capabilities via preflight checks
  3. Verify source file access and build system availability
  4. Initialize shared analysis map
  5. Configure timeouts, limits, and caching
  6. Report: "Preflight complete, starting porting analysis"

shared_context:
  source_files: ["{file_paths}"]
  target_language: "{language}"
  target_runtime: "{runtime_version}"
  build_commands:
    legacy: "{legacy_build_command}"
    target: "{target_build_command}"
  test_commands:
    legacy: "{legacy_test_command}"
    target: "{target_test_command}"
  analysis_timestamp: "{ISO8601}"

mcp_functions:
  - list_qdrant_collections [required]
  - list_source_ids [optional]
  - list_mcp_functions [required]
  - list_parsers [required] - Check for C++ parser
  - list_databases [required]
  - activate_project [required]

on_failure: "abort or fallback to filesystem-only mode"
```

### Phase 1: Discover Historical Context from mind_mcp (Cached, 3min)

```yaml
steps:
  1. Query for porting guides and architecture decisions
  2. Extract business constraints and technical constraints
  3. Capture known issues and workarounds
  4. Retrieve historical porting attempts and lessons learned
  5. Cache results to mcp_context_cache.json
  6. Report progress: "Phase 1 complete: {count} context items cached"

mcp_functions:
  - hybrid_search [required]
    params:
      query: "{porting_guide_query}"
      collection: "{selected_collection}"
      limit: 20
    output:
      - results: list of relevant documents
      - scores: relevance scores
      expected: "Porting guides and architecture docs"

  - sequential_search [optional]
    params:
      query: "{step_by_step_query}"
      collection: "{selected_collection}"
      limit: 10
    output:
      - results: ordered procedure documents
      expected: "Step-by-step migration procedures"

  - get_paragraph_text [required]
    params:
      paragraph_ids: ["{ids_from_hybrid_search}"]
    output:
      - text: actual paragraph content
      - citations: source references
      expected: "Detailed content with citations"

cache_output:
  file: "mcp_context_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    collections: ["{collection_ids}"]
    evidence_items:
      - id: unique_id
        type: constraint | workaround | rationale
        source: mind_mcp
        ref: paragraph_id
        confidence: high | medium | low
        content: summarized content

fallback:
  on_mcp_unavailable: "Skip context discovery, set context_cache = {}"
  on_timeout: "Return partial results, cache partial context"
```

### Phase 2: Run Scope Analysis with graph_mcp (Cached, 5min)

```yaml
steps:
  1. Run filesystem analysis script first
  2. Activate project and analyze with graph_mcp
  3. Map class hierarchies and virtual dispatch patterns
  4. Trace side effects through call graph
  5. Identify API usage patterns and unsafe patterns
  6. Cache results to mcp_analysis_cache.json
  7. Report progress: "Phase 2 complete: {count} analysis items cached"

filesystem_analysis:
  script: "scripts/analyze_cpp_scope.py"
  params:
    source_file: "{source_file_path}"
    min_lines: 120
    json_output: "/tmp/legacy-analysis.json"
    md_output: "/tmp/legacy-analysis.md"
  expected_output:
    - function_metrics: size, complexity, nesting
    - class_structure: classes, methods, inheritance
    - code_quality: unsafe patterns, code smells

mcp_functions:
  - activate_project [required]
    params:
      project_id: "{project_id}"
      database: "{database}"
      parser: "cpp" or "cxx"
    output:
      - status: activated
      - node_count: total nodes
      expected: "Project activated"

  - explore_graph [required]
    params:
      query: "{class_or_function_name}"
      limit: 100
    output:
      - nodes: discovered nodes
      - edges: connections
      expected: "Class/function discovery"

  - search_functions [required]
    params:
      query: "{domain_term}"
      limit: 50
    output:
      - functions: matching functions
      expected: "Domain-specific function discovery"

  - query_subgraph [required]
    params:
      node_id: "{class_or_function_id}"
      depth: 3
      limit: 50
    output:
      - subgraph: nodes and edges
      expected: "Context around target"

  - trace_flow [optional]
    params:
      start_node: "{function_id}"
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

  - get_node_details [required]
    params:
      node_ids: ["{node_ids}"]  # Batch 10-20 at a time
    output:
      - details: node metadata
      expected: "Node detail retrieval"

cache_output:
  file: "mcp_analysis_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    parser: "{parser}"
    evidence_items:
      - id: node_id
        type: class | function | method
        source: graph_mcp
        metadata: {name, signature, file, line}
        side_effects: [list of effects]
        dependencies: [list of dependencies]
        risk_level: high | medium | low

fallback:
  on_mcp_unavailable: "Use filesystem analysis only"
  on_timeout: "Return partial results, cache partial analysis"
```

### Phase 3: Create Enriched Behavior Contract (2min)

```yaml
steps:
  1. Load MCP evidence from caches
  2. Combine with filesystem analysis results
  3. Create behavior contract for each target function
  4. Enrich with evidence from mind_mcp and graph_mcp
  5. Report progress: "Phase 3 complete: {count} behavior contracts created"

behavior_contract_template:
  function_name: "{function_name}"

  from_mind_mcp:
    business_purpose: "Domain intent and business value"
    historical_bugs: "Known issues and edge cases"
    known_workarounds: "Legacy quirks to preserve"
    constraints: "Business and technical constraints"

  from_graph_mcp:
    signature: "Exact function signature"
    side_effects: "Observable side effects"
    dependencies: "Function dependencies and coupling"
    thread_safety: "Thread safety assumptions"

  from_filesystem:
    size_metrics: "Lines of code, complexity"
    complexity_metrics: "Cyclomatic complexity, nesting"
    unsafe_patterns: "Raw pointers, C-style casts"

  contract_fields:
    inputs: "Required and optional parameters"
    outputs: "Return values and status codes"
    side_effects: "Files, globals, state mutations"
    invariants: "Must always hold"
    error_cases: "Error and edge case handling"
    risks: "Open risks and unknowns"

output_file:
  format: "Markdown"
  template: "references/porting-artifact-templates.md"
  output: "behavior_contracts/{function_name}.md"
```

### Phase 4: Build Golden Parity Harness with MCP Evidence (3min)

```yaml
steps:
  1. Use graph_mcp evidence to ensure comprehensive coverage
  2. Use mind_mcp evidence to include historical edge cases
  3. Build comparison harness for both implementations
  4. Capture return values, outputs, and side effects
  5. Report progress: "Phase 4 complete: {count} parity cases created"

parity_coverage_from_graph_mcp:
  - list_up_entrypoint: "All public callable methods"
  - find_paths: "Happy + error paths"
  - search_functions: "Error handling keywords"
  - trace_flow: "Side effect paths"

edge_cases_from_mind_mcp:
  - historical_bugs: "Known issues from documentation"
  - boundary_conditions: "Edge cases from docs"
  - workarounds: "Legacy quirks to test"

parity_test_structure:
  input: "Test input data"
  expected_legacy_output: "Expected return value/status"
  expected_side_effects: "Expected state mutations"
  port_output: "Actual port output"
  side_effects_actual: "Actual side effects"
  match: "✅/❌ parity check"

output_file:
  format: "Markdown"
  template: "references/porting-artifact-templates.md"
  output: "parity_tests/{function_name}_parity.md"
```

### Phase 5: Port in Slices, Not in One Shot (Variable)

```yaml
steps:
  1. Use graph_mcp cluster analysis to identify slices
  2. Check dependencies with mind_mcp
  3. Create ordered slice list with evidence
  4. Port each slice with parity verification
  5. Update migration ledger after each slice
  6. Report progress: "Phase 5 complete: {slices_ported}/{total_slices} slices ported"

slice_selection_criteria:
  - call_graph_proximity: "Group functions with high mutual coupling"
  - dependency_level: "Start with low-dependency slices"
  - risk_assessment: "Identify high-risk slices requiring extra care"

slice_porting_workflow:
  1. Select slice by call graph proximity
  2. Check dependencies with mind_mcp
  3. Implement equivalent behavior only
  4. Run parity harness
  5. Commit only if parity is green
  6. Update migration ledger

slice_order_example:
  - slice_id: 1
    functions: [utility_functions]
    risk: low
    external_deps: []
    business_context: "Utility functions, no side effects"
    evidence: {mind_mcp: [para_id], graph_mcp: [node_ids]}
  - slice_id: 2
    functions: [core_logic_functions]
    risk: medium
    external_deps: [standard_library]
    business_context: "Core business logic, some dependencies"
    evidence: {mind_mcp: [para_id], graph_mcp: [node_ids]}

port_plan_script:
  script: "scripts/make_port_plan.py"
  params:
    analysis_json: "/tmp/legacy-analysis.json"
    target: "{ModuleOrClassName}"
    output: "/tmp/port-plan.md"
  expected_output:
    - slice_order: "Ordered list of slices"
    - risk_assessment: "Risk per slice"
    - evidence_links: "MCP evidence per slice"
```

### Phase 6: Enforce Parity Gates with MCP Verification (Variable)

```yaml
steps:
  1. Gate every slice with quality checks
  2. Verify with graph_mcp after porting
  3. Compare call graph structure
  4. Document any divergences
  5. Report progress: "Phase 6 complete: Parity verified for {functions_count} functions"

parity_gates:
  - build_success: "Target code builds without errors"
  - golden_parity: "All parity tests pass"
  - regression_tests: "No regressions in touched behavior"
  - warning_classes: "No new warning classes"
  - ledger_updated: "Migration ledger complete"

post_port_verification:
  - search_functions: "Re-analyze ported code"
  - query_subgraph: "Compare call graph structure"
  - structure_comparison: "Same nodes, same neighbors"
  - divergence_documentation: "Document any structural changes"

verification_report:
  format: "Markdown"
  output: "verification/{function_name}_verification.md"
  content:
    - structure_preserved: "Call graph comparison"
    - parity_results: "Test results summary"
    - divergences: "Documented changes"
    - recommendations: "Follow-up actions"
```

### Phase 7: Refactor After Equivalence (Optional)

```yaml
trigger_condition: "Parity is stable and verified"

steps:
  1. Extract helpers
  2. Rename variables/types
  3. Replace unsafe APIs
  4. Improve structure and style
  5. Run parity after each refactor step

refactor_gates:
  - parity_stable: "Parity tests pass before refactor"
  - test_after_each: "Run parity after each refactor step"
  - incremental_refactor: "One improvement at a time"
  - no_behavior_change: "Refactors must not change behavior"
```

## Non-Negotiable Rules

- ✅ Never port a multi-thousand-line function in one edit
- ✅ Never mix behavior changes with stylistic refactors in the same checkpoint
- ✅ Never remove legacy quirks until explicitly proven unnecessary by tests
- ✅ Always preserve legacy return/error contract first, then evolve intentionally
- ✅ Always use graph_mcp to verify call graph structure after porting
- ✅ Always validate inputs before analysis (security)
- ✅ Always redact sensitive data before caching or logging (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always cache MCP evidence to improve efficiency (performance)

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  porting_progress:
    - total_functions: "Total functions to port"
    - ported_functions: "Functions successfully ported"
    - remaining_functions: "Functions remaining"
    - completion_percentage: "Progress percentage"
    - high_risk_remaining: "High-risk functions remaining"

  parity_tracking:
    - total_parity_cases: "Total parity test cases"
    - passing_parity_cases: "Passing parity tests"
    - failing_parity_cases: "Failing parity tests"
    - parity_rate: "Percentage of passing tests"

  risk_assessment:
    - high_risk_functions: "High-risk functions identified"
    - medium_risk_functions: "Medium-risk functions"
    - low_risk_functions: "Low-risk functions"
    - mitigated_risks: "Successfully mitigated risks"

  mcp_performance:
    - mind_mcp_calls_total: "Total mind_mcp calls"
    - mind_mcp_calls_successful: "Successful mind_mcp calls"
    - mind_mcp_calls_failed: "Failed mind_mcp calls"
    - graph_mcp_calls_total: "Total graph_mcp calls"
    - graph_mcp_calls_successful: "Successful graph_mcp calls"
    - graph_mcp_calls_failed: "Failed graph_mcp calls"
    - cache_hit_rate: "Percentage of cache hits"

  build_test_performance:
    - legacy_build_duration: "Legacy build time"
    - legacy_test_duration: "Legacy test time"
    - target_build_duration: "Target build time"
    - target_test_duration: "Target test time"
    - total_porting_duration: "Total porting time"
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

  log_porting_decisions:
    - function_name: "Function being ported"
    - slice_id: "Slice identifier"
    - decision: "Porting decision made"
    - rationale: "Evidence-based rationale"
    - confidence: "Confidence level"

  log_parity_results:
    - function_name: "Function tested"
    - test_case: "Test case identifier"
    - legacy_output: "Legacy implementation output"
    - port_output: "Port implementation output"
    - parity_status: "PASS|FAIL"

  log_redactions:
    - redaction_type: "API_KEY|PASSWORD|TOKEN|etc"
    - count: "number_of_redactions"
    - source: "source_file|documentation|build_config"
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

  porting_progress_health:
    endpoint: "/health/porting"
    check_interval: 300s
    alert_on:
      - parity_failure_rate: "Parity failure rate >20% for >10min"
      - stale_progress: "No progress for >30min"
      - high_risk_accumulation: "High-risk functions increasing"

  build_test_health:
    endpoint: "/health/build"
    check_interval: 600s
    alert_on:
      - build_failure_rate: "Build failure rate >30% for >20min"
      - test_timeout_rate: "Test timeout rate >10% for >20min"
```

## Version History & Changelog

### Version 2.0.0 (2025-04-16)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration (was unlimited, now 30min max for build)
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
- Added preflight checks for MCP and build system validation
- Enhanced error handling with specific recovery strategies per phase
- Added progress reporting after each phase
- Added conflict resolution rules with conservative approach
- Added health monitoring and alerting

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on MCP down)
- Fixed: No conflict resolution (evidence contradictions unresolved)
- Fixed: No progress feedback (poor UX for long porting processes)
- Fixed: No build/test failure handling (unclear recovery actions)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update build/test failure handling if custom workflows exist

### Version 1.0.0 (Initial Release)

- Initial workflow for legacy C++ porting with guardrails
- Basic MCP integration (mind_mcp, graph_mcp)
- Evidence-based behavior contracts
- Slice-by-slice migration strategy
- Basic parity testing guidance

## Known Limitations

```yaml
limitations:
  mcp_dependent:
    - "Requires both mind_mcp and graph_mcp for full functionality"
    - "Filesystem-only mode has significantly reduced accuracy and confidence"
    - "Historical context unavailable if mind_mcp is down"

  performance:
    - "Very large files (>10000 lines) may exceed timeouts"
    - "Deep call graphs (>10 levels) hit traversal limits"
    - "Complex class hierarchies may exceed max_results limits"

  analysis_scope:
    - "Only analyzes specified source files"
    - "Cannot analyze external dependencies without source code"
    - "Cannot analyze runtime behavior without execution traces"

  language_support:
    - "Best support for C and C++"
    - "Partial support for C with C++ bindings"
    - "Limited support for other languages via interoperability layers"

  build_test:
    - "Requires buildable legacy code for baseline parity"
    - "Requires executable test infrastructure"
    - "Platform-specific build systems may need custom configuration"
```

## Deliverables

- Scope report (analysis JSON + markdown)
- Behavior contract per migrated function (enriched with MCP evidence)
- Port plan with slice order and evidence references
- Migration ledger with checkpoint results
- Parity/regression test results (coverage guided by graph_mcp)
- Post-port verification report (graph_mcp structure comparison)

## References

- `references/porting-artifact-templates.md` for contract, ledger, and parity-case templates
- `references/mcp-porting-playbook.md` for mind_mcp and graph_mcp integration patterns
- `references/data-ctSample01-findings.md` for real-world sample signals from a 27k-line legacy file
