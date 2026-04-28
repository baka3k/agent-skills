---
name: tech-build-audit
description: Detect core technologies, build systems, CI/CD pipelines, deployment targets, and platform assumptions by combining mind_mcp project knowledge with graph_mcp semantic code evidence. Use when documenting an unknown project stack, preparing migrations, validating onboarding docs, or estimating build and runtime risks.
version: 2.0.0
last_updated: 2025-04-16
---

# Tech Build Audit

Derive stack and build facts from MCP evidence first, verify against files, with comprehensive security hardening, operational resilience, and evidence-based decision making.

## When To Use

- You need a reliable picture of tech stack, build commands, and deployment surfaces
- You are validating onboarding docs or preparing migration/build stabilization
- You want API-layer dependency guardrails and build/runtime risk signals
- You are auditing deployment configurations and CI/CD pipelines
- You need to document platform assumptions for cloud/container migrations

## Avoid Using When

- You only need module ownership/entry-point mapping (use repo-recon)
- You only need high-level summary output (use module-summary-report)
- You are focused on one bug's blast radius (use bug-impact-analyzer)
- You only need architectural decision records (use deep-codebase-discovery)

## Required Inputs

- Repository root path
- Optional target environment (`local`, `container`, `cloud`, `hybrid`)
- Optional depth (`quick`, `standard`, `deep`)

## Input Validation & Security

### Path Validation

- **Repository path**: Must exist, be within allowed scope, and be readable by current user
- **Path traversal protection**: Block `../` patterns and absolute paths outside allowed directories
- **Path sanitization**: Remove null bytes, limit to 10000 characters, whitelist allowed characters
- **Access verification**: Verify read access before analysis

**Validation rules**:
```yaml
repository_path_validation:
  - repository_path must exist: os.path.exists(repo_path)
  - repository_path must be readable: os.access(repo_path, os.R_OK)
  - Block path traversal: reject if contains "../" or absolute path
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max length: 10000 characters
```

### Target Environment Validation

- **Target environment**: Must be valid environment type
- **Depth preference**: Must be one of `quick`, `standard`, or `deep`

**Validation rules**:
```yaml
target_environment_validation:
  allowed_values: ["local", "container", "cloud", "hybrid", "auto"]
  default: "auto"
  validation: "Auto-detect if not specified"

depth_validation:
  allowed_values: ["quick", "standard", "deep"]
  default: "standard"
  quick_depth: "Build commands and basic platform detection only"
  standard_depth: "Build commands, CI/CD, and platform detection"
  deep_depth: "All standard + API dependency analysis and runtime tracing"
```

### Sensitive Data Redaction

When auditing build systems and deployment configurations that may contain sensitive information:

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
                    /\bredis:\/\/[^\s]+\b/gi → 'redis://[REDACTED]'

# Cloud and Container Registry
AWS keys:           /\bAKIA[0-9A-Z]{16}\b/g → '[REDACTED_AWS_KEY]'
GCP keys:           /\b[0-9a-f]{32}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi → '[REDACTED_GCP_KEY]'
Azure keys:         /\b[0-9a-zA-Z+/]{86,}=*\b/g → '[REDACTED_AZURE_KEY]'
Docker registry:    /\b[a-z0-9]+\.azurecr\.io\/[^\s]+\b/gi → '[REDACTED_REGISTRY]'
                    /\b[a-z0-9]+\.dkr\.ecr\.[^\s]+\b/gi → '[REDACTED_REGISTRY]'

# Personal Data
Email addresses:    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED_EMAIL]'
Phone numbers:      /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g → '[REDACTED_PHONE]'
```

**Build artifact redaction**:
```yaml
logging_redaction:
  - Log all redactions in audit evidence: "Redacted {count} API keys from build configs"
  - Never log original sensitive data
  - Store only redacted evidence in audit reports
  - Apply redaction before writing to output files

build_config_redaction:
  - .env files: Redact all values, keep keys
  - CI/CD configs: Redact secrets, tokens, credentials
  - Docker/K8s configs: Redact registry credentials, secrets
  - Cloud deployment configs: Redact access keys, connection strings
