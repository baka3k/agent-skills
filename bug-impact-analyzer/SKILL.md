---
name: bug-impact-analyzer
description: Analyze bugs and evaluate their impact across the codebase by combining mind_mcp context knowledge with graph_mcp dependency tracing. Use when triaging bugs, assessing risk, planning fixes, or estimating regression scope.
version: 2.0.0
last_updated: 2025-04-16
---

# Bug Impact Analyzer

Derive bug impact and dependency reach from MCP evidence, then calculate risk and fix priority with comprehensive security hardening and operational resilience.

## When To Use

- Triaging production or pre-release bugs that may affect multiple modules.
- Estimating severity, reach, and regression risk before implementing a fix.
- Planning test scope and rollback strategy for risky bug fixes.
- Analyzing security vulnerabilities or data corruption issues.

## Avoid Using When

- You only need a quick local syntax/runtime fix with no dependency analysis.
- The request is feature design or architecture planning (use discovery/audit skills instead).
- There is no identifiable bug signal yet (missing error, symptom, or suspected location).

## Required Inputs

- Bug identifier or description (issue URL, error message, stack trace, or suspected location).
- Repository root path.
- Optional analysis scope: `local`, `module`, `system`, or `full`.

## Input Validation & Security

### Path Validation
- **Repository path**: Must exist, be within allowed scope, and be readable by current user
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **Path sanitization**: Remove null bytes, limit to 1000 characters, whitelist allowed characters
- **Access verification**: Verify user has read access to repository before analysis

### Bug Identifier Validation
- **Issue URLs**: Validate URL format and domain whitelist
- **Error messages**: Sanitize to remove null bytes, limit to 2000 characters
- **Stack traces**: Remove potential sensitive data before processing, limit to 10000 characters
- **File locations**: Validate paths exist and are within repository scope

### Sensitive Data Redaction
When analyzing security bugs or processing bug reports:
```regex
# Redaction patterns (apply in this order):
API keys:           /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
Passwords:          /password.*/gi → '[REDACTED_PASSWORD]'
Tokens:             /token.*/gi → '[REDACTED_TOKEN]'
Bearer tokens:      /Bearer\s+[A-Za-z0-9\-._~+/]+=*/gi → 'Bearer [REDACTED]'
Email addresses:    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED_EMAIL]'
Phone numbers:      /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g → '[REDACTED_PHONE]'
SSN:                /\b\d{3}-\d{2}-\d{4}\b/g → '[REDACTED_SSN]'
IP addresses:       /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'
```

**Logging Redaction**:
- Log all redactions in evidence trace: `"Redacted 3 API keys from bug description"`
- Never log original sensitive data
- Store only redacted evidence in output files

### Access Boundaries
- **Repository scope**: Limit analysis to specified repository path
- **Module scoping**: Respect `local`/`module`/`system`/`full` scope parameters
- **Permission checks**: Verify read access before each filesystem operation
- **Network restrictions**: No external network calls except to MCP servers

## Performance & Operational Configuration

### Timeout Configuration
```yaml
timeouts:
  mcp_call_timeout: 30s          # Per MCP function call
  query_timeout: 45s              # Per complex query
  phase_timeout: 90s              # Per workflow phase
  total_workflow_timeout: 300s    # Entire analysis (5 minutes)

  on_timeout:
    action: "return_partial_results"
    log: "Phase timeout reached, returning partial results"
    notify_user: "Analysis incomplete due to timeout. Results may be incomplete."
```

### Traversal Limits
```yaml
limits:
  max_traversal_depth: 5          # Call graph depth
  max_results_per_query: 100      # Nodes/edges returned
  max_total_nodes: 500            # Total nodes analyzed
  max_concurrent_queries: 3       # Parallel MCP calls
  batch_size: 20                  # Batch processing size
```

