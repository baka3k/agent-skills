---
name: cpp-java-migration-planner
description: Plan migration order for C++ to Java by computing dependency-aware module, file, and function waves; produce an executable worklist with cycle handling, risk scoring, and verification checkpoints with comprehensive security hardening, operational resilience, and evidence-based planning.
version: 2.1.0
last_updated: 2026-05-05
hooks:
  pre:
    - name: mcp-health-check
      timeout: 15s
      required: true
    - name: input-validation
      scope: [source_root, migration_scope]
      enable_redaction: true
  phase:
    phase_0_preflight:
      post: [progress-reporter]
    phase_1_inventory:
      post: [progress-reporter]
    phase_2_dependency_graph:
      pre: [mcp-health-check]
      post: [progress-reporter]
    phase_3_ordering:
      post: [progress-reporter]
    phase_4_cycle_handling:
      post: [progress-reporter]
    phase_5_worklist:
      post: [progress-reporter]
  post:
    - name: cleanup-handler
      paths: [migration-planning-data/]
      keep: [*.json, *.md]
---

# C++ to Java Migration Planner

Use this skill to decide what to port first, next, and last across modules and files.

## When To Use

- You need an explicit migration sequence before coding starts
- Scope includes multiple modules/files with cross-dependencies
- You need a repeatable, auditable worklist for team execution

## Avoid Using When

- Scope is a single trivial file/function
- Dependency data is unavailable and cannot be approximated
- You only need implementation guidance (use porting skills directly)

## Required Inputs

- Source root and migration scope (module list or full repo subset)
- Target root/package policy
- Active graph database context (from `activate_project`)
- Dependency sources (graph_mcp + build metadata + include/import graph fallback)
- Constraints (timeline, parallelism, risk tolerance)

## Input Validation & Security

### Scope Validation

- **Source root**: Must exist, be within allowed scope, and be readable
- **Migration scope**: Must be valid module list or directory subset
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories

**Validation rules**:
```yaml
scope_validation:
  - source_root must exist: os.path.exists(source_root)
  - source_root must be readable: os.access(source_root, os.R_OK)
  - migration_scope must be within source_root
  - Block path traversal: reject if contains "../" or absolute path
  - Max scope size: 1000 modules for planning
  - Character whitelist: [a-zA-Z0-9_\-./]
```

### Graph Context Validation

- **Active project**: Must have valid graph database context
- **Parser availability**: Must have C++ parser activated
- **MCP functions**: Verify planner functions are available

**Validation rules**:
```yaml
graph_validation:
  - active_project must be set: activate_project called
  - parser must be available: C++ parser in list_parsers
  - planner_functions must exist:
    - plan_dependency_order
    - plan_file_dependency_order
    - plan_function_dependency_order
    - compute_scc
    - topological_sort
```

### Dependency Source Validation

- **Graph MCP**: Primary source for dependency data
- **Build metadata**: Fallback for build-time dependencies
- **Include/import graph**: Fallback for source-level dependencies

**Validation rules**:
```yaml
dependency_validation:
  primary_source: "graph_mcp dependency analysis"
  fallback_sources:
    - build_metadata: "CMakeLists.txt, Makefile, build.gradle"
    - include_graph: "#include, import statements analysis"
  min_dependency_coverage: 0.7  # 70% of dependencies must be resolved
```

### Sensitive Data Redaction

When analyzing module structure that may contain sensitive information:

**Redaction patterns**:
```regex
# Module names with sensitive terms
Sensitive modules:  /auth|security|crypto|password|token/gi → '[REDACTED_MODULE]'
API endpoints:      /\/api\/v[0-9]\/[a-zA-Z0-9_-]+/gi → '/api/v[0-9]/[REDACTED]'
Connection strings:  /jdbc:[^\s"]*/gi → 'jdbc://[REDACTED]'
```

