---
name: hi-predict
description: Five expert personas independently analyze proposed changes before implementation to catch architectural, security, performance, and UX issues early. Uses mind_mcp for project context and graph_mcp for code impact analysis. Produces GO/CAUTION/STOP verdict with consensus agreements, conflict resolutions, and risk mitigations. Use before major features, refactors, or risky changes.
version: 1.0.0
last_updated: 2026-05-12
hooks:
  pre:
    - name: input-validation
      scope: [change_proposal, analysis_depth]
      enable_redaction: true
  phase:
    code_context:
      pre: [mcp-health-check]
      post: [progress-reporter]
    independent_analysis:
      post: [progress-reporter]
    consensus_debate:
      post: [progress-reporter]
    verdict:
      post: [progress-reporter]
    all_phases:
      post: [progress-reporter]
  post:
    - name: cleanup-handler
      paths: [predict-data/]
      keep: [*.json, *.md]
---

# HI Predict

Five-expert-persona pre-analysis that debates proposed changes using MCP-assisted code context before any code is written.

## When To Use

- Before implementing a major or high-risk feature
- Before a significant refactor or architecture change
- Evaluating competing technical approaches
- Stress-testing assumptions in a proposed design
- Gate check before committing to implementation

## When NOT to Use

- Trivial or low-risk changes (single file, known pattern)
- Already-approved work with no open design questions
- Pure dependency upgrades with no API changes
- Documentation-only changes

## Required Inputs

- Change proposal or feature description
- Optional: file paths to analyze (`--files <glob>`)
- Optional: specific concern areas to focus on
- Analysis depth: `quick` or `deep`

## The 5 Personas

| Persona | Focus | Core Questions |
|---------|-------|----------------|
| **Architect** | System design, scalability, coupling | Does this fit the architecture? Will it scale? What new coupling does it introduce? |
| **Security** | Attack surface, data protection, auth | What can be abused? Where is data exposed? Are auth boundaries respected? |
| **Performance** | Latency, memory, queries, resource usage | What is the latency impact? N+1 queries? Memory leaks? Resource contention? |
| **UX** | User experience, accessibility, error states | Is this intuitive? What does the error state look like? Accessible on all devices? |
| **Devil's Advocate** | Hidden assumptions, simpler alternatives | Why not do nothing? What is the simplest alternative? Which assumption could be wrong? |

## Input Validation & Security

```yaml
proposal_validation:
  - proposal must be non-empty, 10-5000 characters
  - reject proposals containing only code (must be described in natural language)

depth_validation:
  allowed_values: ["quick", "deep"]
  default: "quick"
```

## Performance & Operational Configuration

```yaml
timeouts:
  phase_0_code_context_timeout: 180s
  phase_1_independent_analysis_timeout: 300s
  phase_2_consensus_debate_timeout: 180s
  phase_3_verdict_timeout: 60s

  total_workflow_timeout: 720s             # 12 minutes

progress_reporting:
  phase_start: "Phase {N} started: {phase_name}"
  persona_progress: "Persona {name} analyzing..."
  conflict_resolving: "Resolving conflict: {topic} ({architect} vs {security})"
  final_summary: "Verdict: {GO|CAUTION|STOP} — {agreement_count} agreements, {conflict_count} conflicts resolved"
```

---

## Verdict Levels

| Verdict | Meaning |
|---------|---------|
| **GO** | All personas aligned, no critical risks, proceed with confidence |
| **CAUTION** | Concerns exist but manageable — mitigations identified, proceed carefully |
| **STOP** | Critical unresolved issue found — redesign or more information needed |

### STOP Triggers (any one is sufficient)

- Security persona identifies auth bypass or data exposure with no viable mitigation
- Architect identifies fundamental design incompatibility requiring significant rework
- Performance persona identifies unacceptable latency or query explosion with no workaround
- Devil's Advocate exposes a false assumption that invalidates the entire approach

---

## Orchestration Workflow

### Phase 0: Code Context Gathering (3min)

```yaml
steps:
  1. Parse change proposal and file scope
  2. Query mind_mcp for architecture docs and patterns
  3. Query graph_mcp for affected code areas and dependencies
  4. Build context package for persona analysis
  5. Report: "Phase 0 complete: Context gathered"

mcp_functions:
  - mind_mcp.hybrid_search [optional]
    params:
      query: "{proposal_keywords} architecture design"
      collection: "{collection}"
      limit: 10
    output:
      - results: relevant architecture docs
    expected: "Design patterns and architecture decisions"

  - graph_mcp.explore_graph [optional]
    params:
      query: "{affected_module_or_component}"
      limit: 50
    output:
      - nodes: affected components
      - edges: dependencies
    expected: "Code areas impacted by change"

  - graph_mcp.trace_flow [optional]
    params:
      start_node: "{entry_point_id}"
      max_depth: 5
    output:
      - flow: execution path
    expected: "Runtime flow through affected code"
```

### Phase 1: Independent Analysis (5min)