### Caching Strategy
```yaml
cache:
  mind_mcp_context:
    enabled: true
    ttl: 300                      # 5 minutes
    key: "repo:{repo_path}:branch:{branch}"
    invalidation: "on_workflow_start"

  graph_mcp_traces:
    enabled: true
    ttl: 600                      # 10 minutes
    key: "trace:{node_id}:depth:{depth}"
    invalidation: "on_repo_change"

  query_results:
    enabled: true
    ttl: 180                      # 3 minutes
    key: "query:{hash}"
    max_size: 1000                # Max cached queries
```

### Progress Feedback
Report progress after each phase:
```yaml
progress_reporting:
  phase_complete:
    - "Phase 1 complete: Found {count} historical context items"
    - "Phase 2 complete: Traced {count} callers, {count} dependencies"
    - "Phase 3 complete: Severity={severity}, Reach={reach_score}/10"
    - "Phase 4 complete: Fix complexity={complexity}, Regression risk={risk}"
    - "Phase 5 complete: Generated impact report"

  estimation:
    show_eta: true
    update_frequency: "per_phase"
    progress_bar: true  # For long-running operations
```

## Error Handling & Fallback Strategy

### Preflight Checks
Before starting analysis:
```yaml
preflight:
  - check: "mcp_capability_check"
    functions:
      - mind_mcp.query_knowledge_base
      - graph_mcp.find_nodes
      - graph_mcp.get_call_graph
      - graph_mcp.trace_data_flow
      - graph_mcp.find_test_coverage
    action_on_failure: "fallback_to_static_analysis"

  - check: "repository_access_check"
    verify:
      - repository_path_exists
      - repository_is_readable
      - repository_is_valid_git_repo
    action_on_failure: "abort_with_error"

  - check: "input_validation"
    validate:
      - bug_identifier_format
      - repository_path_within_scope
      - scope_parameter_valid
    action_on_failure: "sanitize_or_abort"
```

### MCP Fallback Strategy
```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  degraded_mode:
    1. Use static analysis tools:
       - grep -r "error_pattern" repository/
       - find repository/ -name "*.ext" | xargs grep "function_name"
       - ctags/gtags for symbol lookup

    2. Use manual documentation review:
       - Search README, docs/, *.md files
       - Check CHANGELOG for recent changes
       - Review test files for context

    3. Log degraded mode:
       - "Running in DEGRADED MODE: MCP unavailable"
       - "Analysis limited to static analysis only"
       - "Evidence confidence: LOW"

    4. Notify user:
       - "⚠️ MCP services unavailable. Running in degraded mode."
       - "Results may be incomplete. Consider retrying when MCP is available."
       - "Confidence levels reduced: HIGH → MEDIUM, MEDIUM → LOW"

    5. Return partial results with degraded indicators:
       - All confidence levels downgraded by one tier
       - Add "[DEGRADED MODE]" prefix to report
       - List which MCP functions failed

  recovery:
    auto_retry: 3                # Retry 3 times before fallback
    retry_delay: 5s              # Wait 5s between retries
    backoff_multiplier: 2        # Exponential backoff
```

### Error Recovery
```yaml
error_recovery:
  graph_mcp_timeout:
    action: "return_partial_traces"
    log: "Call graph trace timeout at depth {depth}, returning partial results"

  mind_mcp_unavailable:
    action: "proceed_without_historical_context"
    log: "Historical context unavailable, proceeding with current analysis only"

  conflicting_evidence:
    action: "apply_conflict_resolution_rules"  # See below
    log: "Conflict detected between mind_mcp and graph_mcp evidence"

  empty_results:
    action: "expand_search_scope"
    log: "No results found, expanding search scope and retrying"
```

## Conflict Resolution Rules

When mind_mcp and graph_mcp evidence conflicts:

```yaml
conflict_resolution:
  priority_rules:
    1. "For code structure: Trust graph_mcp over mind_mcp"
       - Example: Function exists in graph but not in docs → Use graph

    2. "For domain concepts: Trust mind_mcp over graph_mcp"
       - Example: Business rule interpretation → Use docs

    3. "For recent changes: Trust graph_mcp (current state)"
       - Example: Function signature changed → Use actual code

    4. "For historical context: Trust mind_mcp (archival knowledge)"
       - Example: Why this was implemented → Use docs/ADRs

    5. "For test coverage: Trust graph_mcp (actual tests)"
       - Example: Which functions are tested → Use test file analysis

  tiebreaker:
    when: "both sources have equal confidence but disagree"
    action: "report_both_with_disclaimer"
    format: |
      CONFLICT DETECTED:
      - mind_mcp says: {mind_mcp_claim} (confidence: {confidence})
      - graph_mcp says: {graph_mcp_claim} (confidence: {confidence})
      Resolution: Manual verification required
      Recommendation: {recommendation}

  logging:
    log_all_conflicts: true
    include_in_report: true
    severity_levels: ["RESOLVED_BY_PRIORITY", "MANUAL_VERIFICATION_NEEDED"]
```

## Workflow

### Phase 0: Preflight and Health Check (30s)
```yaml
steps:
  1. Validate all inputs (paths, bug identifiers, scope)
  2. Check MCP capabilities via preflight checks
  3. Verify repository access and permissions
  4. Configure timeouts, limits, and caching
  5. Report: "Preflight complete, starting analysis"

mcp_functions:
  - mind_mcp.get_system_status [required] - Check MCP availability
  - graph_mcp.get_database_info [required] - Verify graph DB ready

on_failure: "abort or fallback to degraded mode"
```

### Phase 1: Contextualize Bug from mind_mcp (60s)
```yaml
steps:
  1. Query knowledge base for historical context:
     - Related architectural decisions (ADRs)
     - Previous similar bugs or fixes
     - Domain concepts and business rules
     - Integration contracts and SLAs

  2. Recover procedural context:
     - Expected behavior from documentation
     - Requirements for affected features
     - Design decisions influencing bug area

  3. Cache results for 5 minutes
  4. Report progress: "Phase 1 complete: Found {count} context items"

mcp_functions:
  - mind_mcp.query_knowledge_base [required]
    params:
      query: "{bug_area} architecture decisions previous bugs"
      context: "repository:{repo_path}, branch:{branch}"
    output:
      - adr_docs: list of ADRs
      - historical_bugs: list of similar issues
      - domain_knowledge: business rules and concepts
      expected: "{count} context items retrieved"

  - mind_mcp.search_documentation [optional]
    params:
      query: "{feature_name} requirements expected behavior"
      sources: ["README", "docs/", "*.md"]
    output:
      - requirements_docs: relevant documentation
      expected: "Requirements and design docs"

fallback:
  on_mcp_unavailable: "Skip historical context, proceed with current analysis"
  on_timeout: "Return partial context, log timeout"
```

