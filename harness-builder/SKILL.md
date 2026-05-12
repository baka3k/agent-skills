---
name: harness-builder
description: Build, assess, and improve AI coding agent harness infrastructure across five subsystems — instructions, state, verification, scope, and lifecycle. Use mind_mcp for project context and graph_mcp for code structure discovery when designing harness files. Use when creating AGENTS.md, setting up session continuity, designing verification workflows, or benchmarking agent reliability.
version: 1.0.0
last_updated: 2026-05-12
hooks:
  pre:
    - name: input-validation
      scope: [project_root, harness_scope]
      enable_redaction: true
  phase:
    context_gathering:
      post: [progress-reporter]
    assessment:
      post: [progress-reporter]
    design:
      post: [progress-reporter]
    implementation:
      post: [progress-reporter]
    verification:
      post: [progress-reporter]
    all_phases:
      post: [progress-reporter]
  post:
    - name: output-redaction
      apply_to: [agents_md, feature_list, config_yaml]
    - name: cleanup-handler
      paths: [harness-data/]
      keep: [*.json, *.md, *.yaml, *.sh]
---

# Harness Builder

Build production-grade harness infrastructure for AI coding agents with the five-subsystem framework, MCP-assisted context discovery, and comprehensive security hardening.

## When To Use

- Creating a new AGENTS.md / CLAUDE.md for a project
- Improving agent reliability across sessions
- Agent forgets corrections or project rules between sessions
- Agent overreaches scope or breaks working code
- Setting up verification workflows (tests, lint, typecheck before claiming done)
- Designing session continuity with progress tracking and handoff
- Benchmarking harness effectiveness with before/after metrics
- Auditing existing harness for gaps across the five subsystems

## Avoid Using When

- Prompt engineering or system prompt refinement (not harness infrastructure)
- Model selection or fine-tuning decisions
- One-off agent tasks with no continuity requirements
- Generic software architecture design (MVC, microservices patterns)
- The project already has a mature, well-tested harness

## Required Inputs

- Project root path
- Agent tool being used (Claude Code, Codex, Cursor, etc.)
- Harness scope: `full`, `instructions-only`, `state-only`, `verification-only`, `assess-only`
- Existing harness files if any (AGENTS.md, CLAUDE.md, feature tracking)
- Optional: team tolerance for structure (`minimal`, `moderate`, `comprehensive`)

## Input Validation & Security

### Path Validation

- **Project path**: Must exist, be readable, and be a valid git repository
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **Path sanitization**: Remove null bytes, limit to 1000 characters, whitelist allowed characters

```yaml
path_validation:
  - project_path must be a valid directory
  - project_path must be a git repository
  - Block path traversal: reject if contains "../" or absolute path outside workspace
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max length: 1000 characters
  - Must be readable: os.access(path, os.R_OK)
```

### Harness Scope Validation

```yaml
scope_validation:
  allowed_values: ["full", "instructions-only", "state-only", "verification-only", "assess-only"]
  default: "full"
  error_message: "Invalid scope. Must be one of: full, instructions-only, state-only, verification-only, assess-only"

structure_tolerance:
  allowed_values: ["minimal", "moderate", "comprehensive"]
  default: "moderate"
```

### Sensitive Data Redaction

When reading existing project files that may contain secrets:

```regex
# Credentials and Secrets
API keys:           /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
Passwords:          /password.*/gi → '[REDACTED_PASSWORD]'
Secrets:            /secret.*/gi → '[REDACTED_SECRET]'
Tokens:             /token.*/gi → '[REDACTED_TOKEN]'
Connection strings: /\b(postgresql|mongodb|redis):\/\/[^\s]+\b/gi → '$1://[REDACTED]'
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # Phase timeouts
  phase_0_context_gathering_timeout: 120s   # Project understanding
  phase_1_assessment_timeout: 60s           # Five-subsystem scoring
  phase_2_design_timeout: 180s              # Harness component design
  phase_3_implementation_timeout: 300s      # File generation
  phase_4_verification_timeout: 120s        # Benchmark and validate

  total_workflow_timeout: 900s              # 15 minutes total

  on_timeout:
    action: "return_partial_results"
    notify: "Harness build incomplete due to timeout. Partial files may be available."
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name}"
    - "  Scope: {harness_scope}"
  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Results: {results_summary}"
  final_summary:
    - "Harness build complete"
    - "Subsystems covered: {subsystems_count}/5"
    - "Files generated: {files_count}"
    - "Assessment score: {score}/25"
```

