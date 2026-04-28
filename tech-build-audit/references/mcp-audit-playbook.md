# MCP Audit Playbook

Use this sequence to audit technologies, build systems, and platform targets with comprehensive security hardening, operational resilience, and evidence-based decision making.

## 1. Objective

Audit core technologies, build systems, CI/CD pipelines, deployment targets, and platform assumptions by combining mind_mcp project knowledge with graph_mcp semantic code evidence, with security hardening, performance optimization, and fallback strategies.

## 2. MCP-First Tool Order with Detailed Signatures

### Phase 0: Preflight and Validation (Required, 30s timeout)

**Objective**: Verify MCP capabilities, validate inputs, and configure audit environment.

#### Step 1: Input Validation (Required)

```yaml
validation_checks:
  repository_path:
    - repository_path must exist: os.path.exists(repo_path)
    - repository_path must be readable: os.access(repo_path, os.R_OK)
    - Block path traversal: reject if contains "../" or absolute path
    - Character whitelist: [a-zA-Z0-9_\-./]
    - Max length: 10000 characters

  target_environment:
    allowed_values: ["local", "container", "cloud", "hybrid", "auto"]
    default: "auto"
    validation: "Auto-detect if not specified"

  depth_preference:
    allowed_values: ["quick", "standard", "deep"]
    default: "standard"
    quick_depth: "Build commands and basic platform detection only"
    standard_depth: "Build commands, CI/CD, and platform detection"
    deep_depth: "All standard + API dependency analysis and runtime tracing"
```

#### Step 2: MCP Capability Verification

```python
# mind_mcp functions to verify
mind_mcp.list_qdrant_collections [required]
  params: {}
  timeout: 30s
  output:
    - collections: list of available collections
  failure_action: "fallback_to_filesystem_only"

mind_mcp.list_source_ids [optional]
  params:
    collection: string
  timeout: 30s
  output:
    - source_ids: list of document sources
  failure_action: "continue_without_source_filtering"

# graph_mcp functions to verify
graph_mcp.list_mcp_functions [required]
  params: {}
  timeout: 30s
  output:
    - functions: list of available MCP functions
  failure_action: "fallback_to_filesystem_only"

graph_mcp.list_parsers [required]
  params: {}
  timeout: 30s
  output:
    - parsers: list of language parsers available
  expected: "Check for target language parser"
  failure_action: "abort_with_error_if_parser_missing"

graph_mcp.list_databases [required]
  params: {}
  timeout: 30s
  output:
    - databases: list of graph databases
  failure_action: "fallback_to_filesystem_only"

graph_mcp.activate_project [required]
  params:
    project_id: string
    database: string
  timeout: 30s
  output:
    - success: boolean
  failure_action: "abort_with_error"
```

#### Step 3: Preflight Decision

```yaml
if all_mcp_checks_pass:
  proceed_to_phase_1

elif any_mcp_check_fails:
  fallback_to_filesystem_only_mode:
    steps:
      - "⚠️ MCP services unavailable or degraded"
      - "Running in filesystem-only mode with reduced confidence"
      - "API dependency analysis not available"
      - "Build commands may be incomplete"

    logging:
      - "Running in FILESYSTEM-ONLY MODE: MCP unavailable"
      - "Analysis limited to filesystem audit script only"
      - "Evidence confidence: LOW for all items"
```

### Phase 1: mind_mcp Build and Platform Context Discovery (180s timeout)

**Objective**: Extract build commands, test commands, deployment configurations, and platform requirements from knowledge base.

#### 1.1 Discover Build and Test Commands

```python
mind_mcp.hybrid_search [required]
  params:
    query: "build command OR test command OR release process OR deployment architecture"
    collection: "{selected_collection}"
    limit: 20
  timeout: 45s
  output:
    results:
      - id: paragraph_id
        score: relevance_score_0_to_1
        metadata:
          source_file: string
          source_type: "readme" | "doc" | "adr" | "ticket"
    expected:
      - "Build commands (npm run build, mvn package, etc.)"
      - "Test commands (npm test, pytest, etc.)"
      - "Release process descriptions"
      - "Deployment architecture docs"

  # Example queries for build context
  example_queries:
    - "npm run build OR webpack OR vite OR rollup"
    - "mvn package OR gradle build OR maven compile"
    - "pytest OR junit OR npm test"
    - "docker build OR kubernetes apply"
    - "CI/CD pipeline OR github actions OR gitlab CI"

  # Apply sensitive data redaction
  redaction_rules:
    - API keys: /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
    - Passwords: /password.*/gi → '[REDACTED_PASSWORD]'
    - Secrets: /secret.*/gi → '[REDACTED_SECRET]'
    - Tokens: /token.*/gi → '[REDACTED_TOKEN]'
    - Connection strings: /\bpostgresql:\/\/[^\s]+\b/gi → 'postgresql://[REDACTED]'
    - URLs with creds: /\b[\w-]+:\/\/[\w-]+:[\w-]+@/gi → '[REDACTED_URL]'

  error_handling:
    on_timeout:
      action: "return_cached_or_empty"
      log: "mind_mcp timeout, using cached results or empty context"
      continue: true
    on_partial_results:
      action: "continue_with_partial"
      log: "Partial build context retrieved, continuing with available data"
```