### Phase 2: Trace Impact with graph_mcp (90s)
```yaml
steps:
  1. Locate bug position:
     - Semantic search for error messages/function names
     - Find exception throwing sites
     - Locate validation functions

  2. Trace upstream callers (backward):
     - Direct callers (incoming call edges)
     - Indirect callers (reach analysis, max 5 levels)
     - API endpoints and public interfaces
     - Centrality scoring for impact prioritization

  3. Trace downstream dependencies (forward):
     - Direct dependencies (outgoing call edges)
     - Data flow paths through bug location
     - Integration points and external APIs
     - State mutation and side effects

  4. Assess test coverage:
     - Find existing tests for affected functions
     - Identify coverage gaps in impact paths
     - Mark high-reach, low-coverage areas

  5. Expand context around high-centrality nodes
  6. Report progress: "Phase 2 complete: {callers} callers, {deps} dependencies traced"

mcp_functions:
  - graph_mcp.find_nodes [required]
    params:
      search_type: "semantic|exact"
      pattern: "{error_message}|{function_name}|{class_name}"
      filters: {file_types: ["*.py", "*.js", "*.ts"]}
    output:
      - nodes: list of matching nodes with locations
      expected: "Bug location identified"

  - graph_mcp.get_call_graph [required]
    params:
      start_node: "{bug_location}"
      direction: "incoming|outgoing"
      max_depth: 5
      include_centrality: true
      limit: 100
    output:
      - callers: list of caller functions with centrality scores
      - dependencies: list of called functions
      - paths: call paths from bug to roots/leaves
      expected: "Call graph traced"

  - graph_mcp.trace_data_flow [optional]
    params:
      start_node: "{bug_location}"
      variable: "{variable_name}"
      max_depth: 3
    output:
      - data_flow_paths: variable usage and propagation
      expected: "Data flow paths identified"

  - graph_mcp.find_test_coverage [optional]
    params:
      target_functions: ["{affected_functions}"]
      test_types: ["unit", "integration", "e2e"]
    output:
      - coverage_stats: test coverage per function
      - uncovered_functions: functions lacking tests
      expected: "Test coverage assessed"

  - graph_mcp.find_integration_points [optional]
    params:
      node: "{bug_location}"
      types: ["http", "rpc", "queue", "database"]
    output:
      - integration_points: external service calls
      - api_boundaries: module boundaries crossed
      expected: "Integration points mapped"

fallback:
  on_mcp_unavailable: "Use grep/find for static analysis, limited impact assessment"
  on_timeout: "Return partial traces up to current depth, mark as incomplete"
```

### Phase 3: Classify Bug Severity and Reach (45s)
```yaml
steps:
  1. Determine severity category:
     - Critical: Data corruption, security vulnerability, complete service failure
     - High: Major feature broken, significant user impact
     - Medium: Partial feature degradation, workaround available
     - Low: Cosmetic issue, minor UX problem

  2. Calculate reach score (0-9):
     - User reach: All users (3), Most users (2), Some (1), Few (0)
     - Feature visibility: Core (3), Frequent (2), Occasional (1), Rare (0)
     - Impact breadth: System-wide (3), Multi-module (2), Single-module (1), Single-function (0)

  3. Apply risk multipliers:
     - Production-only bug ×2
     - Security-related ×2
     - Compliance/legal ×2
     - High-traffic period ×1.5
     - No monitoring ×1.5
     - Poor test coverage ×1.5
     - Complex fix ×1.5

  4. Apply risk reducers:
     - Easy workaround ×0.5
     - Behind feature flag ×0.5
     - Excellent monitoring ×0.7
     - Comprehensive tests ×0.7
     - Simple fix ×0.7

  5. Report progress: "Phase 3 complete: Severity={severity}, Reach={reach_score}/10"

mcp_functions:
  - mind_mcp.get_domain_knowledge [optional]
    params:
      domain: "{affected_business_domain}"
      concepts: ["business_rules", "sla", "compliance"]
    output:
      - domain_context: business impact assessment
      expected: "Domain context for severity justification"

  - graph_mcp.get_user_facing_surfaces [optional]
    params:
      nodes: ["{affected_functions}"]
    output:
      - api_endpoints: HTTP endpoints affected
      - public_interfaces: library APIs affected
      expected: "User-facing impact assessment"

output:
  - severity_level: Critical|High|Medium|Low
  - reach_score: 0-9
  - risk_adjusted_severity: Final severity with multipliers
  - severity_justification: Evidence-backed reasoning
```