**Logging redaction**:
```yaml
logging_redaction:
  - Redact sensitive module names in planning artifacts
  - Never log original sensitive data in worklist
  - Store only redacted structure information
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # Planning timeouts
  inventory_timeout: 300s
  dependency_graph_timeout: 600s
  ordering_algorithm_timeout: 300s
  cycle_handling_timeout: 180s
  worklist_generation_timeout: 120s

  # Phase timeouts
  phase_0_preflight_timeout: 60s
  phase_1_inventory_timeout: 300s
  phase_2_dependency_graph_timeout: 600s
  phase_3_ordering_timeout: 300s
  phase_4_cycle_handling_timeout: 180s
  phase_5_worklist_timeout: 120s

  # Overall timeout
  total_planning_timeout: 1800s  # 30 minutes

  on_timeout:
    action: "return_partial_plan"
    log: "Planning timeout reached, returning partial plan"
    notify_user: "Migration planning incomplete"
```

### Resource Limits

```yaml
resource_limits:
  # Scope limits
  max_modules_to_plan: 1000
  max_files_per_module: 500
  max_functions_per_file: 500

  # Graph limits
  max_graph_nodes: 50000
  max_graph_edges: 200000
  max_scc_size: 100

  # Output limits
  max_worklist_items: 10000
  max_plan_size_mb: 100
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"
    - "  Items to process: {item_count}"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Modules analyzed: {module_count}"

  phase_error:
    - "Phase {N} error: {phase_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  final_summary:
    - "Migration planning complete"
    - "Total duration: {total_duration}s"
    - "Modules planned: {module_count}"
    - "Waves identified: {wave_count}"
    - "Cycles detected: {cycle_count}"
```

## Error Handling & Fallback Strategy

### Preflight Checks

```yaml
preflight:
  - check: "source_scope_validation"
    verify:
      - source_root_exists
      - source_root_readable
      - migration_scope_valid
    action_on_failure: "abort_with_error"

  - check: "graph_context_validation"
    verify:
      - active_project_set
      - cpp_parser_available
      - planner_functions_available
    action_on_failure: "abort_with_error"

  - check: "dependency_capability_validation"
    verify:
      - graph_mcp_accessible
      - fallback_sources_available
      - min_coverage_achievable
    action_on_failure: "fallback_to_static_analysis"

  - check: "resource_availability"
    verify:
      - sufficient_disk_space
      - sufficient_memory
      - sufficient_time_for_planning
    action_on_failure: "warn_and_continue"
```

### Graph MCP Fallback Strategy

```yaml
fallback:
  when: "graph_mcp_unavailable_or_degraded"

  static_analysis_mode:
    mode: "build_metadata_and_include_analysis"

    steps:
      1. Skip graph_mcp dependency analysis entirely
      2. Use build metadata for module-level dependencies
      3. Use include/import analysis for file-level dependencies
      4. Estimate function dependencies from call frequency
      5. Add disclaimer about reduced planning accuracy

    notification:
      - "⚠️ Graph analysis unavailable"
      - "Using static analysis for planning"
      - "Dependency order may be suboptimal"

  recovery:
    auto_retry: 1
    retry_delay: 10s
    max_retry_time: 30s
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_0_preflight:
    on_scope_invalid:
      action: "abort_with_error"
      log: "Source scope validation failed"
    on_graph_context_invalid:
      action: "abort_with_error"
      log: "Graph context validation failed"

  phase_1_inventory:
    on_inventory_incomplete:
      action: "continue_with_partial_inventory"
      log: "Module inventory incomplete"
      continue: true
    on_mapping_failure:
      action: "use_directory_structure"
      log: "File to module mapping failed, using directory structure"
      continue: true

  phase_2_dependency_graph:
    on_graph_construction_failure:
      action: "fallback_to_static_analysis"
      log: "Graph construction failed, using static analysis"
      continue: true
    on_timeout:
      action: "use_partial_graph"
      log: "Graph construction timeout, using partial graph"
      continue: true

  phase_3_ordering:
    on_ordering_failure:
      action: "use_heuristic_ordering"
      log: "Algorithmic ordering failed, using heuristics"
      continue: true
    on_cycle_detection_failure:
      action: "document_as_manual_review"
      log: "Cycle detection failed, manual review required"
      add_warning: true
      continue: true

  phase_4_cycle_handling:
    on_cycle_resolution_failure:
      action: "document_cycles_for_manual_resolution"
      log: "Automatic cycle resolution failed"
      add_warning: true
      continue: true

  phase_5_worklist:
    on_worklist_generation_failure:
      action: "create_minimal_worklist"
      log: "Worklist generation failed, creating minimal worklist"
      continue: true
```

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  planning_progress:
    - total_modules_to_plan
    - modules_analyzed
    - planning_completion_percentage
    - waves_identified

  dependency_analysis:
    - total_dependencies_analyzed
    - resolved_dependencies
    - unresolved_dependencies
    - circular_dependencies

  cycle_detection:
    - total_sccs_found
    - trivial_sccs  # single node
    - complex_sccs  # multiple nodes
    - resolved_cycles
    - unresolved_cycles

  worklist_generation:
    - total_worklist_items
    - module_level_items
    - file_level_items
    - function_level_items