#### 1.2 Discover CI/CD Pipeline Steps

```python
mind_mcp.sequential_search [optional]
  params:
    query: "CI/CD pipeline step by step OR build process numbered OR deployment workflow"
    collection: "{selected_collection}"
    limit: 10
  timeout: 45s
  output:
    results:
      - ordered_procedures:
          steps: []
          sequence: integer
    expected:
      - "Ordered CI/CD pipeline steps"
      - "Build process stages"
      - "Deployment workflow steps"

  # Example CI/CD queries
  example_queries:
    - "step 1 OR step 2 OR stage 1 OR stage 2"
    - "pipeline stages OR build phases"
    - "continuous integration OR continuous deployment"
    - "github actions workflow OR gitlab CI pipeline"

  error_handling:
    on_timeout:
      action: "skip_cicd_extraction"
      log: "CI/CD extraction timeout, skipping pipeline steps"
      continue: true
```

#### 1.3 Get Detailed Content

```python
mind_mcp.get_paragraph_text [required]
  params:
    paragraph_ids: ["{ids_from_hybrid_search}"]
  timeout: 30s
  output:
    text:
      - id: paragraph_id
        content: string
        citation: string
    expected:
      - "Full paragraph content with citations"
      - "Source references for traceability"

  # Apply comprehensive redaction
  redaction_rules:
    # Credentials
    - API keys: /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED_API_KEY]'
    - Passwords: /password.*/gi → '[REDACTED_PASSWORD]'
    - Secrets: /secret.*/gi → '[REDACTED_SECRET]'
    - Tokens: /token.*/gi → '[REDACTED_TOKEN]'

    # Network
    - IP addresses: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g → '[REDACTED_IP]'
    - Hostnames: /\b[a-zA-Z0-9.-]+\.(?:com|net|org|io)\b/gi → '[REDACTED_HOST]'

    # Cloud
    - AWS keys: /\bAKIA[0-9A-Z]{16}\b/g → '[REDACTED_AWS_KEY]'
    - GCP keys: /\b[0-9a-f]{32}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi → '[REDACTED_GCP_KEY]'
    - Docker registry: /\b[a-z0-9]+\.azurecr\.io\/[^\s]+\b/gi → '[REDACTED_REGISTRY]'

  error_handling:
    on_timeout:
      action: "use_search_snippets"
      log: "get_paragraph_text timeout, using search snippets"
      continue: true
```

#### 1.4 Cache Build Context

```yaml
cache_output:
  file: "mcp_build_context_cache.json"
  ttl: 900  # 15 minutes
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
    redaction_log:
      - "Redacted {count} API keys"
      - "Redacted {count} passwords"
      - "Redacted {count} connection strings"

  progress_reporting:
    phase_complete:
      - "Phase 1 complete: Build context discovery"
      - "  Duration: {actual_time}s"
      - "  Build commands: {commands_count}"
      - "  Test commands: {test_count}"
      - "  Deployment configs: {deploy_count}"
      - "  Evidence items: {evidence_count}"
```

### Phase 2: graph_mcp Build Surface Verification (240s timeout)

**Objective**: Verify build and runtime surfaces using semantic code exploration.

#### 2.1 Activate Project Context

```python
graph_mcp.activate_project [required]
  params:
    project_id: "{project_id}"
    database: "{database}"
  timeout: 30s
  output:
    success: boolean
    project_info:
      name: string
      language: string
      parser: string

  error_handling:
    on_failure:
      action: "abort_with_error"
      log: "Failed to activate project, aborting audit"
```

#### 2.2 Explore Build and Runtime Initialization

```python
graph_mcp.explore_graph [required]
  params:
    query: "application startup OR dependency injection OR database connection"
    limit: 100
  timeout: 60s
  output:
    nodes:
      - id: node_id
        name: string
        type: "function" | "class" | "module"
        file: string
    edges:
      - from: node_id
        to: node_id
        type: "calls" | "contains" | "imports"
    expected:
      - "Application startup code"
      - "Dependency injection initialization"
      - "Database connection setup"
      - "Queue consumer bootstrap"

  # Example build/runtime queries
  example_queries:
    - "main OR startup OR bootstrap OR init"
    - "app.listen OR server.start OR createServer"
    - "database OR connection OR pool"
    - "consumer OR subscriber OR worker"

  # Context control for large modules
  context_control:
    max_results: 100
    if_results_truncated:
      - "Summarize first 100 results"
      - "Ask user for specific build/runtime focus"

  error_handling:
    on_timeout:
      action: "return_partial_results"
      log: "Graph exploration timeout, returning partial results"
      continue: true
```

#### 2.3 Search for Deployment and Infrastructure Code

```python
graph_mcp.search_functions [required]
  params:
    query: "docker OR kubernetes OR deployment OR infrastructure"
    limit: 50
  timeout: 45s
  output:
    functions:
      - id: node_id
        name: string
        file: string
        signature: string
    expected:
      - "Deployment adapter functions"
      - "Infrastructure initialization"
      - "Container orchestration"

  # Example deployment queries
  example_queries:
    - "docker build OR docker run OR container"
    - "kubernetes OR k8s OR deployment OR service"
    - "terraform OR pulumi OR infrastructure"
    - "cloud OR aws OR azure OR gcp"

  error_handling:
    on_timeout:
      action: "skip_deployment_search"
      log: "Deployment function search timeout, using filesystem configs"
      continue: true
```