```yaml
steps:
  1. Each persona analyzes independently WITHOUT reading other personas' outputs
  2. Personas use MCP context + code reading for evidence
  3. Record findings per persona:
     - Architect: coupling, scalability, pattern fit
     - Security: attack surface, data exposure, auth gaps
     - Performance: latency, query patterns, resource usage
     - UX: user flow, error states, accessibility
     - Devil's Advocate: assumptions, alternatives, risks
  4. Report: "Phase 1 complete: {5} personas analyzed"

persona_output_format:
  architect:
    concerns: ["concern 1", "concern 2"]
    recommendations: ["action 1", "action 2"]
    confidence: "high|medium|low"

  security:
    threats: ["threat 1", "threat 2"]
    severity: "critical|high|medium|low"
    mitigations: ["mitigation 1"]

  performance:
    bottlenecks: ["bottleneck 1"]
    metrics_impact: "latency +Xms, queries +N"
    alternatives: ["alternative 1"]

  ux:
    issues: ["issue 1"]
    edge_cases: ["edge case 1"]
    a11y_concerns: ["a11y concern 1"]

  devils_advocate:
    assumptions_challenged: ["assumption 1"]
    simpler_alternatives: ["alternative 1"]
    worst_case: "description of worst case"
```

### Phase 2: Consensus Debate (3min)

```yaml
steps:
  1. Compare all persona outputs side-by-side
  2. Identify agreements — points where 4+ personas align
  3. Identify conflicts — points where personas meaningfully disagree
  4. For each conflict: weigh tradeoffs, determine resolution
  5. Document resolution with rationale
  6. Report: "Phase 2 complete: {agreements} agreements, {conflicts} conflicts resolved"

conflict_resolution_rules:
  - "Security vs Performance → Security wins unless performance makes system unusable"
  - "Architect vs UX → Defer to UX for user-facing features, Architect for backend"
  - "Devil's Advocate vs Everyone → If assumption is unvalidated, CAUTION"
  - "Any persona at Critical severity → cannot be GO"
```

### Phase 3: Verdict & Report (1min)

```yaml
steps:
  1. Synthesize all findings into consensus verdict
  2. Generate risk summary with severity and mitigation
  3. Produce actionable recommendations
  4. Format final report
  5. Report: "Phase 3 complete: Verdict={verdict}"

verdict_calculation:
  go: "0 Critical risks, <3 High risks, all mitigations clear"
  caution: "1-2 Critical mitigatable risks OR 3+ High risks"
  stop: "Any unmitigatable Critical risk OR false assumption detected"
```

---

## Output Contract

```markdown
# Prediction Report — {proposal_title}

**Date**: {timestamp}
**Depth**: {quick|deep}
**Verdict**: **GO** | **CAUTION** | **STOP**

## Executive Summary
{2-3 sentence summary of verdict and key reasoning}

## Agreements (all personas align)
- {Point 1}
- {Point 2}

## Conflicts & Resolutions

| Topic | Architect | Security | Performance | UX | Devil's Advocate | Resolution |
|-------|-----------|----------|-------------|-----|-----------------|------------|
| {topic} | {view} | {view} | {view} | {view} | {view} | {resolution} |

## Risk Summary

| Risk | Severity | Persona | Mitigation |
|------|----------|---------|------------|
| {risk} | Critical/High/Medium/Low | {persona} | {action} |

## Persona Detail

### Architect
- **Concerns**: {concerns}
- **Recommendations**: {recommendations}

### Security
- **Threats**: {threats}
- **Mitigations**: {mitigations}

### Performance
- **Bottlenecks**: {bottlenecks}
- **Impact**: {metrics}

### UX
- **Issues**: {issues}
- **Edge Cases**: {edge_cases}

### Devil's Advocate
- **Challenged Assumptions**: {assumptions}
- **Simpler Alternatives**: {alternatives}

## Recommendations
1. {Action} — {rationale}
2. {Action} — {rationale}

## Next Steps
- If GO: Proceed to implementation plan (use hi-plan)
- If CAUTION: Address mitigations before implementation
- If STOP: Redesign proposal and re-submit for prediction
```

---

## Non-Negotiable Rules

- ✅ Personas MUST analyze independently — no cross-contamination during analysis phase
- ✅ Security persona findings always weighted higher for auth/data concerns
- ✅ Devil's Advocate must challenge at least one core assumption
- ✅ STOP verdict requires explicit documentation of what must change
- ✅ Every risk must have a concrete mitigation, not just identification
- ✅ Conflict resolutions must include rationale, not just the winner

## Error Handling & Fallback Strategy

```yaml
preflight:
  - check: "proposal_validation"
    action_on_failure: "abort_with_error"

fallback:
  when: "mcp_unavailable"
  steps:
    1. Skip MCP code context
    2. Analyze proposal text only
    3. Mark code-derived findings as lower confidence
    4. Note: "MCP unavailable — code context incomplete"

error_recovery:
  phase_1_independent_analysis:
    on_persona_timeout: "mark_persona_incomplete_and_continue"
  phase_2_consensus_debate:
    on_unresolvable_conflict: "document_as_unresolved_in_report"
```

## Known Limitations

```yaml
limitations:
  analysis_scope:
    - "Static analysis only — cannot predict runtime behavior"
    - "Analysis quality depends on proposal detail"
    - "MCP-unavailable mode produces less confident results"
  persona_limitations:
    - "Personas cannot ask clarifying questions — analysis is one-pass"
    - "Business logic nuances may be missed without domain expert input"
```

## Deliverables

- `prediction_report_{timestamp}.md` — Full prediction report with all persona analyses, conflicts, verdict, and recommendations

## References

- `references/persona-playbook.md` — Detailed analysis framework per persona with example prompts
