---
name: module-summary-report
description: Synthesize module-level findings into a concise architecture summary using mind_mcp knowledge evidence and graph_mcp semantic/call-graph evidence, highlighting responsibilities, stack, build flow, platform targets, and key risks. Use after repository and tech/build scans when stakeholders need a readable, decision-focused report.
version: 2.0.0
last_updated: 2025-04-16
---

# Module Summary Report

Convert raw findings into a decision-ready summary with comprehensive security hardening, operational resilience, and evidence-based decision making.

## When To Use

- You already have recon/audit findings and need a concise decision-ready summary
- Stakeholders need module responsibilities, risks, and next actions in one report
- You need to reconcile evidence from mind_mcp and graph_mcp into a readable narrative
- You need architecture summary for technical handover or management review
- You require executive summary with actionable next steps

## Avoid Using When

- You have not produced basic module/build findings yet (use repo-recon or tech-build-audit first)
- You need deep tracing or bug impact analysis rather than synthesis
- The request is implementation work, not reporting/summarization
- You need raw detailed data instead of synthesized summary

## Required Inputs

- Module inventory output (from `repo-recon`)
- Stack/build/platform audit output (from `tech-build-audit`)
- MCP evidence artifacts or direct MCP query results
- Optional audience type: `engineering`, `management`, or `mixed`

## Input Validation & Security

### Evidence File Validation

- **Evidence files**: Must exist, be readable, and contain valid data
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **File size limits**: Prevent memory issues with large evidence files
- **Access verification**: Verify read access before processing

**Validation rules**:
```yaml
evidence_file_validation:
  - module_inventory_file must exist: os.path.exists(file_path)
  - module_inventory_file must be readable: os.access(file_path, os.R_OK)
  - module_inventory_file must be valid JSON: json.load(file)
  - tech_audit_file must exist: os.path.exists(file_path)
  - tech_audit_file must be readable: os.access(file_path, os.R_OK)
  - tech_audit_file must be valid JSON: json.load(file)
  - Block path traversal: reject if contains "../" or absolute path
  - Max file size: 50MB per evidence file
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max path length: 10000 characters
```

### Audience Type Validation

- **Audience type**: Must be valid audience for report tailoring
- **Depth preference**: Must be one of `executive`, `standard`, or `detailed`

**Validation rules**:
```yaml
audience_validation:
  allowed_values: ["engineering", "management", "mixed"]
  default: "mixed"
  engineering: "Full technical details with code references"
  management: "High-level summary with business impact focus"
  mixed: "Balanced technical and business summary"

depth_validation:
  allowed_values: ["executive", "standard", "detailed"]
  default: "standard"
  executive_depth: "1 page executive summary only"
  standard_depth: "2-4 pages with module summaries and top risks"
  detailed_depth: "Full technical summary with call flows and detailed evidence"
```

### Sensitive Data Redaction

When synthesizing reports from evidence that may contain sensitive information:

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

# Cloud Keys
AWS keys:           /\bAKIA[0-9A-Z]{16}\b/g → '[REDACTED_AWS_KEY]'
GCP keys:           /\b[0-9a-f]{32}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi → '[REDACTED_GCP_KEY]'
Azure keys:         /\b[0-9a-zA-Z+/]{86,}=*\b/g → '[REDACTED_AZURE_KEY]'

# Personal Data
Email addresses:    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED_EMAIL]'
Phone numbers:      /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g → '[REDACTED_PHONE]'
```

**Report redaction**:
```yaml
logging_redaction:
  - Log all redactions: "Redacted {count} API keys from report"
  - Never log original sensitive data
  - Store only redacted evidence in reports
  - Apply redaction before writing to output files

evidence_redaction:
  - "Apply redaction to all evidence citations"
  - "Apply redaction to code snippets in report"
  - "Apply redaction to configuration examples"
  - "Apply redaction to build command examples"