#### 2.4 Search by Code for Concrete Signatures

```python
graph_mcp.search_by_code [required]
  params:
    query: "dockerfile OR kubernetes OR deployment OR ci"
    limit: 50
  timeout: 45s
  output:
    code_snippets:
      - id: node_id
        code: string
        file: string
        language: string
    expected:
      - "Docker configuration code"
      - "Kubernetes manifest references"
      - "CI variable usage"
      - "DB driver imports"

  # Example code pattern queries
  example_queries:
    - "FROM node: OR FROM python: OR FROM openjdk:"
    - "apiVersion: apps/v1 OR kind: Deployment"
    - "process.env.CI || CI_PIPELINE_ID"
    - "import mysql OR import pg OR require('redis')"

  error_handling:
    on_timeout:
      action: "skip_code_search"
      log: "Code pattern search timeout, using filesystem patterns"
      continue: true
```

#### 2.5 Map Entry Points

```python
graph_mcp.list_up_entrypoint [required]
  params:
    file_pattern: "**/*.{py,js,ts,java,go,rs}"
    limit: 100
  timeout: 60s
  output:
    entry_points:
      - id: node_id
        name: string
        file: string
        type: "function" | "method" | "api_endpoint"
    expected:
      - "Executable entry points"
      - "API endpoints"
      - "Main functions"

  # Use entry points for runtime tracing
  use_case:
    - "Trace from entry points to infrastructure boundaries"
    - "Identify DB/queue/external API calls"
    - "Map deployment dependencies"

  error_handling:
    on_timeout:
      action: "use_filesystem_entry_patterns"
      log: "Entry point discovery timeout, using rg patterns"
      continue: true
```

#### 2.6 Trace Infrastructure Boundaries

```python
graph_mcp.query_subgraph [optional]
  params:
    node_id: "{infra_node_id}"
    depth: 3
    limit: 50
  timeout: 60s
  output:
    subgraph:
      nodes:
        - id: node_id
          name: string
          type: string
      edges:
        - from: node_id
          to: node_id
          type: string
    expected:
      - "Infrastructure boundary context"
      - "Related database operations"
      - "Queue consumer setup"

  # Example infrastructure nodes
  example_infra_nodes:
    - "Database connection pool"
    - "Queue consumer"
    - "HTTP client"
    - "Cache client"

  error_handling:
    on_timeout:
      action: "skip_infra_expansion"
      log: "Infrastructure expansion timeout, using surface-level evidence"
      continue: true
```

#### 2.7 Trace Runtime Flows

```python
graph_mcp.trace_flow [optional]
  params:
    start_node: "{entry_point_id}"
    max_depth: 5
  timeout: 60s
  output:
    flow:
      - step: integer
        node_id: string
        function_name: string
        file: string
    expected:
      - "Runtime path from entry to infrastructure"
      - "Database operation calls"
      - "External API calls"

  # Use for platform detection
  use_case:
    - "Trace to DB → backend service"
    - "Trace to queue → worker/batch"
    - "Trace to static files → web frontend"

  error_handling:
    on_timeout:
      action: "skip_flow_tracing"
      log: "Flow tracing timeout, using surface-level evidence"
      continue: true
```

#### 2.8 Cache Build Surfaces

```yaml
cache_output:
  file: "mcp_build_surface_cache.json"
  ttl: 1200  # 20 minutes
  content:
    timestamp: "{ISO8601}"
    project_id: "{project_id}"
    database: "{database}"
    evidence_items:
      - id: node_id
        type: build_orchestration | deploy_adapter | infra_boundary
        source: graph_mcp
        metadata:
          name: string
          file: string
          signature: string
        confidence: high | medium | low

  progress_reporting:
    phase_complete:
      - "Phase 2 complete: Build surface verification"
      - "  Duration: {actual_time}s"
      - "  Build orchestration: {orchestration_count}"
      - "  Deploy adapters: {adapter_count}"
      - "  Infra boundaries: {boundary_count}"
```

### Phase 3: Filesystem Audit Script (180s timeout)

**Objective**: Run automated filesystem audit for build system detection and configuration analysis.

#### 3.1 Execute Audit Script

```bash
python scripts/tech_build_audit.py /path/to/repo \
  --json /tmp/tech-build-audit.json \
  --md /tmp/tech-build-audit.md
```

#### 3.2 Build System Detection

