---
name: hi-scenario
description: Generate comprehensive edge cases and test scenarios by decomposing features across 12 dimensions (user types, input extremes, timing, scale, state, environment, errors, authorization, data integrity, integration, compliance, business logic). Uses mind_mcp for feature requirements context and graph_mcp for code path discovery. Use before implementation, during code review, or when planning test coverage.
version: 1.0.0
last_updated: 2026-05-12
hooks:
  pre:
    - name: input-validation
      scope: [target_source, analysis_depth]
      enable_redaction: true
  phase:
    target_analysis:
      pre: [mcp-health-check]
      post: [progress-reporter]
    dimension_filtering:
      post: [progress-reporter]
    scenario_generation:
      post: [progress-reporter]
    severity_classification:
      post: [progress-reporter]
    report_generation:
      post: [progress-reporter]
    all_phases:
      post: [progress-reporter]
  post:
    - name: cleanup-handler
      paths: [scenario-data/]
      keep: [*.json, *.md]
---

# HI Scenario

Edge case and scenario explorer that decomposes features across 12 dimensions with MCP-assisted code path discovery and comprehensive security hardening.

## When To Use

- Before implementing complex or stateful features
- Before writing tests — generates concrete test targets
- Risk assessment during planning or code review
- API design review — surface contract edge cases early
- Refactoring critical paths — identify regression risks
- Security review — focus on auth, data integrity, error cascade dimensions
- Onboarding to unfamiliar features — understand edge behavior

## Avoid Using When

- Trivial single-line changes or cosmetic UI tweaks
- Already well-tested stable code with no recent modifications
- Pure configuration changes with no logic paths
- Simple CRUD endpoints with no business logic
- Documentation-only changes

## Required Inputs

- Target source: file path, glob pattern, or feature description
- Analysis depth: `quick` (major paths only) or `deep` (all branches)
- Optional: focus dimensions (subset of 12)
- Optional: severity threshold filter

## Input Validation & Security

### Path Validation

```yaml
path_validation:
  - target_path must exist and be readable
  - Block path traversal: reject "../" patterns
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max length: 1000 characters
```

### Depth Validation

```yaml
depth_validation:
  allowed_values: ["quick", "deep"]
  default: "quick"
  quick: "Major paths, primary dimensions only"
  deep: "All branches, all 12 dimensions"
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  phase_0_target_analysis_timeout: 120s
  phase_1_dimension_filtering_timeout: 30s
  phase_2_scenario_generation_timeout: 300s
  phase_3_severity_classification_timeout: 60s
  phase_4_report_generation_timeout: 60s

  total_workflow_timeout: 600s              # 10 minutes
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name}"
    - "  Target: {target}, Depth: {depth}"
  phase_complete:
    - "Phase {N} complete: {phase_name}"
  dimension_progress:
    - "Dimension {current}/{total}: {dimension_name}"
  final_summary:
    - "Scenario analysis complete"
    - "Dimensions: {analyzed}/{total}"
    - "Scenarios: Critical={c}, High={h}, Medium={m}, Low={l}"
    - "Total: {total} scenarios"
```

---

## The 12 Decomposition Dimensions

Not all 12 apply to every feature. Filter relevant dimensions first, then generate scenarios only for those.

| # | Dimension | What to Look For |
|---|-----------|------------------|
| 1 | **User Types** | admin, guest, banned, new user, power user, bot/scraper |
| 2 | **Input Extremes** | empty, null, max length, unicode, special chars, SQL/script injection |
| 3 | **Timing** | concurrent access, race conditions, timeout, slow network, retry storms |
| 4 | **Scale** | 0 items, 1 item, 1M items, pagination boundary, cursor wrap |
| 5 | **State Transitions** | first use, mid-flow abort, resume after crash, partial completion |
| 6 | **Environment** | mobile/low-end CPU, no JS, screen reader, proxy/VPN, different timezone/locale |
| 7 | **Error Cascades** | DB down, API timeout, disk full, OOM, network partition, partial write |
| 8 | **Authorization** | expired token, wrong role, shared/public link, CORS, CSRF, privilege escalation |
| 9 | **Data Integrity** | duplicate entries, orphan references, encoding mismatch, concurrent schema migration |
| 10 | **Integration** | webhook replay, API version mismatch, third-party outage, contract drift |
| 11 | **Compliance** | GDPR deletion request, audit logging gap, data retention, accidental PII exposure |
| 12 | **Business Logic** | edge pricing (zero/negative), coupon stacking, refund after partial delivery, free tier limits |

Full checklist per dimension: `references/dimension-checklist.md`

---

## Severity Criteria

