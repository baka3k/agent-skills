---
name: cpp-java-file-structure-porting
description: Port a single C++ file into Java skeleton form with strict 1-to-1 mapping of package/path/file/class/function/parameter names, plus dependency-aware task breakdown and compatibility requirements with comprehensive security hardening, operational resilience, and evidence-based porting.
version: 2.1.0
last_updated: 2026-04-29
---

# C++ to Java File-Structure Porting

Use this skill to generate a Java skeleton for one source file before deep function implementation.

## When To Use

- You need class/interface/function skeletons for one file
- You need strict structure parity for easier diff and verification
- You want a task list before function-by-function conversion

## Avoid Using When

- File is trivial (less than 50 lines)
- You need immediate full implementation, not skeleton
- Target language is not Java
- Source file is not C++

## Required Inputs

- Source language: C++
- Target language: Java
- Source file path
- Source root and target root
- `migration-worklist.json` wave context for this file (recommended)

## Input Validation & Security

### Path Validation

- **Source file path**: Must exist, be within source root, and be readable
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **File extension validation**: Must be valid C++ source files
- **Access verification**: Verify read access before analysis

**Validation rules**:
```yaml
path_validation:
  - source_file must exist: os.path.exists(file_path)
  - source_file must be readable: os.access(file_path, os.R_OK)
  - source_file must have valid extension: [".cpp", ".cc", ".cxx", ".h", ".hpp"]
  - Block path traversal: reject if contains "../" or absolute path
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max path length: 1000 characters
  - Max file size: 10MB
```

### Target Root Validation

- **Target root**: Must exist and be writable
- **Package structure**: Must follow Java package conventions
- **File conflicts**: Check for existing files

**Validation rules**:
```yaml
target_validation:
  - target_root must exist: os.path.exists(target_root)
  - target_root must be writable: os.access(target_root, os.W_OK)
  - Package paths must be valid: /^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$/
  - Check for file conflicts before writing
```

### Sensitive Data Redaction

When extracting C++ code structure that may contain sensitive information:

**Redaction patterns**:
```regex
# Credentials in string literals
String literals:  /password\s*=\s*"[^"]*"/gi → 'password = "[REDACTED]"'
API keys in code:  /api_key\s*=\s*"[^"]*"/gi → 'api_key = "[REDACTED]"'
Connection strings:  /jdbc:[^\s"]*/gi → 'jdbc://[REDACTED]'
```

**Logging redaction**:
```yaml
logging_redaction:
  - Redact sensitive literals in extracted metadata
  - Never log original sensitive data in source-skeleton.json
  - Store only redacted structure information
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # Analysis timeouts
  skeleton_extraction_timeout: 180s
  java_generation_timeout: 120s
  compat_analysis_timeout: 90s
  task_breakdown_timeout: 60s

  # Phase timeouts
  phase_1_extraction_timeout: 180s
  phase_2_generation_timeout: 120s
  phase_3_compat_analysis_timeout: 90s
  phase_4_task_breakdown_timeout: 60s

  on_timeout:
    action: "return_partial_results"
    log: "Phase timeout reached, returning partial results"
    notify_user: "File structure analysis incomplete"
```

### Resource Limits

```yaml
resource_limits:
  # File size limits
  max_source_file_size: 10MB

  # Analysis limits
  max_classes_per_file: 100
  max_functions_per_file: 500
  max_methods_per_class: 200

  # Output limits
  max_java_file_size: 50MB
  max_compat_requirements: 1000
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Classes extracted: {class_count}"
    - "  Methods extracted: {method_count}"

  final_summary:
    - "File structure porting complete"
    - "Total duration: {total_duration}s"
    - "Classes created: {class_count}"
    - "Methods created: {method_count}"
    - "Compat gaps: {gap_count}"
    - "Tasks generated: {task_count}"
```

## Error Handling & Fallback Strategy

### Preflight Checks