```

### Access Boundaries

- **Evidence file scope**: Limit reading to specified evidence files only
- **Report output scope**: Write only to specified output directory
- **MCP access**: Only access collections/databases user is authorized to access
- **Network restrictions**: No external network calls during report generation (except to MCP servers)

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # MCP call timeouts
  mcp_call_timeout: 30s
  query_timeout: 45s
  batch_timeout: 60s

  # Report generation timeouts
  evidence_consolidation_timeout: 180s
  module_summary_timeout: 300s
  narrative_composition_timeout: 240s
  final_output_timeout: 120s

  # Phase timeouts
  phase_0_preflight_timeout: 30s
  phase_1_consolidation_timeout: 180s
  phase_2_summaries_timeout: 300s
  phase_3_narrative_timeout: 240s
  phase_4_output_timeout: 120s

  # Total workflow timeout
  total_workflow_timeout: 900s  # 15 minutes
```

### Resource Limits

```yaml
resource_limits:
  # Evidence file limits
  max_evidence_file_size: 50MB
  max_total_evidence_size: 200MB
  max_modules_to_summarize: 100
  max_risks_to_report: 50

  # Report output limits
  max_report_size: 5MB
  max_module_summaries: 50
  max_call_flows: 20
  max_next_steps: 10
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"
    - "  Audience: {audience_type}"
    - "  Depth: {depth_preference}"
    - "  Modules: {module_count}"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Results: {results_summary}"

  task_progress:
    - "Consolidating evidence: {current}/{total} items"
    - "Writing module summaries: {current}/{total} modules"
    - "Composing narrative: {section_count} sections"
    - "Generating report: {page_count} pages"

  final_summary:
    - "Module summary report complete"
    - "Total duration: {total_duration}s"
    - "Modules summarized: {module_count}"
    - "Risks identified: {risk_count}"
    - "Next steps recommended: {step_count}"
```

### Caching Strategy

```yaml
cache:
  consolidated_evidence_cache:
    enabled: true
    ttl: 1200  # 20 minutes
    file: "consolidated_evidence_cache.json"
    cache_content:
      - mind_mcp_evidence
      - graph_mcp_evidence
      - filesystem_evidence
    invalidation: "on_evidence_change"

  module_summary_cache:
    enabled: true
    ttl: 1800  # 30 minutes
    file: "module_summary_cache.json"
    cache_content:
      - module_summaries
      - risk_assessments
      - dependency_maps
    invalidation: "on_evidence_change"

  narrative_cache:
    enabled: true
    ttl: 2400  # 40 minutes
    file: "narrative_cache.json"
    cache_content:
      - system_narrative
      - call_flow_summaries
      - risk_descriptions
    invalidation: "on_report_generation"
```

## Error Handling & Fallback Strategy

### Preflight Checks

Before starting report generation:

```yaml
preflight:
  - check: "evidence_file_validation"
    verify:
      - module_inventory_file_exists
      - module_inventory_file_readable
      - module_inventory_file_valid_json
      - tech_audit_file_exists
      - tech_audit_file_readable
      - tech_audit_file_valid_json
    action_on_failure: "abort_with_error"

  - check: "audience_validation"
    verify:
      - audience_type_is_valid
      - depth_preference_is_valid
    action_on_failure: "use_default_settings"

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
    action_on_failure: "use_evidence_files_only"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_evidence_files_provided"

  evidence_files_only_mode:
    mode: "synthesize_from_existing_evidence"

    steps:
      1. Skip direct MCP queries
      2. Use provided module inventory and tech audit files
      3. Extract evidence from MCP evidence artifacts if available
      4. Synthesize report from existing evidence only
      5. Mark report as based on existing evidence
      6. Add disclaimer if evidence is incomplete

    logging:
      - "Running in EVIDENCE-ONLY MODE: MCP unavailable or evidence files provided"
      - "Synthesizing report from existing evidence files"
      - "Report quality depends on evidence file quality"

  recovery:
    auto_retry: 1
    retry_delay: 10s
    backoff_multiplier: 1.0
    max_retry_time: 30s
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_0_preflight:
    on_evidence_missing:
      action: "abort_with_error"
      log: "Required evidence files missing, aborting"

  phase_1_consolidation:
    on_evidence_parse_error:
      action: "skip_problematic_evidence"
      log: "Evidence file parse error, skipping problematic evidence"
      continue: true
    on_mcp_timeout:
      action: "use_cached_or_empty"
      log: "MCP timeout during consolidation, using cached or empty evidence"
      continue: true

  phase_2_summaries:
    on_module_summary_timeout:
      action: "return_partial_summaries"
      log: "Module summary generation timeout, returning partial summaries"
      continue: true

  phase_3_narrative:
    on_narrative_timeout:
      action: "use_basic_narrative"
      log: "Narrative composition timeout, using basic summary"
      continue: true

  phase_4_output:
    on_report_generation_failure:
      action: "fallback_to_json_output"
      log: "Markdown report generation failed, using JSON output"
      continue: true
```