| Level | Meaning |
|-------|---------|
| **Critical** | Data loss, security breach, auth bypass, silent corruption |
| **High** | Feature broken for a subset of users, data inconsistency |
| **Medium** | Degraded UX, recoverable error not surfaced to user |
| **Low** | Minor visual glitch, non-blocking warning |

---

## Orchestration Workflow

### Phase 0: Target Analysis (2min)

```yaml
steps:
  1. Validate target (file path or feature description)
  2. Read target source files
  3. Query graph_mcp for code structure and call paths
  4. Query mind_mcp for feature requirements context
  5. Identify entry points, state mutations, external calls
  6. Report: "Phase 0 complete: Target analyzed"

mcp_functions:
  - graph_mcp.explore_graph [optional]
    params:
      query: "{target_function_or_module}"
      limit: 50
    output:
      - nodes: related functions
      - edges: call relationships
    expected: "Code path discovery"

  - graph_mcp.trace_flow [optional]
    params:
      start_node: "{entry_point_id}"
      max_depth: 5
    output:
      - flow: execution path
    expected: "Full execution flow for scenario generation"

  - graph_mcp.find_paths [optional]
    params:
      start_node: "{entry_point_id}"
      end_node: "{error_handler_id}"
      max_paths: 10
    output:
      - paths: error handling paths
    expected: "Error cascade paths"

  - mind_mcp.hybrid_search [optional]
    params:
      query: "{feature_name} requirements use cases edge cases"
      collection: "{collection}"
      limit: 10
    output:
      - results: feature documentation
    expected: "Feature requirements and use case docs"
```

### Phase 1: Dimension Filtering (30s)

```yaml
steps:
  1. Evaluate each of 12 dimensions against target
  2. Mark dimensions as applicable or skipped
  3. Document reason for each skipped dimension
  4. Prioritize applicable dimensions by risk
  5. Report: "Phase 1 complete: {applicable}/{total} dimensions applicable"

dimension_applicability:
  user_types: "Applicable if feature has role-based behavior"
  input_extremes: "Applicable if feature accepts user input"
  timing: "Applicable if concurrent access or async operations"
  scale: "Applicable if feature processes collections"
  state_transitions: "Applicable if feature has multi-step flows"
  environment: "Applicable if feature runs in browser or client"
  error_cascades: "Always applicable for server-side code"
  authorization: "Applicable if feature has access control"
  data_integrity: "Applicable if feature writes to database"
  integration: "Applicable if feature calls external services"
  compliance: "Applicable if feature handles user data"
  business_logic: "Applicable if feature has pricing/rules"
```

### Phase 2: Scenario Generation (5min)

```yaml
steps:
  1. For each applicable dimension, generate 3-5 scenarios
  2. Use graph_mcp call paths to discover error branches
  3. Use mind_mcp requirements to validate business logic scenarios
  4. Describe expected behavior for each scenario
  5. Report: "Phase 2 complete: {count} scenarios generated"

scenario_template:
  - dimension: "Which of the 12 dimensions"
  - scenario: "Concrete description of the edge case"
  - trigger: "How to reproduce"
  - expected: "What should happen"
  - evidence: "mind_mcp | graph_mcp | filesystem"

generation_rules:
  - Each scenario must be concrete and reproducible
  - Scenario descriptions must be implementation-agnostic
  - Do not generate scenarios for skipped dimensions
  - Prioritize dimensions with highest risk first
  - Use graph_mcp flow traces to identify real error paths
```

### Phase 3: Severity Classification (1min)

```yaml
steps:
  1. Classify each scenario as Critical / High / Medium / Low
  2. Critical: data loss, security breach, auth bypass, silent corruption
  3. High: feature broken for user subset, data inconsistency
  4. Medium: degraded UX, recoverable error
  5. Low: minor visual glitch, non-blocking warning
  6. Report: "Phase 3 complete: Scenarios classified"

classification_rules:
  - Auth bypass or data exposure → always Critical
  - Unhandled errors → High or Medium based on impact
  - UI-only issues with no data impact → Low
  - Silent corruption → always Critical
```

### Phase 4: Report Generation (1min)

```yaml
steps:
  1. Aggregate scenarios by dimension and severity
  2. Format as structured table
  3. Include dimension applicability summary
  4. Add recommended test priorities
  5. Report: "Phase 4 complete: Report generated"

report_sections:
  - header: "Target, depth, timestamp"
  - dimension_summary: "Applicable vs skipped dimensions with reasons"
  - scenario_table: "#, Dimension, Scenario, Severity, Expected Behavior"
  - severity_summary: "Count by severity"
  - test_priorities: "Critical scenarios → test immediately"
```

---

## Output Contract

### Report Format