```

### Access Boundaries

- **Repository scope**: Limit analysis to specified repository path
- **Build system access**: Read-only access to build configuration files
- **CI/CD analysis**: Only analyze CI/CD configuration files (no execution)
- **Cloud metadata**: Only analyze cloud metadata files (no API calls)
- **Network restrictions**: No external network calls during analysis (except to MCP servers)

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  # MCP call timeouts
  mcp_call_timeout: 30s              # Per MCP function call
  query_timeout: 45s                  # Per complex query
  batch_timeout: 60s                  # Per batch processing operation

  # Analysis timeouts
  filesystem_scan_timeout: 180s       # Filesystem audit scan
  build_config_analysis_timeout: 120s # Build configuration parsing
  platform_detection_timeout: 120s    # Platform and deployment detection
  api_dependency_analysis_timeout: 240s # API boundary analysis

  # Phase timeouts
  phase_0_preflight_timeout: 30s      # Preflight and context setup
  phase_1_mind_mcp_timeout: 180s      # mind_mcp build context discovery
  phase_2_graph_mcp_timeout: 240s     # graph_mcp build surface verification
  phase_3_filesystem_timeout: 180s    # Filesystem audit scan
  phase_4_platform_timeout: 120s      # Platform and deployment classification
  phase_5_api_guardrails_timeout: 240s # API dependency guardrails
  phase_6_artifact_timeout: 60s       # Audit artifact generation

  # Total workflow timeout
  total_workflow_timeout: 1200s       # Entire audit (20 minutes)
```

### Resource Limits

```yaml
resource_limits:
  # Repository size limits
  max_repository_size: 1GB            # Prevent memory issues
  max_files_to_analyze: 5000          # Limit for large repos
  max_build_config_size: 10MB         # Skip build configs larger than 10MB

  # Analysis limits
  max_build_systems: 20               # Limit for build system detection
  max_ci_pipelines: 50                # Limit for CI/CD pipeline discovery
  max_platform_targets: 10            # Limit for platform target detection
  max_api_warnings: 200               # Limit for API dependency warnings

  # Output limits
  max_audit_report_size: 5MB          # Single report max size
  max_total_output_size: 100MB        # Total output max size
```

### Progress Feedback

```yaml
progress_reporting:
  # Phase-level progress
  phase_start:
    - "Phase {N} started: {phase_name} (estimated: {estimated_time}s)"
    - "  Repository: {repo_name}"
    - "  Depth: {depth_preference}"
    - "  Target environment: {target_environment}"

  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Duration: {actual_time}s"
    - "  Results: {results_summary}"
    - "  Evidence items: {evidence_count}"

  phase_error:
    - "Phase {N} error: {phase_name}"
    - "  Error: {error_message}"
    - "  Action: {recovery_action}"

  # Task-level progress (for long operations)
  task_progress:
    - "Scanning build configurations: {current}/{total} files"
    - "Detecting build systems: {systems_count} systems found"
    - "Analyzing CI/CD pipelines: {current}/{total} pipelines"
    - "Detecting platform targets: {platforms_count} platforms"
    - "Running API dependency analysis: {current}/{total} files"

  # Discovery progress
  discovery_progress:
    - "Build system discovered: {system_name}"
    - "CI/CD pipeline found: {pipeline_name}"
    - "Platform target detected: {platform_name}"
    - "API dependency warning: {warning_count} warnings"

  # Final summary
  final_summary:
    - "Tech build audit complete"
    - "Total duration: {total_duration}s"
    - "Build systems detected: {build_count}"
    - "CI/CD pipelines: {cicd_count}"
    - "Platform targets: {platform_count}"
    - "API warnings: {warning_count}"
    - "Evidence coverage: {mcp_coverage}%"
    - "Output: {output_files}"
```

### Caching Strategy

```yaml
cache:
  # mind_mcp build context cache
  build_context_cache:
    enabled: true
    ttl: 900                          # 15 minutes
    file: "mcp_build_context_cache.json"
    cache_content:
      - build_commands
      - test_commands
      - deployment_configurations
      - platform_requirements
    invalidation: "on_workflow_start"

  # graph_mcp build surface cache
  build_surface_cache:
    enabled: true
    ttl: 1200                         # 20 minutes
    file: "mcp_build_surface_cache.json"
    cache_content:
      - build_orchestration_code
      - infrastructure_boundaries
      - api_boundary_violations
    invalidation: "on_repo_change"

  # Platform detection cache
  platform_cache:
    enabled: true
    ttl: 1800                         # 30 minutes
    file: "platform_detection_cache.json"
    cache_content:
      - detected_platforms
      - deployment_targets
      - container_orchestration
    invalidation: "on_config_change"

  # API dependency cache
  api_dependency_cache:
    enabled: true
    ttl: 2400                         # 40 minutes
    file: "api_dependency_cache.json"
    cache_content:
      - api_warnings
      - boundary_violations
      - coupling_issues
    invalidation: "on_code_change"

  # Shared evidence cache
  shared_cache:
    enabled: true
    ttl: 2400                         # 40 minutes
    file: "shared_audit_cache.json"
    cache_content:
      - all_mcp_evidence
      - build_systems
      - platform_targets
      - api_warnings
    invalidation: "on_workflow_end"

  # Cache hit tracking
  cache_metrics:
    track_cache_hits: true
    track_cache_misses: true
    report_in_summary: true
```

