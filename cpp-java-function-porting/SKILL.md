---
name: cpp-java-function-porting
description: Port one C++ function to Java with strict 1-to-1 name preservation, dependency/impact analysis, compatibility-bridge planning, and function-level migration task artifacts with comprehensive security hardening, operational resilience, and evidence-based porting.
version: 2.1.0
last_updated: 2026-04-29
---

# C++ to Java Function Porting

Use this skill for detailed conversion of an individual function after skeleton generation.

## When To Use

- You are converting one function at a time
- You need dependency-aware conversion and compatibility notes
- You need auditable function-level artifacts

## Avoid Using When

- Function is trivial (getter/setter with no logic)
- You need to convert multiple functions together (use file-structure-porting)
- Target language is not Java
- Function is already ported

## Required Inputs

- Source function identifier (name + file/class context)
- Source file path and target Java file path
- Existing compat-layer contracts (if available)
- `migration-worklist.json` function wave context (recommended)

## Input Validation & Security

### Function Identifier Validation

- **Function name**: Must be valid identifier and exist in source
- **File context**: Must be valid C++ source file
- **Class context**: Must be valid for member functions

**Validation rules**:
```yaml
function_validation:
  - function_name must be valid: /^[a-zA-Z_][a-zA-Z0-9_]*$/
  - function must exist in source file
  - source_file must be readable: os.access(file_path, os.R_OK)
  - Max function name length: 256 characters
```

### Target Path Validation

- **Target file path**: Must be writable
- **Package structure**: Must follow Java package conventions
- **File conflicts**: Check for existing files

**Validation rules**:
```yaml
target_validation:
  - target_file must be writable: os.access(target_path, os.W_OK)
  - Package paths must be valid: /^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$/
  - Check for file conflicts before writing
```

### Sensitive Data Redaction

When extracting function code that may contain sensitive information:

**Redaction patterns**:
```regex
# String literals with sensitive data
Password strings:  /password\s*=\s*"[^"]*"/gi → 'password = "[REDACTED]"'
API key strings:  /api_key\s*=\s*"[^"]*"/gi → 'api_key = "[REDACTED]"'
Connection strings:  /jdbc:[^\s"]*/gi → 'jdbc://[REDACTED]'
Hardcoded IPs:  /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'
```

**Logging redaction**:
```yaml
logging_redaction:
  - Redact sensitive literals in function metadata
  - Never log original sensitive data in source-function.json
  - Store only redacted function structure information
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # Analysis timeouts
  function_extraction_timeout: 60s
  dependency_analysis_timeout: 90s
  compat_gap_analysis_timeout: 60s
  java_conversion_timeout: 120s
  artifact_generation_timeout: 30s

  # Phase timeouts
  phase_1_discovery_timeout: 60s
  phase_2_compat_analysis_timeout: 60s
  phase_3_conversion_timeout: 120s
  phase_4_artifact_generation_timeout: 30s

  on_timeout:
    action: "return_partial_results"
    log: "Phase timeout reached, returning partial results"
    notify_user: "Function porting incomplete"
```

### Resource Limits

```yaml
resource_limits:
  # Function size limits
  max_function_lines: 1000
  max_function_complexity: 50
  max_parameters: 20

  # Analysis limits
  max_dependency_depth: 10
  max_caller_analysis: 50
  max_callee_analysis: 100

  # Output limits
  max_java_function_size: 5000
  max_compat_requirements: 50
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Lines converted: {line_count}"

  final_summary:
    - "Function porting complete"
    - "Total duration: {total_duration}s"
    - "Lines converted: {line_count}"
    - "Compat gaps: {gap_count}"
    - "Dependencies resolved: {dep_count}"
```

## Error Handling & Fallback Strategy

### Preflight Checks

