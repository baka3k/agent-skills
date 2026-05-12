---
name: hi-plan
description: Create detailed technical implementation plans by combining mind_mcp codebase knowledge with graph_mcp dependency analysis. Supports auto/fast/hard/parallel/two-approaches modes with optional red-team review and validation interviews. Use for feature planning, system design, architecture decisions, and implementation roadmaps.
version: 1.0.0
last_updated: 2026-05-12
hooks:
  pre:
    - name: mcp-health-check
      timeout: 10s
    - name: input-validation
      scope: [project_root, plan_scope]
      enable_redaction: true
  phase:
    scope_challenge:
      post: [progress-reporter]
    research:
      pre: [mcp-health-check]
      post: [progress-reporter, timeout-handler]
    codebase_analysis:
      pre: [mcp-health-check]
      post: [progress-reporter]
    solution_design:
      post: [progress-reporter]
    plan_creation:
      post: [progress-reporter]
    review:
      post: [progress-reporter]
    all_phases:
      post: [progress-reporter]
  post:
    - name: output-redaction
      apply_to: [plan_md, phase_files]
    - name: cleanup-handler
      paths: [plan-data/]
      keep: [*.json, *.md]
---

# HI Plan

Create detailed technical implementation plans with MCP-assisted codebase analysis, multi-mode support, red-team review, and comprehensive security hardening.

## When To Use

- Planning new feature implementations
- Architecting system designs or migrations
- Evaluating competing technical approaches
- Creating implementation roadmaps with phased breakdown
- Breaking down complex requirements into executable tasks
- Architecture decision records with evidence

## Avoid Using When

- Quick bug fixes with known solutions (use bug-impact-analyzer)
- Documentation-only changes
- Already-planned work with no open design questions
- Trivial single-file changes

## Required Inputs

- Project root path
- Task or feature description
- Mode: `auto`, `fast`, `hard`, `parallel`, `two-approaches`
- Optional: constraint list, preferred tech stack, deadline

## Modes

| Mode | Research | Codebase Analysis | Red Team | Validation |
|------|----------|-------------------|----------|------------|
| `auto` | Auto-detect | Auto-detect | Based on complexity | Based on complexity |
| `fast` | Skip | Minimal | Skip | Skip |
| `hard` | Deep (2 rounds) | Full MCP analysis | Yes | Optional |
| `parallel` | 2 researchers | Full MCP analysis | Yes | Optional |
| `two-approaches` | 2+ researchers | Full MCP analysis | After selection | After selection |

## Input Validation & Security

```yaml
path_validation:
  - project_path must exist and be a git repository
  - Block path traversal: reject "../" patterns
  - Max length: 1000 characters

mode_validation:
  allowed_values: ["auto", "fast", "hard", "parallel", "two-approaches"]
  default: "auto"
```

## Performance & Operational Configuration

```yaml
timeouts:
  phase_0_scope_challenge_timeout: 120s
  phase_1_research_timeout: 300s
  phase_2_codebase_analysis_timeout: 360s
  phase_3_solution_design_timeout: 300s
  phase_4_plan_creation_timeout: 240s
  phase_5_review_timeout: 180s

  total_workflow_timeout: 1800s            # 30 minutes

cache:
  codebase_cache:
    enabled: true
    ttl: 900
    file: "plan_codebase_cache.json"
    cache_content:
      - mind_mcp_architecture_docs
      - graph_mcp_module_structure
      - graph_mcp_dependency_graph
    invalidation: "on_repo_change"

progress_reporting:
  phase_start: "Phase {N} started: {phase_name}"
  phase_complete: "Phase {N} complete: {phase_name} ({duration}s)"
  final_summary: "Plan created: {plan_path} — {phase_count} phases, {risk_count} risks"
```

---

## Core Principles

- **YAGNI** — build only what's needed now
- **KISS** — simplest solution that meets requirements
- **DRY** — identify and eliminate duplication
- **Evidence-first** — decisions backed by codebase analysis, not assumptions

---

## Orchestration Workflow

