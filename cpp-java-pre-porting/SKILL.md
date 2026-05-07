---
name: cpp-java-pre-porting
description: Prepare pre-porting analysis artifacts for C++ to Java migration, including compatibility gap inventory, compat-layer design, type mapping, migration roadmap, testing strategy, and risk mitigation outputs in pre-porting-data with comprehensive security hardening, operational resilience, and evidence-based planning.
version: 2.1.0
last_updated: 2026-04-29
---

# C++ to Java Pre-Porting

Use this skill before implementation porting starts. The goal is to reduce migration risk by producing auditable planning artifacts and a compatibility-layer plan.

## When To Use

- You are preparing a C++ to Java migration at module or system scope
- You need a compatibility-layer design before converting files/functions
- You want explicit migration phases, risks, and measurable success criteria

## Avoid Using When

- Migration scope is tiny (single function or trivial file)
- Target language is not Java
- You need immediate code conversion without planning artifacts
- Compatibility layer is already designed and frozen

## Required Inputs

- Source root directory and module/file scope
- Target Java package/root conventions
- Build/test commands for legacy and Java targets (if available)
- Constraints: timeline, performance targets, prohibited changes
- `migration-planning-data/wave-plan.md` and `migration-worklist.json` (recommended)

## Input Validation & Security

### Path Validation

- **Source root path**: Must exist, be within allowed scope, and be readable
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **Path sanitization**: Limit to 1000 characters, whitelist allowed characters
- **Access verification**: Verify read access before analysis

**Validation rules**:
```yaml
path_validation:
  - source_root must be a valid directory
  - source_root must be readable: os.access(path, os.R_OK)
  - Block path traversal: reject if contains "../" or absolute path
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max path length: 1000 characters
  - Max directory depth: 20 levels
```

### Module Scope Validation

- **Module boundaries**: Must be within source root
- **File extensions**: Validate C++ source files (.cpp, .cc, .cxx, .h, .hpp)
- **Scope size**: Limit analysis to prevent resource exhaustion

**Validation rules**:
```yaml
scope_validation:
  allowed_extensions: [".cpp", ".cc", ".cxx", ".h", ".hpp", ".c"]
  max_files_to_analyze: 1000
  max_total_size_mb: 500
  max_directory_depth: 20
```

### Target Java Package Validation

- **Package naming**: Must follow Java package naming conventions
- **Target root**: Must be writable for artifact generation
- **Package conflicts**: Check for existing packages

**Validation rules**:
```yaml
package_validation:
  - Package names must be lowercase: /^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$/
  - Max package length: 256 characters
  - Target root must be writable: os.access(path, os.W_OK)
  - Check for existing packages to avoid conflicts
```

### Build/Test Command Validation

- **Command format**: Must be valid shell commands
- **Command sanitization**: Remove dangerous operations
- **Timeout specification**: Commands must have timeout limits

**Validation rules**:
```yaml
command_validation:
  allowed_commands:
    build: [make, cmake, gradle, mvn, bazel]
    test: [ctest, junit, testng, pytest]

  blocked_patterns:
    - "rm -rf"
    - "format"
    - "del /"

  timeout_requirements:
    - build_commands: max 30 minutes
    - test_commands: max 10 minutes
```

### Sensitive Data Redaction

When analyzing C++ code that may contain sensitive information:

**Redaction patterns**:
```regex
# Credentials and Secrets
API keys:           /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
Passwords:          /password.*/gi → '[REDACTED_PASSWORD]'
Secrets:            /secret.*/gi → '[REDACTED_SECRET]'
Tokens:             /token.*/gi → '[REDACTED_TOKEN]'
License keys:       /license.*/gi → '[REDACTED_LICENSE]'

# Network Information
IP addresses:       /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'
URLs with creds:    /\b[\w-]+:\/\/[\w-]+:[\w-]+@/gi → '[REDACTED_URL]'

# Database Strings
Connection strings:  /\bjdbc:[^\s]+\b/gi → 'jdbc://[REDACTED]'
```

**Logging redaction**:
```yaml
logging_redaction:
  - Log all redactions in analysis report
  - Never log original sensitive data
  - Store only redacted evidence in artifacts
  - Apply redaction before caching to MCP files
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # MCP call timeouts
  mcp_call_timeout: 30s
  query_timeout: 45s
  batch_timeout: 60s

  # Analysis timeouts
  source_analysis_timeout: 300s
  gap_analysis_timeout: 180s
  compat_design_timeout: 240s
  roadmap_creation_timeout: 120s

  # Phase timeouts
  phase_0_preflight_timeout: 30s
  phase_1_source_analysis_timeout: 300s
  phase_2_compat_design_timeout: 240s
  phase_3_type_mapping_timeout: 180s
  phase_4_validation_timeout: 120s

  on_timeout:
    action: "return_partial_results"
    log: "Phase timeout reached, returning partial results"
    notify_user: "Analysis incomplete due to timeout"
    continue_next_phase: true
```

