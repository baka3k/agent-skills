# MCP Summary Playbook

Fuse knowledge and code evidence into one report with comprehensive security hardening, operational resilience, and evidence-based decision making.

## 1. Objective

Synthesize module-level findings into a concise architecture summary using mind_mcp knowledge evidence and graph_mcp semantic/call-graph evidence, with security hardening, performance optimization, and fallback strategies.

## 2. Evidence Inputs

### mind_mcp: Knowledge-Level Evidence

```yaml
primary_intents:
  - "Architecture intent and design decisions"
  - "Business/domain context and requirements"
  - "Process documentation and runbooks"
  - "Historical context and ADRs"

evidence_types:
  - "Architecture overview documents"
  - "Module responsibility descriptions"
  - "Service boundary definitions"
  - "Business requirements and user stories"
  - "Process flows and workflows"
```

### graph_mcp: Code-Level Evidence

```yaml
primary_intents:
  - "Semantic structure and organization"
  - "Symbol metadata and signatures"
  - "Call graph and dependencies"
  - "Path traces and execution flows"

evidence_types:
  - "Module structure and boundaries"
  - "Function/class metadata"
  - "Entry points and runtime surfaces"
  - "Call graph edges and dependencies"
  - "Integration paths and coupling"
```

### Filesystem: Configuration Evidence

```yaml
primary_intents:
  - "Manifest and package configuration"
  - "Build system configuration"
  - "CI/CD pipeline definitions"
  - "Deployment configuration"

evidence_types:
  - "package.json, pom.xml, build.gradle"
  - "Dockerfile, docker-compose.yml"
  - "GitHub Actions, GitLab CI configs"
  - "Kubernetes manifests"
```

## 3. Per-Module Evidence Rule

For each module summary, require:

```yaml
minimum_requirements:
  mind_mcp:
    - "At least one knowledge-level signal"
    - "Module purpose or design intent"
    - "Business requirements or domain context"

  graph_mcp:
    - "At least one code-level signal when available"
    - "Module structure and boundaries"
    - "Dependencies and call graph evidence"

  filesystem:
    - "Build and configuration signals"
    - "Package dependencies"

confidence_rules:
  high_confidence:
    required: "mind_mcp and graph_mcp agree"
    evidence: "Multiple independent sources confirm"

  medium_confidence:
    required: "Only one evidence source OR partial disagreement"
    evidence: "Single source OR conflicting sources with resolution"

  low_confidence:
    required: "Inferred from weak signal OR unresolved conflicts"
    evidence: "Limited evidence OR clear conflicts without resolution"

gap_handling:
  when_one_side_missing:
    action: "mark confidence as medium or low"
    required: "explain the gap explicitly"
    example: "Module purpose: [INFERRED from directory name], no documentation found"
```

## 4. Call Flow Section

### For Critical System Paths

```yaml
workflow:
  1. "Pick start nodes from entry points (list_up_entrypoint or startup symbols)"
  2. "Use find_paths, trace_flow, or query_subgraph"
  3. "Summarize the flow with trigger, modules, boundaries, and risk"

call_flow_summary:
  required_fields:
    - trigger: "What initiates the flow (HTTP request, scheduled job, etc.)"
    - modules_traversed: "List of modules involved in the flow"
    - external_boundaries: "External systems and dependencies hit"
    - observed_risk: "Risk assessment (coupling, fan-out, unclear ownership)"
    - evidence_references: "MCP evidence citations"

mcp_functions:
  graph_mcp.list_up_entrypoint [required]
    params:
      file_pattern: "**/*.{py,js,ts,java}"
      limit: 100
    output:
      - entry_points: API endpoints, main functions
    use_case: "Discover flow entry points"

  graph_mcp.find_paths [optional]
    params:
      start_node: "{entry_point_id}"
      end_node: "{target_node_id}"
      max_paths: 10
    output:
      - paths: execution paths
    use_case: "Discover alternate flow paths"

  graph_mcp.trace_flow [optional]
    params:
      start_node: "{entry_point_id}"
      max_depth: 5
    output:
      - flow: execution trace
    use_case: "Trace happy path execution"

  graph_mcp.query_subgraph [optional]
    params:
      node_id: "{key_node_id}"
      depth: 3
      limit: 50
    output:
      - subgraph: neighborhood context
    use_case: "Expand around critical nodes"

risk_assessment:
  high_risk:
    - "High fan-out (>10 downstream dependencies)"
    - "Deep call stacks (>5 levels)"
    - "Cross-module coupling without clear boundaries"
    - "Unclear ownership or responsibility"

  medium_risk:
    - "Moderate fan-out (5-10 dependencies)"
    - "Medium call stacks (3-5 levels)"
    - "Clear module boundaries with some coupling"

  low_risk:
    - "Low fan-out (<5 dependencies)"
    - "Shallow call stacks (<3 levels)"
    - "Well-defined boundaries and ownership"
```

## 5. Conflict Resolution

### When Docs and Code Disagree