### Caching Strategy

```yaml
cache:
  project_context_cache:
    enabled: true
    ttl: 600
    file: "harness_context_cache.json"
    cache_content:
      - project_structure
      - existing_harness_files
      - tech_stack_info
    invalidation: "on_workflow_start"
```

## The Five-Subsystem Harness Framework

Every harness consists of five subsystems. Assessment and design address each systematically:

| # | Subsystem | Files | Purpose |
|---|-----------|-------|---------|
| 1 | **Instructions** | AGENTS.md, docs/ | Routing layer, progressive disclosure, working rules |
| 2 | **State** | feature_list.json, progress.md | Task tracking, session continuity, handoff |
| 3 | **Verification** | verify.sh, config.yaml checks | Explicit commands agent MUST run before done |
| 4 | **Scope** | feature_list task fields | One-feature-at-a-time, graph_entry_node scoping |
| 5 | **Lifecycle** | init.sh, orchestrator | Session init, health checks, clean-state restart |

## Orchestration Workflow

### Phase 0: Context Gathering (2min)

```yaml
steps:
  1. Validate all inputs (project path, agent tool, scope, tolerance)
  2. Scan existing harness files (AGENTS.md, CLAUDE.md, feature_list.json)
  3. Discover project structure (tech stack, size, module layout)
  4. Query mind_mcp for project context if available
  5. Query graph_mcp for code structure if available
  6. Report: "Phase 0 complete: Context gathered"

mcp_functions_optional:
  - mind_mcp.hybrid_search [optional]
    params:
      query: "project architecture conventions standards"
      collection: "{project_collection}"
      limit: 10
    output:
      - results: relevant project docs
    expected: "Project conventions and standards"

  - graph_mcp.explore_graph [optional]
    params:
      query: "module entrypoint"
      limit: 50
    output:
      - nodes: project modules
    expected: "Module structure overview"
```

### Phase 1: Five-Subsystem Assessment (1min)

```yaml
steps:
  1. Score each subsystem 1-5 based on existing harness files
  2. Identify lowest-scoring subsystem as bottleneck
  3. Prioritize improvements by impact
  4. Report: "Phase 1 complete: Assessment score {total}/25"

scoring_rubric:
  5: "Exemplary — documented, consistently followed, automated"
  4: "Good — mostly complete, occasional gaps"
  3: "Adequate — covers basics, missing polish"
  2: "Weak — incomplete, inconsistently applied"
  1: "Missing or actively harmful"

assessment_output:
  - subsystem_scores: {instructions, state, verification, scope, lifecycle}
  - bottleneck: lowest_scoring_subsystem
  - priority_actions: [top_3_improvements]
```

### Phase 2: Harness Design (3min)

```yaml
steps:
  1. Design instructions layer (AGENTS.md with routing + working rules)
  2. Design state tracking (feature_list.json schema + progress.md template)
  3. Design verification workflow (verify.sh commands)
  4. Design scope control (task definition with graph_entry_node)
  5. Design lifecycle management (init.sh with MCP health checks)
  6. Report: "Phase 2 complete: {subsystems_designed}/5 subsystems designed"

instructions_design:
  components:
    - startup_workflow: "Steps agent follows before writing code"
    - working_rules: "Hard constraints (one-feature-at-a-time, verify before done)"
    - required_artifacts: "Files agent must maintain (feature_list, progress)"
    - definition_of_done: "Checklist agent must complete per feature"
    - end_of_session: "Handoff procedure before disconnecting"

state_design:
  feature_list_schema:
    fields: [id, title, type, status, priority, graph_entry_node, related_modules, related_files, session_id]
    status_flow: "todo → in_progress → done | blocked"

verification_design:
  commands:
    - test_cmd: "Project-specific test suite"
    - lint_cmd: "Linter invocation"
    - type_cmd: "Type checker invocation"
  integration: "verify.sh wraps all commands, returns pass/fail"

scope_design:
  policy: "One feature per session"
  task_isolation:
    - graph_entry_node: "Entry point for graph_mcp context"
    - related_modules: "Module scope whitelist"
    - related_files: "File whitelist for modifications"

lifecycle_design:
  init_sequence:
    - mcp_health_check: "Probe graph_mcp + mind_mcp endpoints"
    - env_validation: "Check required tools available"
    - context_loading: "Load feature_list, progress, AGENTS.md"
```