## Conflict Resolution Rules

When evidence sources conflict during report generation:

```yaml
conflict_resolution:
  priority_rules:
    1. "For current implementation: Trust graph_mcp over mind_mcp"
       - Example: Module exists in code but not docs → Use code
      - Example: Actual dependencies vs documented → Use code

    2. "For architectural intent: Trust mind_mcp over graph_mcp"
       - Example: Module purpose and design intent → Use docs
      - Example: Business requirements → Use docs

    3. "For build/platform configuration: Trust filesystem over MCP"
       - Example: Build commands in files vs docs → Use files
      - Example: CI/CD configs → Use actual configs

    4. "For recent changes: Trust filesystem over MCP"
       - Example: Recent changes not yet in MCP → Use files

    5. "For historical context: Trust mind_mcp (archival knowledge)"
       - Example: Why architecture decisions were made → Use docs

  documentation_conflicts:
    when: "docs and code disagree"
    rules:
      - "Treat graph_mcp as current implementation truth"
      - "Mark mind_mcp statement as stale candidate"
      - "Add explicit action item to reconcile documentation"

  logging:
    log_all_conflicts: true
    include_in_report: true
    severity_levels: ["RESOLVED_BY_PRIORITY", "DOCUMENTATION_STALE", "MANUAL_VERIFICATION_NEEDED"]
```

## Workflow

### Phase 0: Preflight and Evidence Validation (30s timeout)

```yaml
steps:
  1. Validate evidence files (module inventory, tech audit)
  2. Validate audience type and depth preference
  3. Check MCP capabilities (if direct MCP access planned)
  4. Initialize shared evidence map
  5. Configure timeouts, limits, and caching
  6. Report: "Preflight complete, starting report generation"

shared_context:
  module_inventory: "{inventory_data}"
  tech_audit: "{audit_data}"
  audience_type: "{engineering|management|mixed}"
  depth_preference: "{executive|standard|detailed}"
  consolidated_evidence: {}

on_failure: "abort or use evidence_files_only"
```

### Phase 1: Consolidate MCP Facts and Assumptions (180s timeout)

```yaml
steps:
  1. Read knowledge/context evidence from mind_mcp (or artifacts)
  2. Read semantic and flow evidence from graph_mcp (or artifacts)
  3. Separate confirmed evidence from inferred conclusions
  4. Do not merge uncertain hypotheses into facts
  5. Apply sensitive data redaction to all evidence
  6. Cache consolidated evidence
  7. Report progress: "Phase 1 complete: {count} evidence items consolidated"

mcp_functions (if direct access):
  - hybrid_search [optional]
    params:
      query: "{architecture OR module OR responsibility}"
      collection: "{selected_collection}"
      limit: 20
    output:
      - results: architecture and module documentation
    expected: "Module intent and design documentation"

  - get_paragraph_text [optional]
    params:
      paragraph_ids: ["{ids_from_search}"]
    output:
      - text: detailed content (redacted)
    expected: "Detailed module descriptions"

  - explore_graph [optional]
    params:
      query: "{module_name}"
      limit: 50
    output:
      - nodes: module structure
    expected: "Module code structure"

cache_output:
  file: "consolidated_evidence_cache.json"
  content:
    timestamp: "{ISO8601}"
    evidence_items:
      - id: unique_id
        type: mind_mcp | graph_mcp | filesystem
        category: architecture | module | dependency | risk
        content: summarized content (redacted)
        confidence: high | medium | low

fallback:
  on_mcp_unavailable: "Use evidence files only (module inventory + tech audit)"
  on_timeout: "Return partial consolidation, continue with available evidence"
```