```yaml
conflict_resolution_rules:
  priority_rules:
    current_implementation:
      source: "graph_mcp"
      priority: "higher than mind_mcp"
      reason: "Current code truth"
      action: "Treat as current implementation"

    architectural_intent:
      source: "mind_mcp"
      priority: "higher than graph_mcp for intent"
      reason: "Design intent and requirements"
      action: "Use for purpose and design decisions"

    build_configuration:
      source: "filesystem"
      priority: "higher than MCP"
      reason: "Actual configuration files"
      action: "Use for build and platform facts"

    recent_changes:
      source: "filesystem"
      priority: "higher than MCP"
      reason: "Changes not yet in MCP"
      action: "Use for current state"

    historical_context:
      source: "mind_mcp"
      priority: "higher for historical questions"
      reason: "Archival knowledge"
      action: "Use for why decisions were made"

  documentation_stale_handling:
    when: "mind_mcp says X, graph_mcp shows Y"
    steps:
      1. "Treat graph_mcp as current implementation truth"
      2. "Mark mind_mcp statement as stale candidate"
      3. "Add explicit action item to reconcile documentation"
      4. "Document discrepancy in report"

    example: |
      **Discrepancy Detected**:
      - Documentation (mind_mcp): "Auth service handles both login and registration"
      - Code (graph_mcp): "AuthController (login), RegistrationController (registration)"
      - Resolution: Code shows split responsibility, documentation may be stale
      - Action Item: Update auth module documentation to reflect split controllers

  logging:
    log_all_conflicts: true
    include_in_report: true
    severity_levels:
      - "RESOLVED_BY_PRIORITY: Conflicts resolved using priority rules"
      - "DOCUMENTATION_STALE: Documentation differs from implementation"
      - "MANUAL_VERIFICATION_NEEDED: Requires manual investigation"
```

## 6. Confidence Scale

```yaml
confidence_definitions:
  high:
    definition: "mind_mcp and graph_mcp agree"
    requirements:
      - "Multiple independent sources confirm"
      - "No significant conflicts"
      - "Direct evidence from both sources"
    examples:
      - "Module purpose in docs, code structure confirms"
      - "Dependencies documented and confirmed in call graph"
    reporting: "Report as fact, cite both sources"

  medium:
    definition: "only one evidence source OR partial disagreement"
    requirements:
      - "Single source with strong signal"
      - "OR conflicts resolved with priority rules"
      - "OR gaps explained and documented"
    examples:
      - "Module purpose inferred from code structure (no docs)"
      - "Dependencies from call graph only (no documentation)"
    reporting: "Report as likely, explain limitation, cite available source"

  low:
    definition: "inferred from weak signal OR unresolved conflicts"
    requirements:
      - "Weak or indirect evidence"
      - "OR significant conflicts without clear resolution"
      - "OR multiple gaps in understanding"
    examples:
      - "Module purpose inferred from directory name only"
      - "Dependencies unclear due to dynamic dispatch"
      - "Conflicting evidence without clear resolution"
    reporting: "Report as uncertain, explain gaps, suggest validation step"

confidence_reporting:
  format: "**Confidence: {HIGH|MEDIUM|LOW}** - {explanation}"
  required: "Always include confidence level with explanation"
  placement: "After each major claim or section"
```

## 7. Context Control for Large Codebases

```yaml
context_control_strategy:
  evidence_aggregation_rules:
    group_by_module: "Don't use flat lists"
    provide_summary_statistics:
      - "Total nodes processed"
      - "Coverage percentage"
      - "Confidence distribution"

    highlight_top_items:
      - "Top 10 high-risk nodes"
      - "Top 10 critical call flows"
      - "Top 10 integration points"

    link_to_details:
      - "Use node_ids for references"
      - "Not full function signatures (saves space)"
      - "Link to detailed evidence by node_id"

  batch_processing:
    rule: "Process evidence in batches of 20-50 items"
    user_confirmation: true
    prompt: "Processing {batch_size} evidence items, continue?"

  scope_by_module:
    example: |
      # Process one module at a time
      for module in ["auth", "payment", "order"]:
          consolidate_evidence(module)
          write_module_summary(module)
          # Summarize before moving to next module

  summarization_rules:
    before_reporting:
      - "Summarize graph clusters before reporting"
      - "Aggregate similar findings"
      - "Group related risks"
      - "Prioritize by impact and confidence"
```

## 8. Report Quality Assurance

### Evidence Quality Checks

```yaml
quality_checks:
  claim_tracability:
    check: "every_key_claim_links_to_explicit_evidence"
    method: "Verify evidence references in report"
    on_fail: "Add evidence reference or mark as low confidence"

  module_coverage:
    check: "each_module_has_clear_responsibility"
    method: "Review module summaries"
    on_fail: "Add responsibility statement or mark as unknown"

  risk_completeness:
    check: "risks_include_impact_and_mitigation"
    method: "Review risk table"
    on_fail: "Add impact description and suggested direction"

  unknown_handling:
    check: "unknowns_are_explicit_and_prioritized"
    method: "Review unknowns section"
    on_fail: "Add validation step or prioritize"
```

### Redaction Verification

```yaml
redaction_checks:
  sensitive_data_check:
    - "Verify no API keys in report"
    - "Verify no passwords in report"
    - "Verify no connection strings in report"
    - "Verify no cloud keys in report"
    - "Verify no personal data in report"

  code_snippet_check:
    - "Verify all code snippets are redacted"
    - "Verify all config examples are redacted"
    - "Verify all build commands are redacted"

  evidence_citation_check:
    - "Verify all evidence citations are redacted"
    - "Verify all paragraph references are redacted"
```

## 9. Integration with SKILL.md

This playbook is fully integrated with the enhanced SKILL.md (v2.0.0) and implements:

- ✅ **Security & Privacy**: Evidence file validation, sensitive data redaction
- ✅ **Performance & UX**: Timeout configuration, progress feedback, caching
- ✅ **Reliability & Resilience**: Fallback strategy, conflict resolution, error recovery
- ✅ **Observability**: Metrics tracking, quality gates, evidence provenance

For complete details, refer to:
- `<repo_root>/module-summary-report/SKILL.md`
- `<repo_root>/module-summary-report/references/summary-template.md`