### Phase 3: Implementation (5min)

```yaml
steps:
  1. Generate AGENTS.md from template with project-specific content
  2. Create .harness/ directory structure
  3. Generate feature_list.json with initial features
  4. Create progress.md session log
  5. Generate init.sh with MCP health checks
  6. Create verify.sh with project-specific commands
  7. Generate config.yaml with MCP endpoints and budget
  8. Report: "Phase 3 complete: {files_count} files generated"

output_files:
  instructions:
    - ".harness/AGENT.md"
  state:
    - ".harness/state/feature_list.json"
    - ".harness/state/progress.md"
  verification:
    - ".harness/scripts/verify.sh"
  lifecycle:
    - ".harness/scripts/init.sh"
  config:
    - ".harness/config.yaml"

template_sources:
  AGENTS.md: "templates/agents.md"
  feature_list.json: "templates/feature-list.json"
  init.sh: "templates/init.sh"
  progress.md: "templates/progress.md"
  config.yaml: "templates/config.yaml"
```

### Phase 4: Verification and Benchmarking (2min)

```yaml
steps:
  1. Validate generated files against schemas
  2. Run five-subsystem re-assessment
  3. Generate before/after comparison if existing harness was present
  4. Produce quality report with gap analysis
  5. Report: "Phase 4 complete: Harness verified"

verification_checks:
  - schema_validation: "feature_list.json passes JSON Schema"
  - completeness: "All 5 subsystems addressed"
  - consistency: "No contradictions between files"
  - usability: "init.sh is executable, paths resolve"

benchmark_metrics:
  - subsystems_covered: "count of addressed subsystems"
  - assessment_score: "before vs after comparison"
  - files_generated: "count of new harness files"
  - improvement_areas: "still-weak subsystems with next actions"
```

## Conflict Resolution Rules

When existing harness practices conflict with recommendations:

```yaml
conflict_resolution:
  priority_rules:
    1. "For project-specific conventions: Trust existing project patterns over generic templates"
    2. "For verification: Prefer existing test/lint commands if already working"
    3. "For state tracking: Adapt to team's existing workflow tools if present"
    4. "For scope: Respect team's existing process if it works reliably"

  tiebreaker:
    when: "existing practice vs recommended practice both reasonable"
    action: "document_both"
    format: |
      Current practice: {existing_practice}
      Recommended: {recommended_practice}
      Decision: Keep existing if functional, note recommendation for future
```

## Quality Gates

- Every subsystem must be addressed in assessment
- AGENTS.md must include startup workflow and working rules
- feature_list.json must have at least one initial feature
- init.sh must include MCP health checks
- verify.sh must reference real project commands
- All generated files must pass syntax validation
- Assessment score improvement must be measurable

## Non-Negotiable Rules

- ✅ Never invent project conventions — derive from existing code and docs
- ✅ Never skip verification workflow design
- ✅ Always validate inputs before generating harness files
- ✅ Always redact sensitive data from generated files
- ✅ Always include MCP health checks in init.sh when MCP servers are available
- ✅ Always provide before/after comparison when improving existing harness

## Observability & Metrics

```yaml
metrics:
  harness_quality:
    - instructions_score: "1-5"
    - state_score: "1-5"
    - verification_score: "1-5"
    - scope_score: "1-5"
    - lifecycle_score: "1-5"
    - total_score: "sum of five scores (max 25)"

  generation_stats:
    - files_generated: "count of new harness files"
    - templates_used: "count of templates applied"
    - project_specific_customizations: "count of template customizations"

  benchmark_comparison:
    - before_score: "pre-improvement total"
    - after_score: "post-improvement total"
    - improvement: "delta"
```