### Phase 4: Calculate Fix Complexity (45s)
```yaml
steps:
  1. Assess code coupling:
     - Number of dependencies in impact zone
     - Cyclomatic complexity of affected functions
     - Cross-module coupling depth

  2. Estimate regression risk:
     - Test coverage quality in impact zone
     - Number of affected modules
     - Coordination requirements across teams

  3. Determine fix approach:
     - Simple fix: One-line change, well-understood (0.5-2h)
     - Medium fix: Local changes, some coordination (2-8h)
     - Complex fix: Multi-module changes, extensive testing (1-3 days)
     - Very complex: Architectural changes, cross-team effort (1-2 weeks)

  4. Report progress: "Phase 4 complete: Complexity={complexity}, Regression risk={risk}"

mcp_functions:
  - graph_mcp.analyze_complexity [optional]
    params:
      nodes: ["{affected_functions}"]
      metrics: ["cyclomatic", "coupling", "cohesion"]
    output:
      - complexity_metrics: code complexity scores
      expected: "Complexity assessment"

  - graph_mcp.get_module_inventory [optional]
    params:
      affected_nodes: ["{affected_functions}"]
    output:
      - affected_modules: list of impacted modules
      - team_ownership: module ownership information
      expected: "Coordination requirements"

output:
  - fix_complexity: Simple|Medium|Complex|Very Complex
  - estimated_effort: Time range
  - regression_risk: High|Medium|Low
  - required_coordination: Number of teams involved
```

### Phase 5: Generate Impact Report (60s)
```yaml
steps:
  1. Compile evidence from all phases
  2. Apply conflict resolution rules if needed
  3. Generate human-readable report using template
  4. Generate machine-readable impact graph
  5. Optional: Generate detailed evidence trace
  6. Optional: Generate detailed fix plan
  7. Report progress: "Phase 5 complete: Impact report generated"

output_files:
  - bug_impact_analysis.md: Human-readable report
  - bug_impact_graph.json: Machine-readable graph
  - bug_evidence_trace.md: Detailed query logs (optional)
  - bug_fix_plan.md: Implementation strategy (optional)

report_sections:
  - executive_summary: Severity, reach, recommended priority
  - bug_description: Location, type, reproduction steps
  - impact_analysis: Affected modules, dependencies, data flows
  - risk_assessment: Severity, reach, regression risk
  - fix_recommendations: Approach, complexity, test strategy, rollback
  - evidence_references: MCP queries, traces, confidence levels
```

## Output Contract

### Standard Outputs
```yaml
bug_impact_analysis.md:
  format: "Markdown"
  sections:
    - executive_summary: "3-5 lines"
    - bug_description: "Location, type, reproduction"
    - impact_analysis: "Modules, dependencies, data flows, user impact"
    - risk_assessment: "Severity with justification, reach metrics"
    - fix_recommendations: "Approach, complexity, test strategy"
    - evidence_references: "All MCP queries and confidence levels"

bug_impact_graph.json:
  format: "JSON"
  content:
    - nodes: "Affected functions/modules with metadata"
    - edges: "Call relationships and dependencies"
    - severity: "Severity scores per node"
    - confidence: "Confidence levels per node"
```

### Optional Outputs
```yaml
bug_evidence_trace.md:
  format: "Markdown"
  content:
    - mcp_queries: "All queries executed with parameters"
    - mcp_results: "Raw results from each query"
    - confidence_levels: "Confidence for each evidence item"
    - redaction_log: "What was redacted and why"

bug_fix_plan.md:
  format: "Markdown"
  content:
    - implementation_steps: "Detailed step-by-step fix plan"
    - alternative_approaches: "Multiple fix options with pros/cons"
    - test_strategy: "Unit, integration, regression tests"
    - rollback_plan: "Rollback steps and risk assessment"
    - coordination_requirements: "Cross-team dependencies"
```

## Quality Gates

### Evidence Quality
- Every impact claim **must** reference at least one MCP evidence item
- Evidence items **must** include confidence levels (High/Medium/Low)
- Conflicting evidence **must** be flagged and resolved
- Uncertain impacts **must** be explicitly flagged as "LOW confidence"

### Trace Quality
- Call graph traces **must** include depth metrics (actual depth, max depth)
- Call graph traces **must** include centrality metrics
- Traces hitting limits **must** be marked as "PARTIAL"
- Empty results **must** trigger scope expansion