```yaml
preflight:
  - check: "source_file_validation"
    verify:
      - source_file_exists
      - source_file_readable
      - source_file_valid_cpp
    action_on_failure: "abort_with_error"

  - check: "target_root_validation"
    verify:
      - target_root_exists
      - target_root_writable
    action_on_failure: "abort_with_error"

  - check: "mcp_capability_check"
    graph_mcp_functions:
      - list_mcp_functions
      - explore_graph
      - search_functions
      - plan_file_dependency_order
      - compute_scc
      - topological_sort
    action_on_failure: "fallback_to_basic_parsing"

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

  basic_parsing_mode:
    mode: "regex_pattern_matching"

    steps:
      1. Skip MCP queries entirely
      2. Use regex patterns for class/function detection
      3. Use basic parsing for structure extraction
      4. Mark all complex constructs for manual review
      5. Add disclaimer about reduced accuracy

    notification:
      - "⚠️ Graph analysis unavailable"
      - "Using basic pattern matching"
      - "Structure may be incomplete"

  recovery:
    auto_retry: 1
    retry_delay: 5s
    max_retry_time: 15s
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_1_extraction:
    on_file_too_large:
      action: "split_and_analyze"
      log: "File too large, splitting analysis"
      continue: true
    on_parsing_failure:
      action: "fallback_to_basic_extraction"
      log: "Advanced parsing failed, using basic extraction"
      continue: true

  phase_2_generation:
    on_package_conflict:
      action: "rename_with_suffix"
      log: "Package conflict detected, adding suffix"
      add_warning: true
      continue: true
    on_java_generation_failure:
      action: "create_manual_task"
      log: "Java generation failed, creating manual task"
      continue: true

  phase_3_compat_analysis:
    on_incomplete_analysis:
      action: "mark_for_manual_review"
      log: "Incomplete compatibility analysis"
      add_warning: true
      continue: true

  phase_4_task_breakdown:
    on_dependency_analysis_failure:
      action: "create_linear_task_list"
      log: "Dependency analysis failed, using linear order"
      continue: true
```

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  structure_extraction:
    - classes_found
    - interfaces_found
    - enums_found
    - methods_extracted
    - fields_extracted

  generation_progress:
    - java_files_created
    - packages_created
    - lines_generated
    - compilation_errors

  compatibility_analysis:
    - total_compat_gaps
    - critical_gaps
    - wrapper_needed
    - manual_review_needed

  task_generation:
    - total_tasks_created
    - high_priority_tasks
    - medium_priority_tasks
    - low_priority_tasks
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

  log_structure_decisions:
    - class_mapping: "C++ class to Java class mapping"
    - method_signature: "Method signature conversion"
    - type_conversion: "Type mapping decisions"
    - package_structure: "Package structure decisions"

  log_redactions:
    - redaction_type: "STRING_LITERAL|PASSWORD|etc"
    - count: "number_of_redactions"
    - source: "source_file"
```

## Non-Negotiable 1:1 Rules

- Keep package/folder structure exactly the same as source hierarchy
- Keep output filename exactly the same base name (only extension changes)
- Keep class names exactly the same
- Keep function names exactly the same
- Keep parameter names exactly the same
- Only convert types/syntax

## Workflow

### Phase 1: Extract Source Skeleton

1. Locate all classes, methods, signatures, and key macros/constants
2. Capture metadata into `source-skeleton.json`
3. Read planner wave/dependency context for this file (if present)
4. Build dependency and impact notes for downstream function porting

### Phase 2: Generate Target Skeleton

1. Create Java file at mirrored package path
2. Generate class/enum/interface skeletons
3. Generate method stubs with exact names/parameters
4. Convert only type annotations and Java syntax

### Phase 3: Compatibility and Gap Notes

1. Identify unsupported constructs requiring compat layer
2. Mark required wrappers/bridges in `compat-requirements.md`
3. Mark unresolved constructs for manual review

### Phase 4: Task Breakdown

1. Produce ordered implementation tasks by dependency
2. Align task order with planner wave order when provided
3. Include risk tags and suggested test focus
4. Save as `file-porting-tasks.md`

## Output Contract

Create `tasks/porting_<filename>/` with:

- `file-porting-tasks.md`
- `source-skeleton.json`
- `<exact_package_path>/<exact_source_filename>.java`
- `compat-requirements.md`

## Guardrails

- Do not rename symbols for style
- Do not mix structural skeleton generation with behavioral refactor
- Preserve traceability to source line/symbol origins

## Non-Negotiable Rules

- ✅ Always validate inputs before processing (security)
- ✅ Always redact sensitive data in extracted metadata (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always preserve 1:1 name mapping for traceability
- ✅ Never rename symbols during skeleton generation
- ✅ Never mix structural generation with behavioral changes
- ✅ Never skip compatibility analysis

## Version History & Changelog

### Version 2.0.0 (2026-04-29)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration with specific limits
- Enhanced fallback strategy with basic parsing mode

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
- Improved structure extraction with fallback modes

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on parsing errors)
- Fixed: No progress feedback (poor UX for large files)
- Fixed: No observability (hard to track porting progress)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update error handling if custom workflows exist

### Version 1.0.0 (Initial Release)

- Initial workflow for C++ to Java file structure porting
- Basic skeleton generation with 1:1 name mapping
- Four-phase workflow (Extraction, Generation, Compatibility, Tasks)
- Basic compatibility requirements identification

## Known Limitations

```yaml
limitations:
  parsing_dependent:
    - "Requires parseable C++ code"
    - "Template metaprogramming may confuse structure extraction"
    - "Macro-heavy code may require manual analysis"

  analysis_scope:
    - "Only analyzes single file at a time"
    - "Cannot resolve external dependencies without source code"
    - "Cross-file references need manual verification"

  language_support:
    - "Best support for C++ to Java"
    - "Multiple inheritance requires manual interface design"
    - "Operator overloading needs special handling"

  compatibility:
    - "Cannot automatically design all compatibility layers"
    - "Complex runtime patterns require manual analysis"
    - "Platform-specific code needs per-platform handling"
```