### Phase 0: Scope Challenge (2min)

```yaml
steps:
  1. Validate inputs and determine complexity
  2. Auto-detect mode based on feature complexity
  3. Challenge scope: Is this really needed? What's the simplest version?
  4. Identify constraints and boundary conditions
  5. Scan existing plans for cross-dependencies
  6. Query mind_mcp for project architecture context
  7. Report: "Phase 0 complete: Mode={mode}, Complexity={level}"

complexity_detection:
  trivial: "Single file, < 50 lines change → fast mode"
  moderate: "2-5 files, new function → auto/hard mode"
  complex: "5+ files, new module, API change → hard mode"
  architectural: "Cross-module, new service, DB migration → hard/parallel mode"
```

### Phase 1: Research & Analysis (5min)

```yaml
steps:
  1. Query mind_mcp for relevant architecture docs, ADRs, standards
  2. Query graph_mcp for affected modules and dependencies
  3. Identify existing patterns and conventions in codebase
  4. Research alternatives if mode is hard/parallel/two-approaches
  5. Compile research findings with evidence citations
  6. Report: "Phase 1 complete: {findings_count} research items"

mcp_functions:
  - mind_mcp.hybrid_search [required]
    params:
      query: "{feature_name} architecture design pattern"
      collection: "{collection}"
      limit: 15
    output:
      - results: relevant architecture docs
    expected: "Architecture decisions and design patterns"

  - mind_mcp.get_paragraph_text [required]
    params:
      paragraph_ids: ["{ids}"]
    output:
      - text: full content with citations
    expected: "Detailed ADRs and standards"

  - graph_mcp.explore_graph [required]
    params:
      query: "{feature_module_or_domain}"
      limit: 100
    output:
      - nodes: affected modules and functions
      - edges: call relationships
    expected: "Module structure around feature"

  - graph_mcp.find_path_between_module [optional]
    params:
      start_module: "{source_module}"
      end_module: "{target_module}"
      max_depth: 5
    output:
      - paths: cross-module paths
    expected: "Integration paths for new feature"
```

### Phase 2: Codebase Analysis (6min)

```yaml
steps:
  1. Deep analysis of affected code areas via graph_mcp
  2. Identify integration points and API surfaces
  3. Map data flow and state transitions
  4. Assess test coverage in affected areas
  5. Identify technical debt that impacts plan
  6. Report: "Phase 2 complete: {modules} modules analyzed"

analysis_focus:
  - affected_files: "Files that will be modified"
  - dependency_graph: "Upstream and downstream impacts"
  - api_surfaces: "Public interfaces that change"
  - data_models: "Schema changes required"
  - test_gaps: "Areas lacking test coverage"
```

### Phase 3: Solution Design (5min)

```yaml
steps:
  1. Design solution architecture aligned with codebase patterns
  2. Define component responsibilities and interfaces
  3. Identify tradeoffs and document rationale
  4. Design error handling and edge cases
  5. For two-approaches mode: design competing solutions
  6. Report: "Phase 3 complete: Solution designed"

design_deliverables:
  - architecture_overview: "High-level design with Mermaid diagram"
  - component_spec: "Per-component responsibilities and interfaces"
  - data_flow: "Data transformation and state management"
  - api_contract: "New or changed API signatures"
  - tradeoff_log: "Decisions, alternatives considered, rationale"
```

### Phase 4: Plan Creation (4min)

```yaml
steps:
  1. Break solution into ordered phases with dependencies
  2. Estimate effort per phase
  3. Identify risks and mitigations per phase
  4. Define acceptance criteria and verification gates
  5. Generate plan.md with full phase breakdown
  6. Report: "Phase 4 complete: Plan created"

plan_structure:
  metadata: "Title, mode, date, status, blockedBy, blocks"
  overview: "Problem statement, proposed solution, success criteria"
  phases:
    - name: "Phase N: Description"
      objective: "What this phase achieves"
      tasks: ["Task 1", "Task 2", ...]
      dependencies: ["Phase X", "External Y"]
      risks: ["Risk → Mitigation"]
      verification: "How to confirm phase is done"
      estimated_effort: "hours or days"
  risk_register: "Cross-phase risks with severity and mitigation"
  open_questions: "Unresolved decisions needing input"
```