### Phase 2: Write Evidence-Backed Module Summaries (300s timeout)

```yaml
steps:
  1. For each major module from inventory, include:
  2. purpose (from mind_mcp or inferred)
  3. key responsibilities (from graph_mcp or inferred)
  4. inbound/outbound dependencies (from graph_mcp)
  5. main technologies (from tech audit)
  6. risk level (assessed from evidence)
  7. evidence references (mind_mcp and/or graph_mcp)
  8. Cache module summaries
  9. Report progress: "Phase 2 complete: {count} module summaries written"

per_module_summary:
  required_fields:
    - name: string (from inventory)
    - purpose: string (from mind_mcp or inferred from code)
    - key_responsibilities: [] (from mind_mcp or graph_mcp)
    - inbound_dependencies: [] (from graph_mcp)
    - outbound_dependencies: [] (from graph_mcp)
    - main_technologies: [] (from tech audit)
    - risk_level: low | medium | high (assessed)
    - evidence_references: [] (all sources)
    - confidence: high | medium | low

  evidence_requirements:
    mind_mcp:
      - "At least one knowledge-level signal preferred"
      - "Module purpose and design intent"
      - "Business requirements and domain context"

    graph_mcp:
      - "At least one code-level signal when available"
      - "Module structure and dependencies"
      - "Call graph evidence"

    filesystem:
      - "Build and platform configuration"
      - "Package dependencies"

  confidence_rules:
    high:
      - "mind_mcp and graph_mcp agree"
      - "Multiple evidence sources confirm"
    medium:
      - "Only one evidence source"
      - "Partial disagreement between sources"
    low:
      - "Inferred from weak signal"
      - "Unresolved conflicts between sources"

cache_output:
  file: "module_summary_cache.json"
  content:
    timestamp: "{ISO8601}"
    module_summaries:
      - module_name: string
        summary: module_summary_object
        risk_assessment: string
        confidence: high | medium | low

fallback:
  on_summary_timeout: "Return partial summaries for high-priority modules"
```

### Phase 3: Compose System-Level Narrative (240s timeout)

```yaml
steps:
  1. Summarize runtime topology (services, workers, UIs, data stores)
  2. Summarize build and deployment path
  3. Explain critical call flows and cross-module coupling points
  4. Surface architectural strengths and bottlenecks
  5. Apply sensitive data redaction to all narrative
  6. Cache narrative sections
  7. Report progress: "Phase 3 complete: {section_count} narrative sections composed"

narrative_sections:
  runtime_topology:
    - "Services and their responsibilities"
    - "Workers and background jobs"
    - "UI components and frontends"
    - "Data stores and persistence layers"

  build_deployment:
    - "Build commands and processes"
    - "CI/CD pipeline locations"
    - "Deployment targets and platforms"
    - "Infrastructure tooling"

  call_flows:
    - "Critical request flows"
    - "Cross-module dependencies"
    - "Integration points"
    - "Coupling and fan-out analysis"

  strengths_bottlenecks:
    - "Architectural strengths"
    - "Performance bottlenecks"
    - "Risk areas"
    - "Technical debt indicators"

cache_output:
  file: "narrative_cache.json"
  content:
    timestamp: "{ISO8601}"
    narrative_sections:
      - section_name: string
        content: string
        evidence_references: []

fallback:
  on_narrative_timeout: "Use basic narrative from evidence summaries"
```