```

### Logging

```yaml
logging:
  log_level: "INFO"
  log_format: "structured_json"

  log_all_phases:
    - phase_start: timestamp, phase_number, phase_name
    - phase_complete: timestamp, phase_number, results_summary
    - phase_error: timestamp, phase_number, error_details

  log_planning_decisions:
    - wave_assignment: "Module/file to wave assignment rationale"
    - dependency_resolution: "Dependency resolution decisions"
    - cycle_breaking: "Cycle breaking strategy"
    - risk_scoring: "Risk score calculation"

  log_mcp_interactions:
    - function_called: "MCP function name"
    - parameters: "Function parameters"
    - result: "Success/Failure"
    - duration: "Call duration"

  log_redactions:
    - redaction_type: "MODULE_NAME|API_ENDPOINT|etc"
    - count: "number_of_redactions"
    - source: "planning_artifacts"
```

### Health Monitoring

```yaml
health_checks:
  planning_health:
    check_interval: 300s
    alert_on:
      - stale_progress: "No progress for >5min"
      - cycle_detection_rate: "Complex cycle rate >20%"
      - dependency_resolution_rate: "Unresolved dependencies >30%"

  graph_mcp_health:
    check_interval: 60s
    alert_on:
      - graph_mcp_unavailable: "Graph MCP down for >30s"
      - planner_functions_missing: "Required planner functions unavailable"
      - query_degraded: "Graph query response time >10s for >5min"

  resource_health:
    check_interval: 600s
    alert_on:
      - disk_space_low: "Available disk <2GB"
      - memory_high: "Memory usage >85%"
      - timeout_rate: "Phase timeout rate >15%"