## Error Handling & Fallback Strategy

### Preflight Checks

Before starting audit:

```yaml
preflight:
  - check: "repository_validation"
    verify:
      - repository_path_exists
      - repository_is_readable
      - repository_has_build_config
      - repository_within_size_limit
    action_on_failure: "abort_with_error"

  - check: "target_environment_validation"
    verify:
      - target_environment_is_valid
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
      - search_by_code
      - list_up_entrypoint
    action_on_failure: "fallback_to_filesystem_only"
```

### MCP Fallback Strategy

```yaml
fallback:
  when: "mcp_unavailable_or_degraded"

  filesystem_only_mode:
    mode: "filesystem_audit_with_reduced_confidence"

    steps:
      1. Skip MCP queries entirely
      2. Use filesystem audit script for build system detection
      3. Use grep/rg patterns for platform detection
      4. Use config file analysis for CI/CD detection
      5. Skip API dependency analysis (requires graph_mcp)
      6. Mark all evidence as low confidence
      7. Add disclaimer to audit report

    logging:
      - "Running in FILESYSTEM-ONLY MODE: MCP unavailable"
      - "Analysis limited to filesystem audit script only"
      - "Evidence confidence: LOW for all items"
      - "API dependency analysis skipped"

    notification:
      - "⚠️ MCP services unavailable or degraded"
      - "Running in filesystem-only mode with reduced confidence"
      - "API dependency analysis not available"
      - "Build commands may be incomplete"

  recovery:
    auto_retry: 1                    # Retry 1 time before fallback
    retry_delay: 10s                 # Wait 10s before retry
    backoff_multiplier: 1.0          # No backoff
    max_retry_time: 30s              # Total retry time before fallback
```

### Error Recovery by Phase

```yaml
error_recovery:
  phase_0_preflight:
    on_repo_invalid:
      action: "abort_with_error"
      log: "Repository validation failed, aborting"
    on_build_config_not_found:
      action: "continue_with_warning"
      log: "No build configuration found, marking as unknown"

  phase_1_mind_mcp:
    on_mcp_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty context"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial build context retrieved, continuing with available data"

  phase_2_graph_mcp:
    on_mcp_timeout:
      action: "fallback_to_filesystem_audit"
      log: "graph_mcp timeout, using filesystem audit script"
      continue: true
    on_parser_unavailable:
      action: "skip_semantic_analysis"
      log: "Required parser unavailable, skipping semantic analysis"
      continue: true

  phase_3_filesystem:
    on_scan_timeout:
      action: "return_partial_results"
      log: "Filesystem scan timeout, returning partial results"
      continue: true
    on_config_parse_error:
      action: "skip_config_and_log"
      log: "Build config parse error, skipping config file"
      continue: true

  phase_4_platform:
    on_detection_timeout:
      action: "use_basic_detection"
      log: "Platform detection timeout, using basic file-based detection"
      continue: true

  phase_5_api_guardrails:
    on_mcp_unavailable:
      action: "skip_api_analysis"
      log: "API dependency analysis requires graph_mcp, skipping"
      continue: true
    on_analysis_timeout:
      action: "return_partial_warnings"
      log: "API analysis timeout, returning partial warnings"
      continue: true

  phase_6_artifact:
    on_report_generation_failure:
      action: "fallback_to_json_output"
      log: "Markdown report generation failed, using JSON output"
      continue: true
```

## Conflict Resolution Rules

When evidence sources conflict during audit decisions:

```yaml
conflict_resolution:
  priority_rules:
    1. "For current build configuration: Trust filesystem (actual files) over mind_mcp"
       - Example: Build command in package.json vs docs → Use package.json
      - Example: CI config in .github/workflows vs docs → Use actual config

    2. "For build process and intent: Trust mind_mcp over filesystem"
       - Example: Why this build step exists → Use docs
      - Example: Build process requirements → Use docs

    3. "For code structure and dependencies: Trust graph_mcp over mind_mcp"
       - Example: Actual imports and dependencies → Use graph
      - Example: API boundaries → Use graph

    4. "For platform and deployment: Trust filesystem over MCP"
       - Example: Docker/K8s configs → Use actual files
      - Example: Cloud deployment scripts → Use actual files

    5. "For CI/CD configuration: Trust filesystem over MCP"
       - Example: CI config files → Use actual configs
      - Example: Pipeline definitions → Use actual definitions

  build_command_conflicts:
    when: "documented build command differs from actual build config"
    rules:
      - "If build configs conflict: Use actual config, document discrepancy"
      - "If docs unclear: Use config analysis as primary, document ambiguity"
      - "If both unclear: Mark as unknown, require manual investigation"

  platform_conflicts:
    when: "documented platform differs from detected platform"
    rules:
      - "If Docker/K8s files exist but docs say local: Document both, flag as inconsistency"
      - "If cloud configs exist but docs say on-prem: Document both, flag as inconsistency"

  logging:
    log_all_conflicts: true
    include_in_report: true
    severity_levels: ["RESOLVED_BY_PRIORITY", "MANUAL_VERIFICATION_NEEDED", "DOCUMENTED_INCONSISTENCY"]
```

## Workflow

### Phase 0: Preflight and Context Setup (30s timeout)

```yaml
steps:
  1. Validate all inputs (repo path, target environment, depth)
  2. Check MCP capabilities via preflight checks
  3. Verify repository and build config access
  4. Initialize shared context map
  5. Configure timeouts, limits, and caching
  6. Report: "Preflight complete, starting tech build audit"

shared_context:
  repository_path: "{repo_path}"
  target_environment: "{local|container|cloud|hybrid|auto}"
  depth_preference: "{quick|standard|deep}"
  detected_platforms: []

mcp_functions:
  - list_qdrant_collections [required]
  - list_source_ids [optional]
  - list_mcp_functions [required]
  - list_parsers [required]
  - list_databases [required]
  - activate_project [required]

on_failure: "abort or fallback to filesystem-only mode"
```

### Phase 1: Pull Build and Platform Context from mind_mcp (180s timeout)

```yaml
steps:
  1. Query for build, release, deployment, runtime, and environment keywords
  2. Use sequential reconstruction when documents describe CI/CD pipelines step by step
  3. Capture explicit commands and constraints as high-confidence facts
  4. Apply sensitive data redaction to all extracted commands
  5. Store as evidence with citations
  6. Cache results to build_context_cache
  7. Report progress: "Phase 1 complete: {count} build context items cached"

mcp_functions:
  - hybrid_search [required]
    params:
      query: "build command OR test command OR release process OR deployment architecture"
      collection: "{selected_collection}"
      limit: 20
    output:
      - results: list of relevant documents
      - scores: relevance scores
    expected: "Build, test, release, deployment commands"

  - sequential_search [optional]
    params:
      query: "CI/CD pipeline step by step OR build process numbered OR deployment workflow"
      collection: "{selected_collection}"
      limit: 10
    output:
      - results: ordered procedure documents
    expected: "Step-by-step CI/CD processes"

  - get_paragraph_text [required]
    params:
      paragraph_ids: ["{ids_from_hybrid_search}"]
    output:
      - text: actual paragraph content
      - citations: source references
    expected: "Detailed content with citations (redacted)"

cache_output:
  file: "mcp_build_context_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    collections: ["{collection_ids}"]
    evidence_items:
      - id: unique_id
        type: build_command | test_command | deployment_config | platform_requirement
        source: mind_mcp
        ref: paragraph_id
        confidence: high | medium | low
        content: summarized content (redacted)

fallback:
  on_mcp_unavailable: "Skip build context discovery, set build_context_cache = {}"
  on_timeout: "Return partial results, cache partial context"
```

### Phase 2: Verify Build Surfaces with graph_mcp (240s timeout)