```yaml
build_system_patterns:
  Node.js:
    config_files:
      - "package.json"
    indicators:
      - "scripts: { build, test, start }"
      - "dependencies: { react, vue, angular }"
      - "devDependencies: { webpack, vite, rollup, tsup }"
    build_commands:
      - "npm run build"
      - "yarn build"
      - "pnpm build"
    test_commands:
      - "npm test"
      - "npm run test:unit"
      - "npm run test:integration"

  Java_Maven:
    config_files:
      - "pom.xml"
    indicators:
      - "<packaging>jar|war</packaging>"
      - "<build><plugins>"
    build_commands:
      - "mvn package"
      - "mvn clean install"
    test_commands:
      - "mvn test"
      - "mvn verify"

  Java_Gradle:
    config_files:
      - "build.gradle"
      - "build.gradle.kts"
    indicators:
      - "apply plugin: 'java' OR 'application'"
      - "dependencies { implementation }"
    build_commands:
      - "gradle build"
      - "./gradlew build"
    test_commands:
      - "gradle test"
      - "./gradlew test"

  Python:
    config_files:
      - "setup.py"
      - "pyproject.toml"
      - "requirements.txt"
      - "Pipfile"
    indicators:
      - "[tool.poetry]"
      - "[build-system]"
      - "flask OR django OR fastapi"
    build_commands:
      - "python setup.py build"
      - "poetry build"
    test_commands:
      - "pytest"
      - "python -m unittest"
      - "tox"

  Go:
    config_files:
      - "go.mod"
    indicators:
      - "module github.com/..."
      - "require github.com/..."
    build_commands:
      - "go build"
      - "go build ./..."
    test_commands:
      - "go test"
      - "go test ./..."

  Rust:
    config_files:
      - "Cargo.toml"
    indicators:
      - "[dependencies]"
      - "[bin]"
    build_commands:
      - "cargo build"
      - "cargo build --release"
    test_commands:
      - "cargo test"

  Ruby:
    config_files:
      - "Gemfile"
    indicators:
      - "gem 'rails' OR 'sinatra' OR 'hanami'"
    build_commands:
      - "bundle exec rake build"
    test_commands:
      - "bundle exec rspec"
      - "bundle exec rake test"

  PHP:
    config_files:
      - "composer.json"
    indicators:
      - "\"laravel/framework\" OR \"symfony/*\""
    build_commands:
      - "composer install"
      - "composer build"
    test_commands:
      - "phpunit"
      - "composer test"
```

#### 3.3 CI/CD Detection

```yaml
ci_cd_patterns:
  GitHub_Actions:
    config_files:
      - ".github/workflows/*.yml"
      - ".github/workflows/*.yaml"
    indicators:
      - "on: [push, pull_request]"
      - "jobs: { build, test, deploy }"
      - "runs-on: ubuntu-latest"
    platform: "GitHub Actions"

  GitLab_CI:
    config_files:
      - ".gitlab-ci.yml"
    indicators:
      - "stages: [build, test, deploy]"
      - "image: node:latest"
    platform: "GitLab CI"

  Jenkins:
    config_files:
      - "Jenkinsfile"
    indicators:
      - "pipeline { agent any }"
      - "stage('Build') {"
    platform: "Jenkins"

  Cloud_Build:
    config_files:
      - "cloudbuild.yaml"
      - "cloudbuild.yml"
    indicators:
      - "steps: [ name: 'node' ]"
      - "- name: 'gcr.io/cloud-builders/docker'"
    platform: "Google Cloud Build"

  Azure_Pipelines:
    config_files:
      - "azure-pipelines.yml"
    indicators:
      - "trigger: [ main ]"
      - "pool: vmImage: 'ubuntu-latest'"
    platform: "Azure Pipelines"

  CircleCI:
    config_files:
      - ".circleci/config.yml"
    indicators:
      - "version: 2.1"
      - "jobs: { build }"
    platform: "CircleCI"
```

#### 3.4 Platform Detection

```yaml
platform_patterns:
  Docker:
    config_files:
      - "Dockerfile"
      - "docker-compose.yml"
      - "docker-compose.yaml"
    indicators:
      - "FROM node: OR FROM python: OR FROM openjdk:"
      - "version: '3' services:"
    classification: containerized

  Kubernetes:
    config_files:
      - "kubernetes/*.yaml"
      - "k8s/*.yaml"
      - "helm/*.yaml"
    indicators:
      - "apiVersion: apps/v1"
      - "kind: Deployment"
      - "kind: Service"
    classification: orchestrated

  Terraform:
    config_files:
      - "terraform/*.tf"
      - "infrastructure/*.tf"
    indicators:
      - "resource 'aws_instance'"
      - "resource 'google_compute_instance'"
    classification: infrastructure_as_code

  Web_Frontend:
    indicators:
      - "package.json with react/vue/angular"
      - "webpack/vite/rollup config"
      - "static asset build"
    classification: web

  Backend_Service:
    indicators:
      - "server framework (express, spring boot, django)"
      - "API route definitions"
      - "database migrations"
    classification: api

  Worker_Batch:
    indicators:
      - "job queue library (bull, celery, sidekiq)"
      - "cron/scheduler configuration"
    classification: worker

  Mobile:
    indicators:
      - "react-native / flutter / swift / kotlin"
      - "mobile build configuration"
    classification: mobile

  Desktop:
    indicators:
      - "electron / tauri / javafx configuration"
    classification: desktop
```

#### 3.5 Apply Redaction to Configs