```yaml
preflight:
  - check: "function_validation"
    verify:
      - function_exists
      - function_accessible
      - function_signature_parsable
    action_on_failure: "abort_with_error"

  - check: "target_validation"
    verify:
      - target_file_writable
      - package_structure_valid
    action_on_failure: "abort_with_error"

  - check: "mcp_capability_check"
    graph_mcp_functions:
      - explore_graph
      - search_functions
      - trace_flow
      - plan_function_dependency_order
      - compute_scc
      - topological_sort
    action_on_failure: "fallback_to_basic_analysis"

  - check: "dependency_check"
    verify:
      - compat_layer_accessible
      - required_dependencies_resolved
    action_on_failure: "flag_unresolved_dependencies"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  basic_analysis_mode:
    mode: "static_analysis_only"

    steps:
      1. Skip MCP dependency tracing
      2. Use basic parsing for function extraction
      3. Analyze only explicit dependencies in function body
      4. Mark all implicit dependencies for manual review
      5. Add disclaimer about incomplete analysis

    notification:
      - "⚠️ Dependency analysis unavailable"
      - "Using basic static analysis"
      - "Dependencies may be incomplete"

  recovery:
    auto_retry: 1
    retry_delay: 5s
    max_retry_time: 15s
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_1_discovery:
    on_function_too_complex:
      action: "split_into_smaller_functions"
      log: "Function too complex, recommending split"
      add_warning: true
      continue: false
    on_extraction_failure:
      action: "manual_extraction_required"
      log: "Automatic extraction failed"
      continue: false

  phase_2_compat_analysis:
    on_incomplete_gap_analysis:
      action: "mark_gaps_for_manual_review"
      log: "Incomplete gap analysis"
      add_warning: true
      continue: true

  phase_3_conversion:
    on_conversion_failure:
      action: "create_manual_conversion_task"
      log: "Automatic conversion failed"
      add_warning: true
      continue: true
    on_type_conversion_error:
      action: "use_object_type_and_flag"
      log: "Type conversion error, using Object type"
      add_warning: true
      continue: true

  phase_4_artifact_generation:
    on_artifact_failure:
      action: "create_minimal_artifacts"
      log: "Artifact generation failed, creating minimal set"
      continue: true
```

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  function_analysis:
    - functions_analyzed
    - total_lines_analyzed
    - average_complexity
    - high_complexity_functions

  conversion_progress:
    - functions_converted
    - lines_converted
    - conversion_success_rate
    - conversion_errors

  compatibility_analysis:
    - total_compat_gaps
    - critical_gaps
    - wrapper_needed
    - manual_review_needed

  dependency_analysis:
    - total_dependencies
    - resolved_dependencies
    - unresolved_dependencies
    - circular_dependencies
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

  log_conversion_decisions:
    - type_conversion: "Type mapping decisions"
    - control_flow_conversion: "Control flow changes"
    - memory_semantics: "Memory to reference conversion"
    - compat_usage: "Compatibility layer usage"

  log_redactions:
    - redaction_type: "STRING_LITERAL|PASSWORD|etc"
    - count: "number_of_redactions"
    - source: "function_body"
```

## Non-Negotiable 1:1 Rules

- Preserve function name exactly
- Preserve parameter names exactly
- Preserve output file/package path parity
- Convert syntax and types only unless behavior fix is explicitly approved

## Workflow

### Phase 1: Function Discovery

1. Extract exact signature, parameters, return type, and body
2. Capture callers/callees and side effects
3. Load planner wave/dependency context for this function (if present)
4. Record complexity and risk points

### Phase 2: Compatibility Gap Analysis

1. Identify unsupported language/library patterns
2. Map each gap to compat-layer bridge or Java-native equivalent
3. Record unresolved gaps for manual review

### Phase 3: Function Conversion

1. Convert control flow and expressions to Java syntax
2. Convert memory/pointer semantics to safe Java references
3. Keep symbol names unchanged
4. Add minimal TODO markers only for unresolved dependencies

### Phase 4: Artifact and Task Generation

1. Create dependency-ordered function task list
2. Align function task order with planner wave order when provided
3. Produce compat requirement checklist
4. Save outputs to function task folder

## Output Contract

Create `tasks/porting_<function_name>/` with:

- `function-porting-tasks.md`
- `source-function.json`
- `<exact_package_path>/<exact_filename>.java`
- `compat-requirements.md`

## Guardrails

- Do not introduce broad refactors in function-porting phase
- Keep migration incremental and verifiable
- Mark behavior uncertainty explicitly

## Non-Negotiable Rules

- ✅ Always validate inputs before processing (security)
- ✅ Always redact sensitive data in function metadata (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always preserve 1:1 name mapping for traceability
- ✅ Never refactor during function conversion
- ✅ Never change function signatures without explicit approval
- ✅ Never skip dependency analysis

## Version History & Changelog

### Version 2.0.0 (2026-04-29)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration with specific limits
- Enhanced fallback strategy with basic analysis mode

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
- Improved function conversion with fallback modes

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on analysis errors)
- Fixed: No progress feedback (poor UX for complex functions)
- Fixed: No observability (hard to track conversion progress)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update error handling if custom workflows exist

### Version 1.0.0 (Initial Release)

- Initial workflow for C++ to Java function porting
- Basic 1:1 name preservation and conversion
- Four-phase workflow (Discovery, Compatibility, Conversion, Artifacts)
- Basic dependency and impact analysis

## Known Limitations

```yaml
limitations:
  conversion_dependent:
    - "Requires parseable C++ function code"
    - "Template functions may confuse conversion"
    - "Macro-heavy code may require manual conversion"

  analysis_scope:
    - "Only analyzes single function at a time"
    - "Cannot resolve all runtime dependencies statically"
    - "Virtual function calls need manual verification"

  language_support:
    - "Best support for C++ to Java"
    - "Function pointers need functional interface design"
    - "Operator overloading needs special handling"

  compatibility:
    - "Cannot automatically resolve all compatibility gaps"
    - "Memory management patterns require careful conversion"
    - "Exception handling needs manual mapping"
```