```yaml
steps:
  1. Activate graph project context first
  2. Use semantic exploration to find build orchestration code, pipeline helpers, deploy adapters
  3. Trace flows from startup/entry functions to infrastructure boundaries (DB, queue, external APIs)
  4. Validate whether code structure matches documented build/runtime expectations
  5. Cache results
  6. Report progress: "Phase 2 complete: {count} build surfaces verified"

mcp_functions:
  - activate_project [required]
    params:
      project_id: "{project_id}"
      database: "{database}"
    output:
      - success: boolean
      - project_info: project metadata

  - explore_graph [required]
    params:
      query: "application startup OR dependency injection OR database connection"
      limit: 100
    output:
      - nodes: discovered nodes
      - edges: connections
    expected: "Build and runtime initialization code"

  - search_functions [required]
    params:
      query: "docker OR kubernetes OR deployment OR infrastructure"
      limit: 50
    output:
      - functions: matching functions
    expected: "Deployment and infrastructure code"

  - search_by_code [required]
    params:
      query: "dockerfile OR kubernetes OR deployment OR ci"
      limit: 50
    output:
      - code_snippets: matching code
    expected: "Concrete deployment signatures"

  - list_up_entrypoint [required]
    params:
      file_pattern: "{module_pattern}/**/*.{ext}"
      limit: 100
    output:
      - entry_points: API endpoints, main functions
    expected: "Executable roots"

  - query_subgraph [optional]
    params:
      node_id: "{infra_node_id}"
      depth: 3
      limit: 50
    output:
      - subgraph: nodes and edges around infrastructure
    expected: "Infrastructure boundary context"

  - trace_flow [optional]
    params:
      start_node: "{entry_point_id}"
      max_depth: 5
    output:
      - flow: execution path to infrastructure
    expected: "Runtime path to DB/queue/external APIs"

cache_output:
  file: "mcp_build_surface_cache.json"
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    evidence_items:
      - id: node_id
        type: build_orchestration | deploy_adapter | infra_boundary
        source: graph_mcp
        metadata: {name, file, signature}
        confidence: high | medium | low

fallback:
  on_mcp_unavailable: "Skip build surface verification, continue to filesystem audit"
  on_timeout: "Return partial results, continue to filesystem audit"
```

### Phase 3: Run Automated Filesystem Audit (180s timeout)

```yaml
steps:
  1. Run filesystem audit script for build system detection
  2. Analyze build configuration files
  3. Detect package managers and build tools
  4. Analyze CI/CD configuration files
  5. Apply sensitive data redaction to all configs
  6. Report progress: "Phase 3 complete: {count} build systems detected"

audit_script:
  command: |
    python scripts/tech_build_audit.py /path/to/repo \
      --json /tmp/tech-build-audit.json \
      --md /tmp/tech-build-audit.md

  timeout: 180s
  output:
    - build_systems: detected build systems (npm, maven, gradle, etc.)
    - build_commands: extracted build commands
    - test_commands: extracted test commands
    - ci_pipelines: detected CI/CD configurations
    - platform_targets: detected platforms (web, api, worker, etc.)

  build_system_detection:
    - "package.json" → Node.js, npm/yarn/pnpm
    - "pom.xml" → Java, Maven
    - "build.gradle" → Java, Gradle
    - "requirements.txt" / "pyproject.toml" → Python, pip
    - "go.mod" → Go, go modules
    - "Cargo.toml" → Rust, Cargo
    - "Gemfile" → Ruby, Bundler
    - "composer.json" → PHP, Composer

  ci_cd_detection:
    - ".github/workflows/*.yml" → GitHub Actions
    - ".gitlab-ci.yml" → GitLab CI
    - "Jenkinsfile" → Jenkins
    - "cloudbuild.yaml" → Google Cloud Build
    - "azure-pipelines.yml" → Azure Pipelines
    - ".circleci/config.yml" → CircleCI

  platform_detection:
    - "Dockerfile" → Docker container
    - "docker-compose.yml" → Docker compose
    - "kubernetes/*.yaml" → Kubernetes
    - "helm/*.yaml" → Helm chart
    - "terraform/*.tf" → Terraform infrastructure

  redaction_applied:
    - All credentials redacted from configs
    - All API keys redacted from configs
    - All connection strings redacted from configs

fallback:
  on_script_failure: "Use manual grep patterns for build system detection"
  on_timeout: "Return partial results, document coverage gap"
```

### Phase 4: Classify Platform and Deployment Surfaces (120s timeout)