### Resource Limits

```yaml
resource_limits:
  # File size limits
  max_source_file_size: 10MB
  max_total_analysis_size: 100MB

  # Analysis limits
  max_files_to_analyze: 1000
  max_functions_per_file: 500
  max_classes_per_file: 100
  max_type_mappings: 10000

  # Memory limits
  max_memory_per_analysis: 2GB
  max_cache_size: 100MB
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Artifacts: {artifacts_created}"

  phase_error:
    - "Phase {N} error: {phase_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  final_summary:
    - "Pre-porting analysis complete"
    - "Total duration: {total_duration}s"
    - "Artifacts created: {artifact_count}"
    - "Compatibility gaps: {gap_count}"
    - "Type mappings: {type_mapping_count}"
```

### Caching Strategy

```yaml
cache:
  source_analysis_cache:
    enabled: true
    ttl: 1800
    file: "source_analysis_cache.json"
    invalidation: "on_source_change"

  compat_design_cache:
    enabled: true
    ttl: 2400
    file: "compat_design_cache.json"
    invalidation: "on_workflow_end"

  shared_cache:
    enabled: true
    ttl: 3600
    file: "pre_porting_cache.json"
    invalidation: "on_workflow_end"
```

## Error Handling & Fallback Strategy

### Preflight Checks

```yaml
preflight:
  - check: "source_path_validation"
    verify:
      - source_root_exists
      - source_root_readable
      - valid_cpp_files_present
    action_on_failure: "abort_with_error"

  - check: "target_path_validation"
    verify:
      - target_root_writable
      - package_naming_valid
    action_on_failure: "abort_with_error"

  - check: "mcp_capability_check"
    mind_mcp_functions:
      - list_qdrant_collections
      - hybrid_search
      - get_paragraph_text
    graph_mcp_functions:
      - list_mcp_functions
      - list_databases
      - explore_graph
      - search_functions
      - plan_dependency_order
    action_on_failure: "fallback_to_static_analysis"

  - check: "resource_availability"
    verify:
      - sufficient_disk_space
      - sufficient_memory
    action_on_failure: "warn_and_continue"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  static_analysis_mode:
    mode: "filesystem_only_analysis"

    steps:
      1. Skip MCP queries entirely
      2. Use grep/ctags for code structure discovery
      3. Use manual documentation review
      4. Set all confidence levels: HIGH → MEDIUM
      5. Add disclaimer to all outputs

    notification:
      - "⚠️ MCP services unavailable"
      - "Running in static analysis mode"
      - "Analysis may be incomplete"

  recovery:
    auto_retry: 1
    retry_delay: 10s
    max_retry_time: 30s
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_0_preflight:
    on_source_invalid:
      action: "abort_with_error"
      log: "Source path validation failed"
    on_target_invalid:
      action: "abort_with_error"
      log: "Target path validation failed"

  phase_1_source_analysis:
    on_mcp_timeout:
      action: "fallback_to_static_analysis"
      log: "MCP timeout, using static analysis"
      continue: true
    on_filesystem_timeout:
      action: "return_partial_analysis"
      log: "Filesystem analysis timeout"
      continue: true

  phase_2_compat_design:
    on_incomplete_evidence:
      action: "flag_gaps_for_manual_review"
      log: "Incomplete evidence for compatibility gaps"
      add_warning: true
      continue: true

  phase_3_type_mapping:
    on_mapping_conflicts:
      action: "document_conflict_and_continue"
      log: "Type mapping conflicts detected"
      add_warning: true
      continue: true

  phase_4_validation:
    on_validation_failure:
      action: "document_risk_and_continue"
      log: "Validation incomplete"
      add_warning: true
      continue: true
```

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  analysis_progress:
    - total_files_to_analyze
    - files_analyzed
    - analysis_completion_percentage
    - remaining_high_priority_files

  compatibility_gaps:
    - total_gaps_identified
    - critical_gaps
    - gaps_with_compat_solution
    - gaps_requiring_manual_review

  type_mappings:
    - total_type_mappings_created
    - direct_mappings
    - wrapper_mappings
    - complex_mappings

  artifacts_created:
    - analysis_artifacts
    - design_artifacts
    - planning_artifacts
    - validation_artifacts

  mcp_performance:
    - mind_mcp_calls_total
    - mind_mcp_calls_successful
    - graph_mcp_calls_total
    - graph_mcp_calls_successful
    - cache_hit_rate
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

  log_analysis_decisions:
    - gap_identified: "Compatibility gap details"
    - mapping_decision: "Type mapping rationale"
    - design_decision: "Compat layer design rationale"
    - confidence: "Confidence level"

  log_redactions:
    - redaction_type: "API_KEY|PASSWORD|etc"
    - count: "number_of_redactions"
    - source: "source_file|documentation"