## Error Handling & Fallback Strategy

```yaml
preflight:
  - check: "project_path_validation"
    verify:
      - project_path_exists
      - project_path_is_git_repo
      - project_path_readable
    action_on_failure: "abort_with_error"

  - check: "existing_harness_scan"
    verify:
      - scan for AGENTS.md, CLAUDE.md
      - scan for feature_list.json, progress.md
      - scan for init.sh, verify.sh
    action_on_failure: "continue_with_empty_assessment"

fallback:
  when: "mcp_unavailable"
  action: "filesystem_only_context"
  steps:
    1. Skip MCP queries
    2. Use filesystem tools for project structure discovery
    3. Derive conventions from existing files (README, package.json, etc.)
    4. Note in output: "MCP unavailable, context derived from filesystem only"

error_recovery:
  on_generation_failure:
    action: "report_partial_and_continue"
    log: "File generation failed for {file}, continuing with remaining files"
  on_validation_failure:
    action: "report_errors_and_skip"
    log: "Validation failed for {check}, skipping non-critical components"
```

## Version History & Changelog

### Version 1.0.0 (2026-05-12)

**Initial Release:**
- ✅ Five-subsystem harness framework (Instructions, State, Verification, Scope, Lifecycle)
- ✅ MCP-assisted context discovery (mind_mcp + graph_mcp)
- ✅ Comprehensive input validation and sensitive data redaction
- ✅ Phase-based workflow with progress reporting
- ✅ Harness assessment with 1-5 scoring rubric
- ✅ AGENTS.md, feature_list.json, init.sh, verify.sh, config.yaml generation
- ✅ Before/after benchmarking support
- ✅ Error handling and MCP fallback strategy
- ✅ 6 reference patterns (memory, context, tool-registry, multi-agent, lifecycle, gotchas)
- ✅ 7 harness file templates

## Known Limitations

```yaml
limitations:
  mcp_dependent:
    - "Enhanced context discovery requires mind_mcp and graph_mcp"
    - "Filesystem-only fallback provides basic project context"
    - "module structure from graph_mcp unavailable in fallback mode"

  project_assumptions:
    - "Assumes git-based project with standard structure"
    - "Best results with projects using standard build tools"
    - "Team conventions may override generic recommendations"

  scope:
    - "Generates harness files but does not enforce them"
    - "Session continuity depends on agent following AGENTS.md rules"
    - "Verification effectiveness depends on quality of project test suite"
```

## Deliverables

- `.harness/AGENT.md` — Agent working contract with startup workflow and rules
- `.harness/state/feature_list.json` — Feature tracker with task definitions
- `.harness/state/progress.md` — Session continuity log
- `.harness/scripts/init.sh` — MCP health checks and initialization
- `.harness/scripts/verify.sh` — Test/lint/type check gate
- `.harness/config.yaml` — MCP endpoints, budget, verify configuration
- Assessment report with five-subsystem scores and improvement plan

## References

### Skill-Specific References

- `references/memory-persistence-pattern.md` — Four-level instruction hierarchy, auto-memory taxonomy
- `references/context-engineering-pattern.md` — Select / Compress / Isolate / Write operations, budget management
- `references/tool-registry-pattern.md` — Fail-closed registration, per-call concurrency, permission pipeline
- `references/multi-agent-pattern.md` — Coordinator / Fork / Swarm patterns, context sharing
- `references/lifecycle-bootstrap-pattern.md` — Hook system, long-running tasks, dependency-ordered init
- `references/gotchas.md` — 15 non-obvious failure modes with fixes

### Templates

- `templates/agents.md` — AGENT working contract scaffold
- `templates/feature-list.json` — Task backlog in CortexHarness format
- `templates/feature-list.schema.json` — JSON Schema for validation
- `templates/config.yaml` — Harness config (MCP URLs, budget, verify commands)
- `templates/init.sh` — MCP health check + env validation script
- `templates/progress.md` — Session continuity log template
- `templates/session-handoff.md` — Handoff structure template