```yaml
steps:
  1. Detect platform targets from build configs and code structure
  2. Classify deployment surfaces (web, API, worker, mobile, desktop)
  3. Identify containerization and orchestration
  4. Capture CI/CD ownership and release path hints
  5. Report progress: "Phase 4 complete: {count} platforms classified"

platform_classification:
  web_frontend:
    indicators:
      - package.json with react/vue/angular
      - webpack/vite rollup config
      - static asset build process
    evidence: "Build config + source structure"

  backend_services:
    indicators:
      - server framework (express, spring boot, django)
      - API route definitions
      - database migrations
    evidence: "Code structure + dependencies"

  worker_batch:
    indicators:
      - job queue library (bull, celery, sidekiq)
      - cron/scheduler configuration
      - batch processing framework
    evidence: "Code structure + config files"

  mobile:
    indicators:
      - react-native / flutter / swift / kotlin
      - mobile build configuration
      - app store deployment configs
    evidence: "Build config + project structure"

  desktop:
    indicators:
      - electron / tauri / javafx configuration
      - desktop framework dependencies
    evidence: "Build config + dependencies"

  containerized:
    indicators:
      - Dockerfile present
      - docker-compose configuration
      - container registry references
    evidence: "Config files"

  orchestrated:
    indicators:
      - Kubernetes manifests
      - Helm charts
      - Deployment/Service objects
    evidence: "K8s files"

deployment_surfaces:
  ci_cd_ownership:
    - Detect CI/CD platform (GitHub Actions, GitLab CI, etc.)
    - Identify pipeline configuration files
    - Extract deployment stages and environments

  release_path:
    - Identify versioning strategy
    - Detect artifact publishing (npm, maven, docker registry)
    - Extract deployment commands

cache_output:
  file: "platform_detection_cache.json"
  content:
    timestamp: "{ISO8601}"
    platforms:
      - type: web | api | worker | mobile | desktop | container | orchestrated
        indicators: []
        evidence_source: filesystem | graph_mcp
        confidence: high | medium | low

fallback:
  on_detection_incomplete: "Document as unknown platform, require manual verification"
```

### Phase 5: Run API Dependency Guardrails (240s timeout)

```yaml
steps:
  1. Detect API boundary violations
  2. Find API/controller/handler calling driver directly
  3. Find service/domain layer importing web framework APIs
  4. Prioritize high-risk warnings with graph_mcp path tracing
  5. Apply warning taxonomy (see api-warning-rules.md)
  6. Report progress: "Phase 5 complete: {warning_count} API warnings generated"

api_boundary_checks:
  rule_w1_api_direct_driver_access:
    condition:
      - "API/controller/handler code imports low-level DB driver"
      - "Same file performs direct query/execute/connect operations"

    severity:
      - high: "Both import and operation observed"
      - medium: "Only driver import observed"

    why_it_matters:
      - "Bypasses service/repository abstraction"
      - "Makes transport layer tightly coupled to persistence details"

  rule_w2_service_layer_framework_coupling:
    condition:
      - "Service/domain/usecase layer imports web framework symbols"

    severity:
      - medium: "Framework symbols imported in business logic"

    why_it_matters:
      - "Business logic becomes framework-dependent"
      - "Harder to test and migrate frameworks"

  rule_w3_controller_to_driver_call_path:
    condition:
      - "Call path exists from API entry function to driver symbol"
      - "No intermediate service/repository abstraction node observed"

    severity:
      - high: "Direct call path to driver without abstraction"

    why_it_matters:
      - "Indicates architectural boundary violation in runtime flow"

detection_methods:
  filesystem_scan:
    - "rg 'import.*driver|require.*driver' in controllers/"
    - "rg '@Repository|@Service' for Spring patterns"
    - "rg 'SELECT|UPDATE|DELETE|INSERT' in API files"

  graph_mcp_tracing:
    - "Find API entry functions (list_up_entrypoint)"
    - "Find driver or low-level DB symbols (search_functions)"
    - "Use find_paths between API nodes and driver nodes"
    - "Check for service/repository adapter hop in path"

warning_payload:
  required_fields:
    - warning_id: "Unique identifier"
    - severity: "high | medium | low"
    - path: "File path or node/function id"
    - title: "Short description"
    - evidence: "Matched patterns or graph path refs"
    - recommendation: "Mitigation recommendation"
    - evidence_type: "graph_mcp | filesystem"

fallback:
  on_mcp_unavailable: "Use filesystem-only pattern matching, reduced accuracy"
  on_timeout: "Return partial warnings, document incomplete analysis"
```