```markdown
# Scenario Report — {target}

**Date**: {timestamp}
**Depth**: {quick|deep}
**Source**: {file_path or feature_description}

## Dimensions Analyzed
{applicable_dimensions_list}

## Dimensions Skipped
| Dimension | Reason |
|-----------|--------|
| {dim} | {reason} |

## Scenarios

| # | Dimension | Scenario | Severity | Expected Behavior |
|---|-----------|----------|----------|-------------------|
| 1 | Input Extremes | Empty string for required field | High | Return 400 with field error |
| 2 | Authorization | Expired JWT on protected route | Critical | Redirect to login, clear session |
| 3 | Timing | Two users submit same form simultaneously | High | Idempotency key or 409 conflict |

## Severity Summary

| Level | Count |
|-------|-------|
| Critical | {c} |
| High | {h} |
| Medium | {m} |
| Low | {l} |
| **Total** | **{total}** |

## Test Priorities

1. **Immediate**: All Critical scenarios ({c})
2. **This sprint**: All High scenarios ({h})
3. **Backlog**: Medium/Low scenarios ({m+l})

## Evidence Sources

- mind_mcp: `{refs}`
- graph_mcp: `{node_ids}`
- filesystem: `{file_paths}`
```

---

## Non-Negotiable Rules

- ✅ Every scenario must be concrete and reproducible
- ✅ Filter dimensions before generating — do not generate noise
- ✅ Critical findings must have specific expected behavior described
- ✅ Auth bypass or data exposure always classified as Critical
- ✅ Never skip error cascades dimension for server-side code
- ✅ Provide reason for every skipped dimension
- ✅ Graph-derived scenarios must reference actual code paths

---

## Error Handling & Fallback Strategy

```yaml
preflight:
  - check: "target_validation"
    verify: [target_exists, target_readable or valid_feature_description]
    action_on_failure: "abort_with_error"

  - check: "mcp_capability_check"
    graph_mcp_functions: [explore_graph, trace_flow, find_paths]
    mind_mcp_functions: [hybrid_search]
    action_on_failure: "continue_with_filesystem_only"

fallback:
  when: "mcp_unavailable"
  mode: "manual_code_reading"
  steps:
    1. Skip MCP queries
    2. Read target files manually
    3. Derive call paths from static code analysis
    4. Skip mind_mcp business context
    5. Mark graph-derived scenarios as lower confidence

error_recovery:
  phase_0_target_analysis:
    on_mcp_timeout: "continue_with_filesystem_analysis"
  phase_2_scenario_generation:
    on_dimension_timeout: "skip_dimension_and_continue"
  phase_4_report_generation:
    on_partial_data: "generate_partial_report"
```

---

## Observability & Metrics

```yaml
metrics:
  scenario_stats:
    - total_scenarios: "all generated scenarios"
    - dimensions_analyzed: "count of applicable dimensions"
    - dimensions_skipped: "count of skipped dimensions"
    - scenarios_per_dimension_avg: "average scenarios per dimension"

  severity_distribution:
    - critical_count
    - high_count
    - medium_count
    - low_count

  evidence_coverage:
    - mcp_sourced_scenarios: "scenarios from MCP evidence"
    - filesystem_sourced_scenarios: "scenarios from manual analysis"
```

---

## Version History & Changelog

### Version 1.0.0 (2026-05-12)

**Initial Release:**
- ✅ 12-dimension edge case decomposition framework
- ✅ MCP-assisted code path discovery (graph_mcp explore/trace/find_paths)
- ✅ mind_mcp feature requirements context for business logic validation
- ✅ Severity classification (Critical/High/Medium/Low)
- ✅ Automatic dimension filtering with skip reasons
- ✅ Structured scenario report with test priorities
- ✅ MCP fallback with filesystem-only analysis
- ✅ Dimension checklist reference document

---

## Known Limitations

```yaml
limitations:
  analysis_scope:
    - "Static code analysis only — cannot simulate runtime conditions"
    - "Scenario quality depends on code path completeness from graph_mcp"
    - "Business logic scenarios limited by mind_mcp documentation quality"

  dimension_coverage:
    - "Not all 12 dimensions apply to every feature"
    - "Rare edge cases may be missed if not covered by analysis paths"
    - "Concurrent access scenarios require runtime verification"

  mcp_dependent:
    - "Deep analysis requires graph_mcp for call paths"
    - "Business context requires mind_mcp for requirements"
    - "Filesystem-only mode produces simpler scenarios"
```

---

## Deliverables

- `scenario_report_{target}_{timestamp}.md` — Full scenario report with dimension analysis

---

## References

### Skill-Specific References

- `references/dimension-checklist.md` — Detailed checklist per dimension with example scenarios