### Phase 4: Finalize Decision-Focused Output (120s timeout)

```yaml
steps:
  1. Use summary-template.md for consistent report format
  2. Keep output concise based on audience and depth
  3. Include all required sections
  4. Apply sensitive data redaction
  5. Generate final report
  6. Report progress: "Phase 4 complete: Report generated"

report_structure:
  executive_summary:
    engineering: "1-2 pages with technical overview"
    management: "1 page high-level summary"
    mixed: "1-2 pages balanced technical and business"

  module_summaries:
    engineering: "Full details with code references"
    management: "High-level descriptions and business impact"
    mixed: "Balanced technical and business summaries"

  technology_overview:
    - "Languages and frameworks"
    - "Data storage and persistence"
    - "Build and test commands"
    - "Platform targets and deployment"

  top_risks:
    - "Risk table with impact, evidence, and suggested direction"
    - "Prioritized by severity and likelihood"

  api_dependency_warnings:
    - "Severity, warning, location, evidence, suggested direction"
    - "From tech audit API dependency guardrails"

  recommended_next_steps:
    - "Action list limited to high-impact next steps"
    - "Prioritized by impact and effort"

  unknowns:
    - "Explicit unknowns with why it matters"
    - "Fastest validation step for each unknown"

output_lengths:
  executive:
    - "1 page equivalent"

  standard:
    - "2-4 pages equivalent"

  detailed:
    - "Full technical summary with call flows"

fallback:
  on_report_generation_failure: "Fallback to JSON output only"
```

## Output Contract

### Document Package Structure

```yaml
output_location: "<target>/module-summary/"

mandatory_outputs:
  summary_report:
    - "summary.md" - Main report following template
    - "summary.json" - Machine-readable report data

  optional_outputs:
    - "evidence_details.json" - Detailed evidence citations
    - "call_flows.json" - Call flow details
```

## Non-Negotiable Rules