### Phase 6: Produce Audit Artifact (60s timeout)

```yaml
steps:
  1. Use audit-template.md for consistent report format
  2. Include technology matrix with evidence sources
  3. Include build and test commands grouped by ecosystem
  4. Include CI/CD and deployment signals
  5. Include platform assumptions and risk notes
  6. Include API dependency warnings
  7. Mark evidence type for each claim (mind_mcp, graph_mcp, filesystem)
  8. Report progress: "Phase 6 complete: Audit artifact generated"

audit_artifact_content:
  snapshot:
    - repository: string
    - commit/branch: string
    - scan_date: ISO8601
    - audit_scope: string

  technology_matrix:
    rows:
      - area: "Language/runtime | Framework | Package/build | CI/CD | Deployment"
        detected: string
        evidence: paragraph_id | node_id | file_path
        confidence: high | medium | low

  build_and_test_commands:
    rows:
      - ecosystem: "Node | Python | Java | etc."
        command: string
        source: package.json | pyproject | etc.
        status: confirmed | inferred

  platform_targets:
    - web: boolean
    - api: boolean
    - worker/batch: boolean
    - mobile: boolean
    - desktop: boolean
    - container/kubernetes: boolean

  risks_and_unknowns:
    rows:
      - topic: string
        risk: low | medium | high
        evidence_gap: string
        recommended_probe: string

  api_dependency_warnings:
    rows:
      - severity: high | medium | low
        warning: string
        path: string
        evidence_type: graph_mcp | filesystem
        recommendation: string

output_files:
  - "tech_build_audit.json": Normalized evidence and derived signals
  - "tech_build_audit.md": Human summary with actionable command list
  - "mcp_build_evidence.md": Query logs and extracted facts (optional)
  - "api_dependency_warnings.json": Extracted boundary and coupling warnings (optional)

fallback:
  on_report_generation_failure: "Fallback to JSON output only"
```

## Output Contract

### Document Package Structure

```yaml
output_location: "<target>/.github/tech-build-audit/"

mandatory_outputs:
  audit_report:
    - "tech_build_audit.md" - Human-readable audit summary
    - "tech_build_audit.json" - Machine-readable audit data

  optional_outputs:
    - "mcp_build_evidence.md" - MCP query logs
    - "api_dependency_warnings.json" - API warnings detail
    - "platform_analysis.json" - Platform classification detail
```

## Non-Negotiable Rules

- ✅ Never invent build commands or platform targets without evidence
- ✅ Never assume CI/CD configuration without verifying actual config files
- ✅ Always validate inputs before analysis (security)
- ✅ Always redact sensitive data before writing to output (security)
- ✅ Always timeout operations and handle failures gracefully (operational)
- ✅ Always report progress for long-running operations (UX)
- ✅ Always cache MCP evidence to improve efficiency (performance)
- ✅ Always include evidence source tags in every claim (traceability)
- ✅ Always mark conflicting evidence with resolution rules (consistency)

## Observability & Metrics

### Metrics to Track

```yaml
metrics:
  audit_progress:
    - total_phases: "Total workflow phases"
    - completed_phases: "Completed phases"
    - current_phase: "Current phase in progress"

  build_system_coverage:
    - build_systems_detected: "Build systems discovered"
    - build_commands_confirmed: "Build commands with high confidence"
    - build_commands_inferred: "Build commands with medium/low confidence"
    - test_commands_detected: "Test commands discovered"
    - ci_pipelines_detected: "CI/CD pipelines discovered"

  platform_coverage:
    - web_detected: boolean
    - api_detected: boolean
    - worker_detected: boolean
    - mobile_detected: boolean
    - desktop_detected: boolean
    - container_detected: boolean
    - orchestrated_detected: boolean

  evidence_quality:
    - total_claims: "Total audit claims"
    - mcp_sourced_claims: "Claims with MCP evidence"
    - mind_mcp_sourced_claims: "Claims from mind_mcp"
    - graph_mcp_sourced_claims: "Claims from graph_mcp"
    - filesystem_sourced_claims: "Claims from filesystem"
    - mcp_evidence_percentage: "MCP coverage percentage"

  api_dependency_warnings:
    - high_severity_warnings: "High-risk API boundary violations"
    - medium_severity_warnings: "Medium-risk coupling issues"
    - low_severity_warnings: "Low-risk warnings"
    - total_warnings: "Total API dependency warnings"

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
    threshold: 60
    check: "mcp_evidence_percentage >= 60"
    on_fail:
      action: "report_gaps_and_continue"
      add_warning: true

  gate_2_build_command_verification:
    threshold: 80
    check: "confirmed_build_commands / total_build_commands >= 80%"
    on_fail:
      action: "mark_as_inferred"
      add_warning: true

  gate_3_platform_detection:
    check: "all_platforms_have_evidence"
    on_fail:
      action: "document_as_unknown"
      add_note: true

  gate_4_high_risk_warnings:
    check: "all_high_risk_warnings_have_recommendations"
    on_fail:
      action: "add_generic_recommendation"
      add_warning: true
```