### Severity Justification
- Severity classification **must** be justified by concrete reach data
- Risk multipliers **must** be documented with reasons
- Risk reducers **must** be documented with reasons
- Final severity **must** include calculation trail

### Report Completeness
- Fix recommendations **must** include test strategy
- Fix recommendations **must** include rollback considerations
- High-risk fixes **must** include coordination requirements
- Security bugs **must** include security impact assessment

## Observability & Metrics

### Metrics to Track
```yaml
metrics:
  workflow_duration:
    - phase_1_duration_seconds
    - phase_2_duration_seconds
    - phase_3_duration_seconds
    - phase_4_duration_seconds
    - phase_5_duration_seconds
    - total_workflow_duration_seconds

  evidence_quality:
    - total_evidence_items
    - high_confidence_items
    - medium_confidence_items
    - low_confidence_items
    - conflicting_evidence_count

  analysis_scope:
    - nodes_analyzed
    - edges_traversed
    - depth_reached
    - modules_impacted
    - integration_points_found

  mcp_performance:
    - mcp_calls_total
    - mcp_calls_successful
    - mcp_calls_failed
    - mcp_calls_timeout
    - mcp_cache_hit_rate
```

### Logging
```yaml
logging:
  log_level: "INFO"  # DEBUG for development, INFO for production
  log_format: "structured_json"  # For parsing and analysis

  log_all_phases:
    - phase_start: timestamp, phase_number
    - phase_complete: timestamp, phase_number, results_summary
    - phase_error: timestamp, phase_number, error_details

  log_mcp_calls:
    - function_name: "mind_mcp.query_knowledge_base"
    - params: "sanitized_params"
    - duration_ms: "call_duration"
    - success: true/false
    - cache_hit: true/false
    - result_count: "number_of_results"

  log_redactions:
    - redaction_type: "API_KEY|PASSWORD|TOKEN|etc"
    - count: "number_of_redactions"
    - source: "bug_description|error_message|stack_trace"

  log_conflicts:
    - conflict_type: "mind_vs_graph|evidence_disagreement"
    - resolution: "priority_rule|manual_verification|both_reported"
    - confidence_mind: "high|medium|low"
    - confidence_graph: "high|medium|low"
```

### Health Monitoring
```yaml
health_checks:
  mcp_health:
    endpoint: "/health/mcp"
    check_interval: 60s
    alert_on:
      - mcp_unavailable: "MCP services down for >30s"
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
      - low_confidence: "Average confidence < MEDIUM for >20min"
      - partial_results: "Partial results rate >20% for >20min"
      - conflict_rate: "Conflict rate >15% for >20min"
```

## Version History & Changelog

### Version 2.0.0 (2025-04-16)
**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction
- Enhanced timeout configuration (was unlimited, now 5min max)
- Enhanced fallback strategy (was implicit, now explicit with rules)

**New Features:**
- ✅ Added Security & Privacy section with validation and redaction
- ✅ Added Performance & UX section with timeouts, progress feedback, caching
- ✅ Added comprehensive fallback strategy with degraded mode
- ✅ Added conflict resolution rules for mind_mcp vs graph_mcp
- ✅ Added specific MCP function names with parameters and outputs
- ✅ Added observability and metrics tracking
- ✅ Added version history and changelog

**Improvements:**
- Enhanced MCP integration with specific function names
- Added preflight checks for MCP capability validation
- Enhanced error handling with specific recovery strategies
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
- Initial workflow for bug impact analysis
- Basic MCP integration (mind_mcp, graph_mcp)
- Severity classification framework
- Basic output templates

## Known Limitations