```

### Health Monitoring

```yaml
health_checks:
  mcp_health:
    check_interval: 60s
    alert_on:
      - mind_mcp_unavailable: "down for >30s"
      - graph_mcp_unavailable: "down for >30s"
      - mcp_degraded: "response time >10s for >5min"

  analysis_health:
    check_interval: 300s
    alert_on:
      - stale_progress: "No progress for >30min"
      - high_gap_count: "Critical gaps increasing"
      - resource_exhaustion: "Memory/disk limits approached"
```

## Workflow

### Phase 0: Preflight

1. Validate source path accessibility and scope
2. Identify module boundaries and entry points
3. Load planner artifacts (`wave-plan.md`, `migration-worklist.json`) if available
4. Confirm available analysis tools (graph/static analysis)
5. Create `pre-porting-data/` output directory

### Phase 1: Source and Gap Analysis

1. Inventory language features and runtime behaviors used in C++
2. Inventory stdlib/third-party dependencies
3. Identify features requiring compatibility bridges in Java
4. Produce `source-analysis.md` and `feature-gap-analysis.md`

### Phase 2: Compatibility Layer Design

1. Design package layout for `compat` components
2. Decide wrapper vs reimplementation strategy per feature
3. Define API contracts for compat interfaces
4. Produce `compat-layer-design.md` and `compat-layer-api.md`

### Phase 3: Type and Migration Planning

1. Build type mapping matrix C++ -> Java
2. Define conversion strategy (direct, staged, shim-first)
3. Create phased roadmap (creation -> integration -> optimization -> removal)
4. Produce `type-mappings.json` and `migration-roadmap.md`

### Phase 4: Validation, Risks, and Metrics

1. Define parity/regression test strategy and performance baselines
2. Identify technical/business risks and mitigations
3. Define success metrics and acceptance thresholds
4. Produce `testing-framework.md`, `performance-baseline.md`, `risk-mitigation-plan.md`, `success-metrics.md`

## Output Contract

Create these files under `pre-porting-data/`:

- `pre-porting-plan.md`
- `source-analysis.md`
- `compat-layer-design.md`
- `feature-gap-analysis.md`
- `type-mappings.json`
- `migration-roadmap.md`
- `compat-layer-api.md`
- `testing-framework.md`
- `performance-baseline.md`
- `risk-mitigation-plan.md`
- `success-metrics.md`

## Guardrails

- Keep decisions evidence-based and traceable
- Do not start full-code conversion in this skill
- Flag unknowns explicitly; do not hide assumptions
- Escalate high-risk dependencies (threading, memory, IPC, platform APIs)

## Non-Negotiable Rules

- ✅ Always validate inputs before analysis (security)
- ✅ Always redact sensitive data before caching or logging (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always cache analysis evidence to improve efficiency (performance)
- ✅ Never start code conversion in pre-porting phase
- ✅ Never hide assumptions or unknowns
- ✅ Never skip compatibility layer design for complex features

## Version History & Changelog

### Version 2.0.0 (2026-04-29)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration with specific limits
- Enhanced fallback strategy with static analysis mode

**New Features:**
- ✅ Added Input Validation & Security section
- ✅ Added Performance & Operational Configuration section
- ✅ Added Error Handling & Fallback Strategy section
- ✅ Added Observability & Metrics section
- ✅ Added Version History & Changelog
- ✅ Added Non-Negotiable Rules section

**Improvements:**
- Enhanced MCP integration with specific function names
- Added preflight checks for validation
- Enhanced error handling with specific recovery strategies per phase
- Added progress reporting after each phase
- Added health monitoring and alerting

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on MCP down)
- Fixed: No progress feedback (poor UX for long analysis processes)
- Fixed: No observability (hard to track analysis progress)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update error handling if custom workflows exist

### Version 1.0.0 (Initial Release)

- Initial workflow for C++ to Java pre-porting analysis
- Basic artifact generation (gap analysis, compat design, type mappings)
- Four-phase workflow (Preflight, Analysis, Design, Validation)
- Basic MCP integration hints

## Known Limitations

```yaml
limitations:
  mcp_dependent:
    - "Requires both mind_mcp and graph_mcp for full functionality"
    - "Static-only mode has significantly reduced accuracy"
    - "Historical context unavailable if mind_mcp is down"

  analysis_scope:
    - "Only analyzes specified source files"
    - "Cannot analyze external dependencies without source code"
    - "Cannot analyze runtime behavior without execution traces"

  language_support:
    - "Best support for C++ to Java"
    - "Type system mappings may be incomplete for edge cases"
    - "Template metaprogramming requires manual analysis"

  compatibility:
    - "Cannot automatically resolve all compatibility gaps"
    - "Complex runtime patterns may require manual design"
    - "Platform-specific code needs per-platform analysis"
```