```yaml
config_redaction:
  .env_files:
    - "Redact all values, keep keys only"
    - "Format: KEY=[REDACTED]"

  ci_cd_configs:
    - "Redact secrets, tokens, credentials"
    - "Redact API keys and access tokens"
    - "Redact registry credentials"

  docker_configs:
    - "Redact registry credentials"
    - "Redact ENV values with sensitive data"

  k8s_configs:
    - "Redact Secret values"
    - "Redact ConfigMap sensitive values"

  cloud_configs:
    - "Redact access keys"
    - "Redact connection strings"
    - "Redact account IDs"

  progress_reporting:
    phase_complete:
      - "Phase 3 complete: Filesystem audit"
      - "  Duration: {actual_time}s"
      - "  Build systems: {build_count}"
      - "  CI/CD pipelines: {cicd_count}"
      - "  Platform targets: {platform_count}"
```

### Phase 4: Platform and Deployment Classification (120s timeout)

**Objective**: Classify platform targets and deployment surfaces.

#### 4.1 Platform Classification Rules

```yaml
classification_rules:
  web_frontend:
    required:
      - "Frontend framework detected (react/vue/angular)"
      - "Build process for static assets"
    evidence:
      - "package.json scripts.build"
      - "webpack/vite/rollup config"
    confidence: high

  backend_api:
    required:
      - "Server framework detected"
      - "API route definitions"
    evidence:
      - "express / spring boot / django / fastapi"
      - "API route handlers"
    confidence: high

  worker_batch:
    required:
      - "Job queue library OR scheduler"
    evidence:
      - "bull / celery / sidekiq"
      - "cron configuration"
    confidence: high

  containerized:
    required:
      - "Dockerfile OR docker-compose.yml"
    evidence:
      - "Docker build configuration"
      - "Container orchestration"
    confidence: high

  orchestrated:
    required:
      - "Kubernetes manifests OR Helm charts"
    evidence:
      - "Deployment/Service objects"
      - "Helm values"
    confidence: high

  cloud_infrastructure:
    required:
      - "Terraform OR Cloud Formation OR Pulumi"
    evidence:
      - "Infrastructure as code"
      - "Cloud provider resources"
    confidence: high
```

#### 4.2 Deployment Surface Detection

```yaml
deployment_surfaces:
  ci_cd_platform:
    detection:
      - "GitHub Actions"
      - "GitLab CI"
      - "Jenkins"
      - "Cloud Build"
      - "Azure Pipelines"
    evidence: "CI config files"

  release_path:
    detection:
      - "Artifact publishing (npm, maven, docker registry)"
      - "Deployment commands"
      - "Environment promotion"
    evidence: "CI pipeline definitions"

  versioning_strategy:
    detection:
      - "Semantic versioning"
      - "Git tags"
      - "Automated versioning"
    evidence: "Build configs + CI pipelines"

  cache_output:
    file: "platform_detection_cache.json"
    content:
      timestamp: "{ISO8601}"
      platforms:
        - type: web | api | worker | container | orchestrated
          indicators: []
          evidence_source: filesystem | graph_mcp
          confidence: high | medium | low

  progress_reporting:
    phase_complete:
      - "Phase 4 complete: Platform classification"
      - "  Duration: {actual_time}s"
      - "  Platforms detected: {platform_count}"
```

### Phase 5: API Dependency Guardrails (240s timeout)

**Objective**: Detect API boundary violations and architectural coupling issues.

#### 5.1 Rule W1: API Direct Driver Access

```yaml
rule_w1_api_direct_driver_access:
  condition:
    - "API/controller/handler code imports low-level DB driver"
    - "Same file performs direct query/execute/connect operations"

  detection_filesystem:
    - "rg 'import.*mysql|require.*pg|from pymongo' in controllers/"
    - "rg '\.query\(|\.execute\(|SELECT.*FROM' in API files"

  detection_graph_mcp:
    - "Find API entry functions (list_up_entrypoint)"
    - "Find driver symbols (search_functions for 'mysql|pg|redis')"
    - "Use find_paths between API and driver nodes"
    - "Check for direct path without repository hop"

  severity:
    high:
      - "Both driver import and query operation in API file"
      - "Direct call path from API to driver without abstraction"
    medium:
      - "Only driver import in API file"
      - "Query operation but no direct import (shared module)"

  why_it_matters:
    - "Bypasses service/repository abstraction"
    - "Makes transport layer tightly coupled to persistence details"
    - "Harder to test and mock"
    - "Database schema changes propagate to API layer"

  recommendation:
    - "Introduce repository/service abstraction layer"
    - "Move all database operations to repository layer"
    - "API should only call service methods"

  example:
    violation: |
      # ❌ Violation: API directly queries database
      @app.route('/users/<id>')
      def get_user(id):
          conn = mysql.connect()
          cursor = conn.cursor()
          cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
          return jsonify(cursor.fetchone())

    fixed: |
      # ✅ Fixed: API calls repository
      @app.route('/users/<id>')
      def get_user(id):
          user = user_repository.find_by_id(id)
          return jsonify(user.to_dict())
```

#### 5.2 Rule W2: Service Layer Framework Coupling

