---
name: cpp-java-porting-orchestrator
description: Orchestrate end-to-end C++ to Java migration by sequencing pre-porting, file-structure porting, function porting, and legacy guardrails with parity-focused checkpoints and migration deliverables with comprehensive security hardening, operational resilience, and evidence-based orchestration.
version: 2.2.0
last_updated: 2026-05-05
hooks:
  pre:
    - name: mcp-health-check
      timeout: 15s
      required: true
    - name: skill-chain-verification
      skills: [cpp-java-migration-planner, cpp-java-pre-porting, cpp-java-file-structure-porting, cpp-java-function-porting, legacy-cpp-porting-guardrails]
    - name: migration-scope-validation
      migration_type: cpp_to_java
      validate_target_package: true
      enable_redaction: true
  phase:
    phase_0_preflight:
      post: [progress-reporter]
    phase_1_pre_porting:
      pre: [mcp-health-check]
      post: [progress-reporter]
    phase_2_file_structure:
      pre: [mcp-health-check]
      post: [progress-reporter]
    phase_3_function_porting:
      pre: [mcp-health-check]
      post: [progress-reporter, parity-gate-check]
    phase_4_parity_gates:
      pre: [mcp-health-check]
      post: [progress-reporter, parity-gate-check]
    all_phases:
      post: [progress-reporter]
  post:
    - name: migration-artifact-cleanup
      keep: [migration-planning-data/*.json, migration-planning-data/*.md, porting-data/*.parquet, parity-reports/*.md]
    - name: parity-report-generation
      format: markdown
      include: [build_parity, test_parity, functional_parity]
---

# C++ to Java Porting Orchestrator

Use this skill to coordinate the full migration flow while keeping behavior stable.

## Dependencies

- `cpp-java-migration-planner`
- `cpp-java-pre-porting`
- `cpp-java-file-structure-porting`
- `cpp-java-function-porting`
- `legacy-cpp-porting-guardrails`

## When To Use

- You are migrating a module/system from C++ to Java
- You need staged execution with explicit quality gates
- You want consistent artifacts across module/file/function levels

## Avoid Using When

- Migration scope is tiny (single function or trivial file)
- You only need one specific phase (use the specific skill instead)
- Target language is not Java
- Quick prototyping without quality gates

## Required Inputs

- Migration scope: module, file set, or function set
- Source and target roots
- Legacy build/test commands and Java build/test commands
- Constraints: timeline, risk tolerance, performance targets

## Input Validation & Security

### Migration Scope Validation

- **Scope type**: Must be one of `module`, `file-set`, `function-set`, `dry-run`
- **Source root**: Must exist and be readable
- **Target root**: Must exist and be writable
- **Scope boundaries**: Must be within allowed directories

**Validation rules**:
```yaml
scope_validation:
  allowed_scope_types: ["module", "file-set", "function-set", "dry-run"]
  - source_root must exist: os.path.exists(source_root)
  - source_root must be readable: os.access(source_root, os.R_OK)
  - target_root must exist: os.path.exists(target_root)
  - target_root must be writable: os.access(target_root, os.W_OK)
  - Block path traversal: reject if contains "../" or absolute path
  - Max scope size: 1000 files for batch operations
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
    test: [ctest, junit, testng]

  blocked_patterns:
    - "rm -rf"
    - "format"
    - "del /"

  timeout_requirements:
    - legacy_build: max 30 minutes
    - legacy_test: max 10 minutes
    - java_build: max 30 minutes
    - java_test: max 10 minutes
```

### Dependency Validation

- **Skill availability**: Verify dependent skills are installed
- **Version compatibility**: Check skill version compatibility
- **MCP availability**: Verify MCP services for dependencies

**Validation rules**:
```yaml
dependency_validation:
  required_skills:
    - cpp-java-migration-planner: ">=1.0.0"
    - cpp-java-pre-porting: ">=2.0.0"
    - cpp-java-file-structure-porting: ">=2.0.0"
    - cpp-java-function-porting: ">=2.0.0"
    - legacy-cpp-porting-guardrails: ">=2.0.0"

  mcp_requirements:
    - mind_mcp: "for context retrieval"
    - graph_mcp.list_mcp_functions: "verify planning functions"
    - graph_mcp.plan_dependency_order: "module wave planning"
    - graph_mcp.plan_file_dependency_order: "file wave planning"
    - graph_mcp.plan_function_dependency_order: "function wave planning"
    - graph_mcp.compute_scc: "cycle diagnostics"
    - graph_mcp.topological_sort: "deterministic ordering"
```

### Sensitive Data Redaction

When orchestrating migration that may process sensitive information:

**Redaction patterns**:
```regex
# Apply redaction patterns from all dependent skills
# Credentials, API keys, passwords, tokens
# Network information, database strings
# Personal data, email addresses, phone numbers
```

**Logging redaction**:
```yaml
logging_redaction:
  - Apply redaction patterns from all dependent skills
  - Never log original sensitive data in orchestration artifacts
  - Store only redacted migration information
  - Apply redaction before caching to MCP files
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # Stage timeouts
  stage_0_intake_timeout: 60s
  stage_1_migration_planning_timeout: 600s
  stage_2_pre_porting_timeout: 600s
  stage_3_file_skeleton_timeout: 1800s
  stage_4_function_implementation_timeout: 3600s
  stage_5_verification_timeout: 600s

  # Per-item timeouts
  per_file_porting_timeout: 300s
  per_function_porting_timeout: 120s
  per_parity_check_timeout: 180s

  # Overall timeout
  total_orchestration_timeout: 7200s  # 2 hours

  on_timeout:
    action: "checkpoint_and_continue"
    log: "Stage timeout reached, creating checkpoint"
    notify_user: "Orchestration incomplete due to timeout"
    save_state: true
```

### Resource Limits

```yaml
resource_limits:
  # Migration scope limits
  max_files_per_migration: 1000
  max_functions_per_file: 500
  max_concurrent_operations: 5

  # Artifact limits
  max_artifact_size_mb: 1000
  max_ledger_size_mb: 100

  # Memory limits
  max_memory_per_stage: 4GB
  max_total_cache_size: 500MB
```

### Progress Feedback

```yaml
progress_reporting:
  stage_start:
    - "Stage {N} started: {stage_name} (estimated: {estimated_time}s)"
    - "  Items to process: {item_count}"

  stage_complete:
    - "Stage {N} complete: {stage_name}"
    - "  Duration: {actual_time}s"
    - "  Items processed: {processed_count}/{total_count}"

  stage_error:
    - "Stage {N} error: {stage_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  item_progress:
    - "Processing {item_type}: {current}/{total} - {item_name}"
    - "  Status: {status}"
    - "  Duration: {duration}s"

  final_summary:
    - "Migration orchestration complete"
    - "Total duration: {total_duration}s"
    - "Files processed: {file_count}"
    - "Functions ported: {function_count}"
    - "Parity rate: {parity_rate}%"
    - "Divergences: {divergence_count}"
```

### Checkpoint & Recovery

```yaml
checkpoint_strategy:
  checkpoint_frequency: "after_each_stage"
  checkpoint_location: ".migration-checkpoints/"
  checkpoint_content:
    - completed_stages
    - processed_items
    - artifact_locations
    - state_snapshot

  recovery:
    auto_resume: true
    resume_from_last_checkpoint: true
    skip_completed_items: true
```

## Error Handling & Fallback Strategy

### Preflight Checks

```yaml
preflight:
  - check: "migration_scope_validation"
    verify:
      - source_root_valid
      - target_root_valid
      - scope_type_valid
      - scope_size_within_limits
    action_on_failure: "abort_with_error"

  - check: "dependency_validation"
    verify:
      - required_skills_available
      - skill_versions_compatible
      - mcp_services_accessible
    action_on_failure: "abort_with_error"

  - check: "build_test_validation"
    verify:
      - legacy_build_available
      - java_build_available
      - test_infrastructure_ready
    action_on_failure: "warn_and_continue"

  - check: "resource_availability"
    verify:
      - sufficient_disk_space
      - sufficient_memory
      - sufficient_time_for_migration
    action_on_failure: "warn_and_continue"
```

### Stage Failure Strategy

```yaml
stage_failure_handling:
  on_stage_0_failure:
    action: "abort_with_error"
    log: "Intake stage failed, cannot proceed"
    recovery: "fix_scope_inputs_and_retry"

  on_stage_1_failure:
    action: "abort_or_continue_with_warnings"
    log: "Migration planning stage failed"
    recovery: "review_partial_artifacts_and_decide"

  on_stage_2_failure:
    action: "continue_from_last_checkpoint"
    log: "Pre-porting stage failed"
    recovery: "resume_from_checkpoint_or_skip_failed_files"

  on_stage_3_failure:
    action: "continue_from_last_checkpoint"
    log: "File skeleton stage failed"
    recovery: "resume_from_checkpoint_or_skip_failed_files"

  on_stage_4_failure:
    action: "complete_with_warnings"
    log: "Function implementation stage failed"
    recovery: "resume_from_checkpoint_or_skip_failed_functions"

  on_stage_5_failure:
    action: "complete_with_warnings"
    log: "Verification stage failed"
    recovery: "document_failures_and_complete"
```

### Quality Gate Failures

```yaml
quality_gate_failures:
  on_migration_planning_gate_failure:
    action: "stop_and_review"
    log: "Migration wave plan incomplete"
    requirements:
      - "Module wave plan must exist"
      - "File wave plan must exist"
      - "Function wave plan must exist for hotspot modules"

  on_pre_porting_gate_failure:
    action: "stop_and_review"
    log: "Pre-porting artifacts incomplete"
    requirements:
      - "All pre-porting artifacts must be present"
      - "Compatibility gaps must be documented"
      - "Migration roadmap must be approved"

  on_file_skeleton_gate_failure:
    action: "review_and_fix"
    log: "File skeleton artifacts incomplete"
    requirements:
      - "All files must have Java skeletons"
      - "1:1 mapping must be preserved"
      - "Compatibility requirements documented"

  on_function_parity_gate_failure:
    action: "stop_and_debug"
    log: "Function parity checks failed"
    requirements:
      - "All functions must pass parity tests"
      - "No regressions allowed"
      - "Divergences must be documented"

  on_verification_gate_failure:
    action: "document_and_complete"
    log: "Verification checks failed"
    requirements:
      - "Build must succeed"
      - "Tests must pass (with documented exceptions)"
      - "Migration ledger must be complete"
```

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  orchestration_progress:
    - total_stages
    - completed_stages
    - current_stage
    - overall_completion_percentage

  migration_progress:
    - total_files_to_port
    - files_ported
    - total_functions_to_port
    - functions_ported

  quality_metrics:
    - parity_tests_run
    - parity_tests_passed
    - parity_rate_percentage
    - regressions_detected
    - divergences_documented

  resource_usage:
    - total_duration_seconds
    - disk_space_used_mb
    - memory_used_mb
    - cache_hit_rate

  artifact_generation:
    - pre_porting_artifacts
    - file_skeleton_artifacts
    - function_porting_artifacts
    - verification_artifacts
```

### Logging

```yaml
logging:
  log_level: "INFO"
  log_format: "structured_json"

  log_all_stages:
    - stage_start: timestamp, stage_number, stage_name
    - stage_complete: timestamp, stage_number, results_summary
    - stage_error: timestamp, stage_number, error_details

  log_orchestration_decisions:
    - scope_decision: "Migration scope rationale"
    - stage_sequence: "Stage ordering decisions"
    - quality_gate_results: "Quality gate outcomes"
    - checkpoint_created: "Checkpoint creation events"

  log_quality_gates:
    - gate_name: "Quality gate identifier"
    - gate_status: "PASS|FAIL|WARN"
    - requirements_checked: "List of requirements"
    - failures: "Specific failure reasons"

  log_redactions:
    - redaction_type: "API_KEY|PASSWORD|etc"
    - count: "number_of_redactions"
    - source: "skill_orchestration"
```

### Health Monitoring

```yaml
health_checks:
  orchestration_health:
    check_interval: 300s
    alert_on:
      - stale_progress: "No progress for >10min"
      - stage_failure_rate: "Stage failure rate >20%"
      - quality_gate_failure_rate: "Gate failure rate >10%"

  dependency_health:
    check_interval: 60s
    alert_on:
      - skill_unavailable: "Required skill unavailable"
      - mcp_degraded: "MCP response time >10s for >5min"

  resource_health:
    check_interval: 600s
    alert_on:
      - disk_space_low: "Available disk <1GB"
      - memory_high: "Memory usage >90%"
      - timeout_rate: "Timeout rate >15%"
```

## Orchestration Workflow

### Stage 0: Intake and Scope

1. Parse user scope (`--module`, `--file`, `--function`, `--dry-run`)
2. Build worklist (files/functions) and priorities
3. Define output root for artifacts

### Stage 1: Migration Planning

1. Run `cpp-java-migration-planner`
2. Call `graph_mcp.plan_dependency_order` for module waves
3. Call `graph_mcp.plan_file_dependency_order` for file waves
4. Call `graph_mcp.plan_function_dependency_order` for function waves
5. Use `graph_mcp.compute_scc` and `graph_mcp.topological_sort` for cycle/ordering diagnostics
6. Freeze sequencing assumptions and cycle-break strategy

### Stage 2: Pre-Porting Plan

1. Run `cpp-java-pre-porting`
2. Review compatibility gaps and migration roadmap
3. Freeze initial compat-layer contract

### Stage 3: File Skeleton Pass

1. Run `cpp-java-file-structure-porting` by planner wave order (`migration-worklist.json`)
2. Enforce strict 1:1 naming and path mapping
3. Collect unresolved constructs and compat requirements

### Stage 4: Function Implementation Pass

1. Port functions in planner wave order with `cpp-java-function-porting`
2. Apply `legacy-cpp-porting-guardrails` parity checks per slice
3. Stop and debug when parity/regression gates fail

### Stage 5: Verification and Reporting

1. Run compile + tests + parity/regression checks
2. Summarize divergences and unresolved manual items
3. Publish migration ledger and verification report

## Quality Gates

- Pre-porting artifacts complete before code conversion starts
- Migration wave plan is approved before pre-porting starts
- File skeleton artifacts complete before function-level conversion
- Function-level parity passes before moving to next slice
- Divergences are documented with rationale and follow-up owner

## Deliverables

- `migration-planning-data/*`
- `pre-porting-data/*`
- `tasks/porting_<filename>/*`
- `tasks/porting_<function_name>/*`
- Migration ledger and verification summary

## Non-Negotiable Rules

- ✅ Always validate inputs before orchestration (security)
- ✅ Always redact sensitive data in migration artifacts (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running orchestration (UX)
- ✅ Always enforce quality gates between stages
- ✅ Never skip stages in the orchestration workflow
- ✅ Never bypass quality gates for speed
- ✅ Never proceed with incomplete migration artifacts

## Version History & Changelog

### Version 2.0.0 (2026-04-29)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration with stage-specific limits
- Enhanced fallback strategy with checkpoint & recovery

**New Features:**
- ✅ Added Input Validation & Security section
- ✅ Added Performance & Operational Configuration section
- ✅ Added Error Handling & Fallback Strategy section
- ✅ Added Observability & Metrics section
- ✅ Added Version History & Changelog
- ✅ Added Non-Negotiable Rules section
- ✅ Added Checkpoint & Recovery strategy

**Improvements:**
- Enhanced dependency validation with version checks
- Added stage-specific error handling strategies
- Enhanced quality gate failure handling
- Added progress reporting with item-level granularity
- Improved orchestration with checkpoint recovery

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on stage errors)
- Fixed: No progress feedback (poor UX for long migrations)
- Fixed: No observability (hard to track migration progress)
- Fixed: No checkpoint/recovery (data loss on failures)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update error handling if custom workflows exist
- Review checkpoint configuration for recovery strategy

### Version 1.0.0 (Initial Release)

- Initial orchestration workflow for C++ to Java migration
- Basic sequencing of pre-porting, file-structure, function porting stages
- Basic quality gates and deliverables
- Integration with legacy-cpp-porting-guardrails

## Known Limitations

```yaml
limitations:
  orchestration_dependent:
    - "Requires all dependent skills to be available"
    - "Orchestration fails if critical skills are missing"
    - "Version compatibility constraints apply"

  migration_scope:
    - "Optimized for medium-scale migrations (10-1000 files)"
    - "Very large migrations (>1000 files) may need custom configuration"
    - "Cross-module dependencies need manual verification"

  quality_gates:
    - "Cannot automatically fix all parity failures"
    - "Manual intervention required for complex divergences"
    - "Some compatibility gaps require manual resolution"

  operational:
    - "Long-running migrations may hit timeout limits"
    - "Large codebases may require significant disk space for artifacts"
    - "Parallel processing limited by system resources"
```