### Phase 5: Review & Validation (3min)

```yaml
steps:
  1. Red-team review: adversarial analysis of plan weaknesses
  2. Validation interview: critical questions to stress-test assumptions
  3. Update plan with review findings
  4. Mark unresolved items for follow-up
  5. Report: "Phase 5 complete: Review done"

red_team_focus:
  - "What assumption, if wrong, breaks this plan?"
  - "What is the simplest alternative that wasn't considered?"
  - "What happens if this takes 3x longer?"
  - "What external dependency is most likely to fail?"
  - "How does this interact with other in-progress work?"

validation_questions:
  - "Is the success criteria measurable and verifiable?"
  - "Are all dependencies explicitly identified?"
  - "Is the effort estimate calibrated against similar past work?"
  - "What is the rollback strategy if this fails mid-implementation?"
```

---

## Output Contract

```yaml
output_location: "{project_root}/plans/{plan_dir}/"

files:
  - "plan.md"                    # Master plan with metadata and overview
  - "phase-01-{name}.md"        # Per-phase detail (one per phase)
  - "research-findings.md"       # MCP evidence and research notes
  - "design-notes.md"            # Architecture decisions and tradeoffs

plan_md_frontmatter:
  title: "{Plan title}"
  status: "draft | in_progress | completed | cancelled"
  mode: "{auto|fast|hard|parallel|two-approaches}"
  created: "{ISO8601}"
  blockedBy: ["{plan_dir_names}"]
  blocks: ["{plan_dir_names}"]
  estimated_effort: "{hours/days}"
```

---

## Non-Negotiable Rules

- ✅ Every plan decision must reference codebase evidence
- ✅ Never plan features that violate existing architecture patterns without justification
- ✅ Always identify cross-plan dependencies (blockedBy/blocks)
- ✅ Red-team review required for hard/parallel/two-approaches modes
- ✅ All phases must have verifiable acceptance criteria
- ✅ Risk register must include mitigation, not just identification
- ✅ Never invent APIs or data models — derive from graph_mcp evidence

---

## Error Handling & Fallback Strategy

```yaml
preflight:
  - check: "project_path_validation"
    action_on_failure: "abort_with_error"
  - check: "mcp_capability_check"
    action_on_failure: "fallback_to_filesystem_only"

fallback:
  when: "mcp_unavailable"
  steps:
    1. Use filesystem for codebase analysis
    2. Read README, docs/, ADRs manually
    3. Mark MCP-derived claims as lower confidence

error_recovery:
  phase_1_research:
    on_mcp_timeout: "continue_with_filesystem_research"
  phase_2_codebase_analysis:
    on_graph_timeout: "continue_with_manual_analysis"
  phase_5_review:
    on_timeout: "skip_validation_and_warn"
```

## Known Limitations

```yaml
limitations:
  plan_accuracy:
    - "Effort estimates based on static analysis, not historical velocity"
    - "Cross-module impacts may miss runtime coupling"
    - "Best results with well-documented codebases (mind_mcp coverage)"
  mode_dependent:
    - "Fast mode skips research — higher risk of missed constraints"
    - "Two-approaches mode requires more analysis time"
```

## Deliverables

- `plan.md` — Master plan with metadata, overview, phase summary, risk register
- `phase-*.md` — Per-phase detailed tasks, dependencies, verification criteria
- `research-findings.md` — MCP evidence and codebase analysis notes
- `design-notes.md` — Architecture decisions, tradeoffs, and rationale

## References

- `references/workflow-modes.md` — Auto-detection logic and per-mode detail
- `references/scope-challenge.md` — Scope challenge question framework
- `references/solution-design.md` — Solution design patterns and templates
- `references/red-team-checklist.md` — Adversarial review questions
- `references/validate-framework.md` — Plan validation interview framework