```yaml
rule_w2_service_layer_framework_coupling:
  condition:
    - "Service/domain/usecase layer imports web framework symbols"

  detection_filesystem:
    - "rg 'from flask import|from django.http|import express' in services/"
    - "rg '@app\.|@router\.' in service layer"

  detection_graph_mcp:
    - "Find service/domain functions (search_functions for 'service|domain|usecase')"
    - "Find framework imports (search_by_code for 'flask|django|express')"
    - "Check if service nodes have framework dependencies"

  severity:
    medium:
      - "Framework symbols imported in business logic"
      - "Request/response objects passed to service layer"

  why_it_matters:
    - "Business logic becomes framework-dependent"
    - "Harder to test and migrate frameworks"
    - "Violates clean architecture principles"
    - "Business logic cannot be reused outside HTTP context"

  recommendation:
    - "Use request/response DTOs instead of framework objects"
    - "Keep framework dependencies at edges only"
    - "Service layer should use domain objects"

  example:
    violation: |
      # ❌ Violation: Service imports Flask
      from flask import request

      class UserService:
          def create_user(self):
              data = request.json  # Framework dependency
                  ...

    fixed: |
      # ✅ Fixed: Service uses DTO
      class UserService:
          def create_user(self, user_dto):
              # Pure business logic
                  ...
```

#### 5.3 Rule W3: Controller-to-Driver Call Path

```yaml
rule_w3_controller_to_driver_call_path:
  condition:
    - "Call path exists from API entry function to driver symbol"
    - "No intermediate service/repository abstraction node observed"

  detection_graph_mcp:
    required_functions:
      - list_up_entrypoint: "Find API entry points"
      - search_functions: "Find driver symbols"
      - find_paths: "Trace call paths"

    workflow:
      1. "Find all API entry points"
      2. "Find all driver symbols (mysql, pg, redis, etc.)"
      3. "For each API node, find paths to driver nodes"
      4. "Check if path has service/repository hop"
      5. "Flag high risk if no intermediate abstraction"

  severity:
    high:
      - "Direct call path from API to driver"
      - "No service/repository abstraction in path"

  why_it_matters:
    - "Indicates architectural boundary violation in runtime flow"
    - "Confirmed coupling at execution level"
    - "Not just import, but actual call chain"

  recommendation:
    - "Introduce repository layer between API and driver"
    - "All database operations should go through repository"
    - "API should call service → repository → driver"

  example_call_path:
    violation: |
      # ❌ Violation: Direct call path
      API: UserController.createUser()
        ↓
      Driver: MySQLConnection.execute()
      # No repository abstraction

    fixed: |
      # ✅ Fixed: Proper abstraction layers
      API: UserController.createUser()
        ↓
      Service: UserService.createUser()
        ↓
      Repository: UserRepository.save()
        ↓
      Driver: MySQLConnection.execute()
```

#### 5.4 API Warning Output Format

```yaml
warning_payload:
  required_fields:
    warning_id: "W1-API-001"
    severity: "high | medium | low"
    path: "src/controllers/UserController.js"
    title: "API directly queries database"
    evidence:
      - "Import: require('mysql')"
      - "Operation: connection.query('SELECT * FROM users')"
      - "Graph path: UserController → MySQLConnection.execute"
    evidence_type: "graph_mcp | filesystem"
    recommendation: "Introduce UserRepository abstraction"

  example_warnings:
    - warning_id: "W1-API-001"
      severity: high
      path: "src/controllers/UserController.js"
      title: "API directly queries database"
      evidence:
        - "Driver import detected: require('mysql')"
        - "Direct query: connection.query(...)"
      evidence_type: graph_mcp
      recommendation: "Move database operations to UserRepository"

    - warning_id: "W2-SVC-001"
      severity: medium
      path: "src/services/UserService.js"
      title: "Service layer coupled to Flask framework"
      evidence:
        - "Framework import: from flask import request"
        - "Usage: data = request.json"
      evidence_type: filesystem
      recommendation: "Use request DTOs instead of framework objects"

    - warning_id: "W3-PATH-001"
      severity: high
      path: "UserController → MySQLConnection"
      title: "Direct controller-to-driver call path"
      evidence:
        - "Graph path: UserController.createUser → MySQLConnection.execute"
        - "No service/repository hop detected"
      evidence_type: graph_mcp
      recommendation: "Introduce service and repository layers"

  fallback:
    on_mcp_unavailable: "Use filesystem-only pattern matching, reduced accuracy"
    on_timeout: "Return partial warnings, document incomplete analysis"

  progress_reporting:
    phase_complete:
      - "Phase 5 complete: API dependency guardrails"
      - "  Duration: {actual_time}s"
      - "  High severity warnings: {high_count}"
      - "  Medium severity warnings: {medium_count}"
      - "  Low severity warnings: {low_count}"
```

### Phase 6: Audit Artifact Generation (60s timeout)

**Objective**: Generate comprehensive audit report with all findings.

#### 6.1 Report Structure