### Current Limitations
```yaml
limitations:
  mcp_dependent:
    - "Requires both mind_mcp and graph_mcp to be available"
    - "Degraded mode has reduced accuracy and confidence"
    - "Historical context unavailable if mind_mcp is down"

  performance:
    - "Large repositories (>100k files) may exceed timeouts"
    - "Deep call graphs (>10 levels) hit traversal limits"
    - "Complex dependency webs may exceed max_results limits"

  analysis_scope:
    - "Only analyzes code in specified repository"
    - "Cannot analyze external dependencies without source code"
    - "Cannot analyze runtime behavior without execution traces"

  language_support:
    - "Best support for: Python, JavaScript, TypeScript, Java, C#"
    - "Partial support for: C, C++, Go, Rust"
    - "Limited support for: Dynamic languages without type info"

  bug_types:
    - "Best for: Logic errors, API failures, data corruption"
    - "Good for: Performance issues, race conditions"
    - "Limited for: UI/UX issues, accessibility problems"
```

### TODO / Future Enhancements
```yaml
todo:
  short_term:
    - "Add machine learning for severity prediction"
    - "Add integration with issue trackers (Jira, GitHub Issues)"
    - "Add automated test generation for impacted areas"

  medium_term:
    - "Add visual impact graph rendering"
    - "Add collaborative review and commenting"
    - "Add integration with CI/CD pipelines"

  long_term:
    - "Add automated fix suggestion using AI"
    - "Add regression test auto-generation"
    - "Add cross-repository dependency analysis"
```

## Integration with Other Skills

- **tech-build-audit**: Use to understand build/deploy impact if bug affects infrastructure.
- **repo-recon**: Use if bug area is unfamiliar and needs module context.
- **module-summary-report**: Use for architectural context around bug location.
- **reverse-doc-reconstruction**: Use if bug reveals missing or outdated documentation.

## Resources

### Standard Templates

Bug Impact Analyzer uses specialized templates for impact analysis and can leverage standard testing templates:

**Skill-Specific Template**:
- `references/bug-impact-template.md`: Specialized template for bug impact analysis, including reach metrics, risk assessment, and fix recommendations

**Standard Testing Templates** (template/04_testing/):
- `tpl_bug_report.md`: Standard bug report format for initial bug documentation (reproduction steps, evidence, technical info)
- `tpl_test_case.md`: Test case template for creating regression tests
- `tpl_test_plan.md`: Test plan template for comprehensive testing strategy

**Template Usage Guide**:
- Use `tpl_bug_report.md` for initial bug documentation and reproduction
- Use `bug-impact-template.md` for impact analysis and risk assessment
- Use `tpl_test_case.md` to document regression tests from fix recommendations
- Use `tpl_test_plan.md` to create comprehensive test strategy for high-impact bugs

### Skill-Specific References

- `references/mcp-bug-playbook.md`: MCP query recipes for bug analysis
- `references/severity-matrix.md`: Bug severity classification framework
- `references/dependency-tracing-patterns.md`: Common patterns for tracing bug impact

## Support & Troubleshooting

### Common Issues

**Issue**: "MCP timeout during call graph tracing"
- **Cause**: Repository too large or bug in highly connected code
- **Solution**: Reduce `max_traversal_depth` or `max_results_per_query`
- **Workaround**: Run with `scope: local` for focused analysis

**Issue**: "Conflicting evidence from mind_mcp and graph_mcp"
- **Cause**: Documentation outdated or code recently changed
- **Solution**: Apply conflict resolution rules, prioritize graph_mcp for code structure
- **Workaround**: Manual verification of conflicting items

**Issue**: "Analysis completes but results seem incomplete"
- **Cause**: Timeout or limits hit during tracing
- **Solution**: Check for "PARTIAL" markers in evidence trace
- **Workaround**: Increase timeouts or run with broader scope

**Issue**: "Low confidence across most findings"
- **Cause**: Degraded mode or limited MCP availability
- **Solution**: Check MCP health, consider retrying when MCP is available
- **Workaround**: Supplement with manual analysis

### Getting Help
- Check evidence trace: `bug_evidence_trace.md` for detailed logs
- Review metrics in observability section for performance issues
- Consult MCP documentation for function-specific issues
- Open issue with: SKILL.md version, MCP runtime version, evidence trace attached