## Version History & Changelog

### Version 2.0.0 (2025-04-16)

**Breaking Changes:**
- Added mandatory input validation and sanitization
- Added mandatory sensitive data redaction for build configs
- Enhanced timeout configuration (was unlimited, now 20min max)
- Enhanced fallback strategy (was implicit, now explicit with rules)

**New Features:**
- ✅ Added Security & Privacy section with validation and redaction
- ✅ Added Performance & UX section with timeouts, progress feedback, caching
- ✅ Enhanced fallback strategy with filesystem-only mode
- ✅ Added conflict resolution rules for build command decisions
- ✅ Added specific MCP function names with parameters and outputs
- ✅ Added observability metrics and quality gates
- ✅ Added version history and changelog

**Improvements:**
- Enhanced MCP integration with specific function names
- Added preflight checks for MCP and path validation
- Enhanced error handling with specific recovery strategies per phase
- Added progress reporting after each phase
- Added conflict resolution rules with conservative documentation
- Added quality gates for evidence coverage and build command verification
- Enhanced API dependency guardrails with detailed detection methods

**Bug Fixes:**
- Fixed: No input validation (security vulnerability)
- Fixed: No timeout handling (could hang indefinitely)
- Fixed: No fallback strategy (complete failure on MCP down)
- Fixed: No conflict resolution (build command contradictions unresolved)
- Fixed: No progress feedback (poor UX for long audits)

**Migration Guide:**
- Update any custom timeouts to new configuration format
- Review and update input validation rules if customizing
- Review and update redaction patterns if adding new sensitive data types
- Update audit template if using custom output format

### Version 1.0.0 (Initial Release)

- Initial workflow for tech/build audit
- Basic MCP integration (mind_mcp, graph_mcp)
- Evidence-based build system and platform detection
- Filesystem audit script integration
- API dependency guardrails
- Basic audit report generation

## Known Limitations

```yaml
limitations:
  mcp_dependent:
    - "Requires both mind_mcp and graph_mcp for full functionality"
    - "Filesystem-only mode has significantly reduced accuracy and confidence"
    - "Historical build context unavailable if mind_mcp is down"

  performance:
    - "Very large repositories (>500k files) may exceed timeouts"
    - "Monorepos with many build systems may hit max_build_systems limit"
    - "Deep API dependency analysis may timeout on large codebases"

  analysis_scope:
    - "Only analyzes specified repository"
    - "Cannot analyze external build dependencies without source code"
    - "Cannot execute build commands (analysis only)"

  platform_detection:
    - "Best effort detection based on configs and code patterns"
    - "May miss polyglot projects with mixed platforms"
    - "Cannot detect runtime behavior without execution traces"

  api_dependency_analysis:
    - "Requires graph_mcp for accurate path tracing"
    - "May miss dynamic call patterns not captured in static analysis"
    - "Filesystem-only mode has reduced accuracy for boundary violations"

  build_config_parsing:
    - "May fail on custom or templated build configurations"
    - "Cannot execute build scripts for dynamic config discovery"
    - "May miss build commands generated programmatically"
```

## Deliverables

- Technology matrix with evidence sources
- Build and test commands grouped by ecosystem
- CI/CD pipeline identification and configuration
- Platform target classification
- API dependency warnings with recommendations
- Risk assessment and unknowns documentation

## References

- `scripts/tech_build_audit.py`: Automatic stack/build/platform detector
- `references/audit-template.md`: Consistent audit-report format
- `references/mcp-audit-playbook.md`: MCP query recipes for stack/build/platform analysis
- `references/api-warning-rules.md`: Warning taxonomy for API-driver/framework coupling
- `references/quality-gates.md`: Exit criteria and review checklist
- `references/source-material-index.md`: Canonical source files used