```yaml
audit_report_sections:
  snapshot:
    - repository: string
    - commit/branch: string
    - scan_date: ISO8601
    - audit_scope: string

  technology_matrix:
    columns:
      - area: "Language/runtime | Framework | Package/build | CI/CD | Deployment"
      - detected: string
      - evidence: paragraph_id | node_id | file_path
      - confidence: high | medium | low

    example_row:
      - area: "Language/runtime"
        detected: "Node.js 18.x"
        evidence: "package.json: engines"
        confidence: high

  build_and_test_commands:
    columns:
      - ecosystem: "Node | Python | Java | etc."
      - command: string
      - source: package.json | pyproject | etc.
      - status: confirmed | inferred

    example_row:
      - ecosystem: "Node"
        command: "npm run build"
        source: "package.json: scripts.build"
        status: confirmed

  platform_targets:
    - web: boolean
    - api: boolean
    - worker/batch: boolean
    - mobile: boolean
    - desktop: boolean
    - container/kubernetes: boolean

    example:
      - web: true
      - api: true
      - container: true
      - orchestrated: true

  risks_and_unknowns:
    columns:
      - topic: string
      - risk: low | medium | high
      - evidence_gap: string
      - recommended_probe: string

    example_row:
      - topic: "Build reproducibility"
        risk: medium
        evidence_gap: "No lock file found in repository"
        recommended_probe: "Check if package-lock.json is gitignored"

  api_dependency_warnings:
    columns:
      - severity: high | medium | low
      - warning: string
      - path: string
      - evidence_type: graph_mcp | filesystem
      - recommendation: string

    example_row:
      - severity: high
        warning: "API directly queries database"
        path: "src/controllers/UserController.js"
        evidence_type: graph_mcp
        recommendation: "Introduce UserRepository abstraction"
```

#### 6.2 Output Files

```yaml
output_files:
  tech_build_audit_json:
    format: JSON
    content:
      - technology_matrix: {}
      - build_commands: []
      - platform_targets: {}
      - api_warnings: []
      - evidence_sources: []
    purpose: "Machine-readable audit data"

  tech_build_audit_md:
    format: Markdown
    content:
      - "# Tech Build Audit"
      - "## Snapshot"
      - "## Technology Matrix"
      - "## Build and Test Commands"
      - "## Platform Targets"
      - "## Risks and Unknowns"
      - "## API Dependency Warnings"
    purpose: "Human-readable audit summary"

  mcp_build_evidence_md:
    format: Markdown (optional)
    content:
      - "# MCP Build Evidence"
      - "## mind_mcp Queries"
      - "## graph_mcp Traces"
      - "## Evidence Citations"
    purpose: "Query logs and extracted facts"

  api_dependency_warnings_json:
    format: JSON (optional)
    content:
      - warnings: []
      - summary:
          - high: integer
          - medium: integer
          - low: integer
    purpose: "Detailed API warnings for tooling"

  progress_reporting:
    final_summary:
      - "Tech build audit complete"
      - "Total duration: {total_duration}s"
      - "Build systems detected: {build_count}"
      - "CI/CD pipelines: {cicd_count}"
      - "Platform targets: {platform_count}"
      - "API warnings: {warning_count} ({high_count} high, {medium_count} medium)"
      - "Evidence coverage: {mcp_coverage}%"
      - "Output: {output_files}"
```

## 3. Filesystem Fallback Mode (MCP Unavailable)

**Trigger**: All MCP checks fail or timeout

**Mode**: filesystem_audit_with_reduced_confidence

### 3.1 Build System Detection (Filesystem Only)

```bash
# Use filesystem patterns for build detection
find . -name "package.json" -o -name "pom.xml" -o -name "build.gradle" -o -name "go.mod"
find . -name "requirements.txt" -o -name "pyproject.toml" -o -name "Cargo.toml"
find . -name "Gemfile" -o -name "composer.json"

# Extract build commands
rg '"scripts":\s*\{' -A 10 package.json  # Node
rg '<build>' -A 20 pom.xml                # Maven
rg 'tasks\s*\{' -A 10 build.gradle       # Gradle
```

### 3.2 CI/CD Detection (Filesystem Only)

```bash
# Find CI/CD configs
find . -name ".github/workflows/*.yml" -o -name ".gitlab-ci.yml"
find . -name "Jenkinsfile" -o -name "cloudbuild.yaml"
find . -name "azure-pipelines.yml" -o -name ".circleci/config.yml"
```

### 3.3 Platform Detection (Filesystem Only)

```bash
# Find platform indicators
find . -name "Dockerfile" -o -name "docker-compose.yml"
find . -path "*/kubernetes/*.yaml" -o -path "*/helm/*.yaml"
find . -name "terraform/*.tf"
```

### 3.4 API Dependency Analysis (Skipped)

```yaml
api_dependency_analysis:
  status: "SKIPPED"
  reason: "Requires graph_mcp for accurate path tracing"

  alternatives:
    - "Use filesystem pattern matching (reduced accuracy)"
    - "Manual code review required"
    - "Mark as [MANUAL_REVIEW_REQUIRED]"

  pattern_matching_fallback:
    - "rg 'import.*mysql|require.*pg' controllers/"
    - "rg 'from flask import|from django.http' services/"
    - "Limited to import analysis only"
    - "Cannot trace call paths"
```

### 3.5 Conservative Evidence Rules