```

## Graph MCP Function Mapping

- `list_mcp_functions`: verify planner functions are available in runtime
- `activate_project`: select parser/database context before planning
- `plan_dependency_order`: module-level wave ordering
- `plan_file_dependency_order`: file-level wave ordering per module
- `plan_function_dependency_order`: function-level wave ordering per module
- `compute_scc`: explicit cycle report for diagnostics
- `topological_sort`: deterministic ordering check for custom edge sets

## Planning Objective

Produce a wave-based plan:

1. Module order (which modules first)
2. File order inside each module
3. Function order inside each file (for high-risk files)
4. Risk tags, blockers, and gate criteria per wave

## Workflow

### Phase 0: Preflight

1. Validate scope boundaries and readable sources
2. Run `list_mcp_functions` and confirm planner tools exist
3. Validate dependency extraction capability
4. Create output folder `migration-planning-data/`

### Phase 1: Inventory

1. Build module inventory
2. Map files to modules
3. Detect entry points, core shared libraries, and platform adapters
4. Record baseline in `module-inventory.json`

### Phase 2: Dependency Graph Construction

1. Call `plan_dependency_order(modules=...)` to build module graph and wave order
2. Call `plan_file_dependency_order(modules=...)` to build file graph per module
3. Call `plan_function_dependency_order(modules=...)` for hotspot modules/files
4. Export snapshots (`module-graph.json`, `file-graph.json`, `function-graph.json`)

### Phase 3: Ordering Algorithm

1. Validate module/file/function ordering from planner tools
2. Run `compute_scc` for unresolved cycles and diagnostics
3. Run `topological_sort` on normalized edges for deterministic tie-breaking
4. Rank nodes inside each wave by weighted score:
   - low external dependency first
   - high reuse utility first
   - lower risk first (unless critical-path override)

### Phase 4: Cycle and Blocker Handling

1. For each SCC > 1 node returned by planner tools, generate break strategy:
   - interface extraction
   - temporary compat shim
   - staged adapter pattern
2. Mark blockers and prerequisite tasks
3. Output `cycle-resolution-plan.md`

### Phase 5: Worklist and Gate Definition

1. Generate executable worklist by wave/module/file/function
2. Assign gate criteria per wave (build, parity, regression)
3. Add rollback checkpoint and owner placeholder
4. Output `migration-worklist.json` and `wave-plan.md`

## Ordering Heuristics

- Start with foundational utility modules used by many dependents
- Delay high-churn business modules until compat layer is stable
- Port leaf or low-fan-in files early for fast validation
- Keep cross-module API contracts stable before deep function porting
- Never start wave N+1 before wave N gates are green

## Output Contract

Create `migration-planning-data/` with:

- `module-inventory.json`
- `module-graph.json`
- `file-graph.json`
- `function-graph.json`
- `wave-plan.md`
- `module-port-order.md`
- `file-port-order.md`
- `function-port-order.md`
- `cycle-resolution-plan.md`
- `migration-worklist.json`
- `planning-assumptions.md`
- `planning-risks.md`

## Worklist Schema (minimum)

Each work item should contain:

- `wave_id`
- `scope_type` (`module` | `file` | `function`)
- `scope_id`
- `depends_on` (array)
- `risk_level` (`low` | `medium` | `high`)
- `gates` (build/test/parity requirements)
- `status` (`planned` by default)

## Guardrails

- Document every assumption that changes ordering
- Keep planning deterministic for the same input scope
- Flag unresolved cycles explicitly; do not hide them
- Do not perform full implementation in this skill

## Non-Negotiable Rules

- ✅ Always validate inputs before planning (security)
- ✅ Always redact sensitive data in planning artifacts (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running planning (UX)
- ✅ Always verify graph MCP functions before planning
- ✅ Never hide cycles or dependency conflicts
- ✅ Never perform implementation during planning
- ✅ Never proceed with unresolved critical dependencies

## Version History & Changelog

### Version 2.0.0 (2026-04-29)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration with phase-specific limits
- Enhanced fallback strategy with static analysis mode

**New Features:**
- ✅ Added Input Validation & Security section
- ✅ Added Performance & Operational Configuration section
- ✅ Added Error Handling & Fallback Strategy section
- ✅ Added Observability & Metrics section
- ✅ Added Version History & Changelog
- ✅ Added Non-Negotiable Rules section
- ✅ Enhanced Graph MCP Function Mapping documentation

**Improvements:**
- Enhanced dependency validation with coverage requirements
- Added phase-specific error handling strategies
- Enhanced cycle detection and resolution handling
- Added progress reporting with phase-level granularity
- Improved planning with fallback modes for graph unavailability

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on graph errors)
- Fixed: No progress feedback (poor UX for long planning)
- Fixed: No observability (hard to track planning progress)
- Fixed: Limited error recovery (planning would abort on any error)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update error handling if custom workflows exist
- Review fallback configuration for graph unavailability

### Version 1.1.0 (Initial Release)

- Initial workflow for C++ to Java migration planning
- Basic Graph MCP function integration
- Five-phase workflow (Preflight, Inventory, Dependency Graph, Ordering, Worklist)
- Basic cycle detection and resolution
- Basic worklist generation

## Known Limitations

```yaml
limitations:
  graph_dependent:
    - "Requires graph_mcp for optimal planning accuracy"
    - "Static-only mode has significantly reduced accuracy"
    - "Complex dependency patterns may be missed in fallback mode"

  planning_scope:
    - "Optimized for medium-scale migrations (10-1000 modules)"
    - "Very large migrations (>1000 modules) may need custom configuration"
    - "Cross-language dependencies need manual verification"

  cycle_resolution:
    - "Cannot automatically resolve all circular dependencies"
    - "Complex cycles may require manual intervention"
    - "Some cycle breaking strategies may be suboptimal"

  dependency_analysis:
    - "Runtime dependencies may not be fully captured statically"
    - "Dynamic loading patterns need manual analysis"
    - "Plugin architectures may require special handling"
```