- ✅ Never invent module purpose or responsibilities without evidence
- ✅ Never merge uncertain hypotheses into confirmed facts
- ✅ Always validate evidence files before processing (security)
- ✅ Always redact sensitive data before writing to report (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always cache consolidated evidence to improve efficiency (performance)
- ✅ Always include evidence source tags in every claim (traceability)
- ✅ Always mark conflicting evidence with resolution rules (consistency)

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  report_progress:
    - total_phases: "Total workflow phases"
    - completed_phases: "Completed phases"
    - current_phase: "Current phase in progress"

  module_coverage:
    - total_modules: "Total modules in inventory"
    - summarized_modules: "Modules with summaries"
    - high_confidence_modules: "Modules with high confidence"
    - low_confidence_modules: "Modules with low confidence"

  evidence_quality:
    - total_claims: "Total report claims"
    - mcp_sourced_claims: "Claims with MCP evidence"
    - mind_mcp_sourced_claims: "Claims from mind_mcp"
    - graph_mcp_sourced_claims: "Claims from graph_mcp"
    - filesystem_sourced_claims: "Claims from filesystem"
    - mcp_evidence_percentage: "MCP coverage percentage"

  risk_assessment:
    - total_risks: "Total risks identified"
    - high_risk_count: "High severity risks"
    - medium_risk_count: "Medium severity risks"
    - low_risk_count: "Low severity risks"
    - risks_with_mitigation: "Risks with suggested direction"

  report_quality:
    - report_length_pages: "Report length in pages"
    - next_steps_count: "Number of recommended next steps"
    - unknowns_count: "Number of explicit unknowns"
    - conflicts_resolved: "Number of conflicts resolved"
    - conflicts_documented: "Number of conflicts documented"

  mcp_performance:
    - mind_mcp_calls_total: "Total mind_mcp calls"
    - mind_mcp_calls_successful: "Successful mind_mcp calls"
    - mind_mcp_calls_failed: "Failed mind_mcp calls"
    - graph_mcp_calls_total: "Total graph_mcp calls"
    - graph_mcp_calls_successful: "Successful graph_mcp calls"
    - graph_mcp_calls_failed: "Failed graph_mcp calls"
    - cache_hit_rate: "Percentage of cache hits"
```

## Quality Gates

```yaml
quality_gates:
  gate_1_evidence_coverage:
    threshold: 80
    check: "modules_with_evidence / total_modules >= 80%"
    on_fail:
      action: "flag_low_evidence_modules"
      add_warning: true

  gate_2_claim_tracability:
    threshold: 100
    check: "all_key_claims_have_evidence_references"
    on_fail:
      action: "flag_unsubstantiated_claims"
      add_warning: true

  gate_3_risk_mitigation:
    check: "all_high_risks_have_mitigation"
    on_fail:
      action: "add_generic_mitigation"
      add_note: true

  gate_4_conflict_resolution:
    check: "all_conflicts_resolved_or_documented"
    on_fail:
      action: "add_manual_resolution_flag"
      add_warning: true
```

## Version History & Changelog

### Version 2.0.0 (2025-04-16)

**Breaking Changes:**
- Added mandatory evidence file validation
- Added mandatory sensitive data redaction
- Enhanced timeout configuration (was unlimited, now 15min max)
- Enhanced fallback strategy (was implicit, now explicit with rules)

**New Features:**
- ✅ Added Security & Privacy section with validation and redaction
- ✅ Added Performance & UX section with timeouts, progress feedback, caching
- ✅ Enhanced fallback strategy with evidence-files-only mode
- ✅ Added conflict resolution rules for evidence disagreements
- ✅ Added specific MCP function names with parameters and outputs
- ✅ Added observability metrics and quality gates
- ✅ Added version history and changelog

**Improvements:**
- Enhanced MCP integration with specific function names
- Added preflight checks for evidence file validation
- Enhanced error handling with specific recovery strategies per phase
- Added progress reporting after each phase
- Added conflict resolution rules with documentation staleness handling
- Added quality gates for evidence coverage and claim tracability

**Bug Fixes:**
- Fixed: No evidence file validation (could fail on bad input)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on MCP down)
- Fixed: No conflict resolution (evidence contradictions unresolved)
- Fixed: No progress feedback (poor UX for long reports)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update evidence file validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update summary template if using custom output format

### Version 1.0.0 (Initial Release)

- Initial workflow for module summary reporting
- Basic MCP integration (mind_mcp, graph_mcp)
- Evidence-based module summaries
- System-level narrative composition
- Decision-focused report generation
- Basic quality gates and coverage metrics

## Known Limitations

```yaml
limitations:
  evidence_dependent:
    - "Requires module inventory and tech audit as inputs"
    - "Report quality depends on evidence file quality"
    - "Cannot generate report without basic evidence"

  mcp_dependent:
    - "Requires both mind_mcp and graph_mcp for full functionality"
    - "Evidence-files-only mode has reduced narrative quality"
    - "Historical context unavailable if mind_mcp is down"

  performance:
    - "Very large module inventories (>100 modules) may exceed timeouts"
    - "Deep narrative composition may timeout on large evidence sets"
    - "Detailed reports may exceed size limits"

  synthesis_scope:
    - "Only synthesizes from provided evidence"
    - "Cannot fill evidence gaps without additional analysis"
    - "Cannot verify claims beyond provided evidence"

  audience_tailoring:
    - "Best effort tailoring based on audience type"
    - "May not perfectly match stakeholder expectations"
    - "Manual review may be needed for critical audiences"
```

## Deliverables

- Executive summary (1-2 pages)
- Module summaries with evidence references
- Technology, build, and platform overview
- Critical semantic call flows
- Top risks with impact and mitigation
- API dependency warnings
- Recommended next steps
- Explicit unknowns with validation steps

## References

- `references/summary-template.md`: Canonical summary format
- `references/mcp-summary-playbook.md`: Evidence fusion rules using mind_mcp and graph_mcp
- `references/quality-gates.md`: Exit criteria and review checklist