```yaml
filesystem_evidence_rules:
  build_commands:
    - "Extract from config files only"
    - "Mark as [INFERRED_FROM_CONFIG]"
    - "Confidence: MEDIUM"

  ci_cd_pipelines:
    - "Detect from CI config files only"
    - "Mark as [CONFIG_ONLY]"
    - "Confidence: HIGH"

  platform_targets:
    - "Detect from file patterns only"
    - "Mark as [FILESYSTEM_DETECTED]"
    - "Confidence: MEDIUM"

  api_warnings:
    - "Skipped (requires graph_mcp)"
    - "Document as [ANALYSIS_UNAVAILABLE]"
    - "Recommend manual review"

disclaimer_text: |
  ⚠️ **WARNING**: This audit was generated in FILESYSTEM-ONLY MODE due to MCP unavailability.

  **Limitations**:
  - Build commands inferred from configs (may be incomplete)
  - CI/CD detection limited to config files only
  - Platform detection based on file patterns only
  - API dependency analysis NOT available (requires graph_mcp)
  - No semantic code analysis performed

  **Required Actions**:
  - Manual verification of all build commands
  - Manual verification of CI/CD pipeline behavior
  - Manual code review for API dependency violations
  - Manual verification of platform classification

  **Do NOT use** for:
  - Critical deployment decisions without review
  - Migration planning without verification
  - Architecture analysis without manual review
```

## 4. Performance Optimization Strategies

### 4.1 Context Control for Large Codebases

```yaml
context_control_strategy:
  query_by_ecosystem:
    rule: "Use ecosystem-specific terms, not generic terms"
    example: "dockerfile NOT 'file'"
    benefit: "Reduces false positives by 10-100x"

  limit_results:
    rule: "Limit to 20-50 results per query"
    if_truncated:
      - "Summarize first 20-50 results"
      - "Ask user for specific focus"
      - "Process by ecosystem, not entire project"

  batch_processing:
    rule: "Batch graph queries in groups of 10-20 nodes"
    user_confirmation: true
    prompt: "Processing {batch_size} nodes, continue?"
```

### 4.2 Caching Strategy

```yaml
cache_strategy:
  build_context_cache:
    enabled: true
    ttl: 900  # 15 minutes
    invalidation: "on_workflow_start"

  build_surface_cache:
    enabled: true
    ttl: 1200  # 20 minutes
    invalidation: "on_repo_change"

  platform_cache:
    enabled: true
    ttl: 1800  # 30 minutes
    invalidation: "on_config_change"

  api_dependency_cache:
    enabled: true
    ttl: 2400  # 40 minutes
    invalidation: "on_code_change"
```

### 4.3 Timeout Strategy

```yaml
timeout_strategy:
  mcp_call_timeout: 30s
  query_timeout: 45s
  batch_timeout: 60s
  phase_timeout:
    phase_0: 30s
    phase_1: 180s
    phase_2: 240s
    phase_3: 180s
    phase_4: 120s
    phase_5: 240s
    phase_6: 60s
  total_workflow_timeout: 1200s  # 20 minutes

  on_timeout:
    action: "return_partial_and_continue"
    log: "Timeout exceeded, returning partial results"
    add_warning: true
```

## 5. Error Handling Patterns

### 5.1 MCP Timeout Handling

```yaml
on_mcp_timeout:
  mind_mcp:
    action: "return_cached_or_empty"
    log: "mind_mcp timeout, using cached results or empty context"
    continue: true

  graph_mcp:
    action: "return_partial_or_fallback"
    log: "graph_mcp timeout, returning partial results or filesystem fallback"
    continue: true
```

### 5.2 Evidence Conflict Resolution

```yaml
conflict_resolution_rules:
  priority:
    1. "For current build configuration: Trust filesystem over mind_mcp"
    2. "For build process and intent: Trust mind_mcp over filesystem"
    3. "For code structure and dependencies: Trust graph_mcp over mind_mcp"
    4. "For platform and deployment: Trust filesystem over MCP"
    5. "For CI/CD configuration: Trust filesystem over MCP"

  on_conflict:
    action: "apply_priority_rules"
    log: "Conflict detected, applying resolution rules"
    if_unresolved:
      action: "report_both_with_disclaimer"
      format: |
        CONFLICT DETECTED:
        - mind_mcp says: {mind_mcp_claim}
        - filesystem says: {filesystem_claim}
        - Resolution: {resolution}
        Recommendation: Manual verification required
```

### 5.3 Partial Recovery Strategies

```yaml
partial_recovery:
  on_partial_results:
    action: "continue_with_partial"
    log: "Partial results retrieved, continuing with available data"

  on_missing_build_commands:
    action: "mark_as_inferred"
    log: "Build commands not explicitly documented, marked as inferred"
    add_tag: "[INFERRED]"

  on_api_analysis_skipped:
    action: "document_as_unavailable"
    log: "API dependency analysis requires graph_mcp, skipped"
    add_note: "Manual review required"
```

## 6. Integration with SKILL.md

This playbook is fully integrated with the enhanced SKILL.md (v2.0.0) and implements:

- ✅ **Security & Privacy**: Path validation, sensitive data redaction (11+ patterns)
- ✅ **Performance & UX**: Timeout configuration, progress feedback, caching
- ✅ **Reliability & Resilience**: Fallback strategy, conflict resolution, error recovery
- ✅ **Observability**: Metrics tracking, quality gates, evidence provenance

For complete details, refer to:
- `<repo_root>/tech-build-audit/SKILL.md`
- `<repo_root>/tech-build-audit/references/audit-template.md`
- `<repo_root>/tech-build-audit/references/api-warning-rules.md`
