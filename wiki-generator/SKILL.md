---
name: wiki-generator
description: Generate structured wiki documentation from source code and project documentation by combining mind_mcp knowledge retrieval with graph_mcp code structure discovery. Produces architecture overview, module reference, API reference, setup guide, and index pages in wiki-compatible markdown. Use when creating onboarding wikis, technical reference sites, or Confluence/GitHub Wiki pages from codebases.
version: 1.0.0
last_updated: 2026-05-12
hooks:
  pre:
    - name: mcp-health-check
      timeout: 10s
      required: true
    - name: input-validation
      scope: [source_root, wiki_scope]
      enable_redaction: true
  phase:
    context_discovery:
      pre: [mcp-health-check]
      post: [progress-reporter]
    structure_mapping:
      pre: [mcp-health-check]
      post: [progress-reporter]
    page_generation:
      post: [progress-reporter]
    cross_linking:
      post: [progress-reporter]
    quality_gates:
      post: [progress-reporter]
    all_phases:
      post: [progress-reporter]
  post:
    - name: output-redaction
      apply_to: [wiki_pages, wiki_index]
    - name: cleanup-handler
      paths: [wiki-data/]
      keep: [*.json, *.md]
---

# Wiki Generator

Generate structured, interlinked wiki documentation from source code and project docs using MCP-assisted discovery with comprehensive security hardening.

## When To Use

- Creating onboarding wiki for a new or existing codebase
- Building a Confluence / GitHub Wiki from source
- Generating technical reference documentation from code
- Converting project documentation into structured wiki pages
- Preparing knowledge base for team handover
- Creating architecture overview pages with auto-discovered module structure

## Avoid Using When

- You only need a single-page summary (use module-summary-report)
- You need deep tracing of specific flows (use reverse-doc-reconstruction)
- You need structural analysis only (use repo-recon)
- The project already has a well-maintained wiki
- Quick informal notes without structured formatting

## Required Inputs

- Source root path (repository or documentation directory)
- Wiki output path
- Wiki scope: `full`, `architecture-only`, `modules-only`, `api-only`, `setup-only`
- Wiki format: `github`, `confluence`, `generic-markdown`
- Optional: project name, wiki title, target audience

## Input Validation & Security

### Path Validation

```yaml
path_validation:
  - source_path must exist and be readable
  - output_path must be writable
  - Block path traversal: reject "../" patterns
  - Character whitelist: [a-zA-Z0-9_\-./]
  - Max length: 1000 characters
```

### Scope Validation

```yaml
scope_validation:
  allowed_values: ["full", "architecture-only", "modules-only", "api-only", "setup-only"]
  default: "full"

format_validation:
  allowed_values: ["github", "confluence", "generic-markdown"]
  default: "generic-markdown"
```

### Sensitive Data Redaction

```regex
# Apply before writing wiki pages
API keys:     /\b[A-Za-z0-9]{32,}\b/g → '[REDACTED]'
Passwords:    /password.*/gi → '[REDACTED]'
Tokens:       /token.*/gi → '[REDACTED]'
DB URLs:      /\b(postgresql|mongodb|redis):\/\/[^\s]+\b/gi → '$1://[REDACTED]'
Emails:       /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g → '[REDACTED]'
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  phase_0_context_discovery_timeout: 180s   # mind_mcp + graph_mcp discovery
  phase_1_structure_mapping_timeout: 240s   # Module/API structure analysis
  phase_2_page_generation_timeout: 300s     # Wiki page content generation
  phase_3_cross_linking_timeout: 120s       # Inter-page linking
  phase_4_quality_gates_timeout: 60s        # Validation

  total_workflow_timeout: 900s              # 15 minutes
```

### Resource Limits

```yaml
resource_limits:
  max_repository_size: 1GB
  max_files_to_scan: 5000
  max_modules_to_document: 50
  max_api_endpoints: 200
  max_page_size: 500KB
```

### Caching Strategy

```yaml
cache:
  context_cache:
    enabled: true
    ttl: 600
    file: "wiki_context_cache.json"
    cache_content:
      - mind_mcp_search_results
      - graph_mcp_module_inventory
      - graph_mcp_entry_points
    invalidation: "on_workflow_start"

  structure_cache:
    enabled: true
    ttl: 900
    file: "wiki_structure_cache.json"
    cache_content:
      - module_classifications
      - api_endpoint_mappings
      - dependency_graph
    invalidation: "on_repo_change"

  cache_metrics:
    track_cache_hits: true
    track_cache_misses: true
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name}"
    - "  Format: {wiki_format}, Scope: {wiki_scope}"
  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Pages: {pages_count}"
  page_progress:
    - "Generating: {page_name} ({current}/{total})"
  final_summary:
    - "Wiki generation complete"
    - "Total pages: {total_pages}"
    - "Cross-links: {link_count}"
```

## Wiki Page Structure

The generated wiki includes these page types:

| Page | Template | Source |
|------|----------|--------|
| **Index** | `templates/index.md` | Aggregated from all pages |
| **Architecture Overview** | `templates/architecture-overview.md` | mind_mcp + graph_mcp structure |
| **Module Reference** | `templates/module-reference.md` | graph_mcp module inventory (one per module) |
| **API Reference** | `templates/api-reference.md` | graph_mcp entry points + call chains |
| **Setup Guide** | `templates/setup-guide.md` | mind_mcp build docs + filesystem configs |

## Orchestration Workflow

### Phase 0: Context Discovery (3min)

```yaml
steps:
  1. Validate inputs and configure output format
  2. Query mind_mcp for architecture docs, setup guides, domain concepts
  3. Query graph_mcp for module inventory, entry points, API surfaces
  4. Scan filesystem for README, docs/, config files
  5. Build shared context map with all evidence
  6. Report: "Phase 0 complete: Context discovered"

mcp_functions:
  - mind_mcp.hybrid_search [required]
    params:
      query: "architecture overview design system modules"
      collection: "{selected_collection}"
      limit: 20
    output:
      - results: architecture documentation
    expected: "System architecture and design docs"

  - mind_mcp.hybrid_search [required]
    params:
      query: "setup installation configuration build"
      collection: "{selected_collection}"
      limit: 15
    output:
      - results: setup and build docs
    expected: "Setup and configuration guides"

  - mind_mcp.get_paragraph_text [required]
    params:
      paragraph_ids: ["{ids_from_search}"]
    output:
      - text: full content with citations
    expected: "Detailed documentation content"

  - graph_mcp.explore_graph [required]
    params:
      query: "module service component"
      limit: 100
    output:
      - nodes: modules and components
      - edges: dependencies
    expected: "Module inventory with relationships"

  - graph_mcp.list_up_entrypoint [required]
    params:
      file_pattern: "{scope_filter}"
      limit: 100
    output:
      - entry_points: API endpoints
    expected: "API surface discovery"
```

### Phase 1: Structure Mapping (4min)

```yaml
steps:
  1. Classify modules by type (service, controller, repository, utility)
  2. Map API endpoints to modules
  3. Identify dependency graph between modules
  4. Extract setup steps from documentation and configs
  5. Define wiki page hierarchy and inter-page links
  6. Report: "Phase 1 complete: Structure mapped"

wiki_hierarchy:
  index:
    children: [architecture_overview, setup_guide]
  architecture_overview:
    children: [module_reference_pages]
  module_reference:
    children: [api_reference_pages]
  api_reference:
    children: []
  setup_guide:
    children: []
```

### Phase 2: Page Generation (5min)

```yaml
steps:
  1. Generate Index page with page hierarchy and summaries
  2. Generate Architecture Overview with diagram (Mermaid)
  3. Generate Module Reference pages (one per module)
  4. Generate API Reference pages (grouped by module)
  5. Generate Setup Guide with step-by-step instructions
  6. Include MCP evidence tags in all claims
  7. Report: "Phase 2 complete: {count} pages generated"

page_content_rules:
  - Every claim must have evidence source tag (mind_mcp, graph_mcp, filesystem)
  - Architecture diagram must be Mermaid format for wiki compatibility
  - Module pages must include purpose, dependencies, key symbols
  - API pages must include endpoint, method, parameters, response
  - Setup pages must include verified commands from build configs
```

### Phase 3: Cross-Linking (2min)

```yaml
steps:
  1. Link module pages to their dependencies
  2. Link API pages to their parent modules
  3. Add "See Also" sections with relevant cross-references
  4. Update Index with complete page tree
  5. Report: "Phase 3 complete: {link_count} cross-links created"

linking_rules:
  - module_a depends_on module_b → link from module_a page to module_b page
  - API endpoint belongs_to module → link from API page to module page
  - Architecture overview references module → link to module page
```

### Phase 4: Quality Gates (1min)

```yaml
steps:
  1. Validate all pages have required sections
  2. Check all cross-links resolve
  3. Verify MCP evidence coverage
  4. Generate quality report
  5. Report: "Phase 4 complete: Quality validated"

quality_gates:
  - every_page_has_title: true
  - every_claim_has_source: true
  - cross_links_resolve: true
  - mermaid_diagrams_valid: true
  - minimum_evidence_coverage: 60%
  - no_sensitive_data_leaked: true
```

## Output Contract

```yaml
output_location: "{output_path}/wiki/"

pages:
  - "index.md"
  - "architecture-overview.md"
  - "setup-guide.md"
  - "modules/{module_name}.md"          # One per module
  - "api/{module_name}-api.md"          # One per module with APIs

format_specific:
  github:
    - Standard GitHub Flavored Markdown
    - [[wiki-links]] for cross-references
  confluence:
    - Confluence Storage Format compatible markdown
    - [Page Title](link) for cross-references
  generic-markdown:
    - Standard markdown with relative links
    - [Page Title](./page.md) for cross-references
```

## Non-Negotiable Rules

- ✅ Never invent modules or APIs without code evidence
- ✅ Every wiki claim must have source tag (mind_mcp, graph_mcp, filesystem)
- ✅ Architecture diagram must reflect actual code structure
- ✅ All cross-links must resolve to existing pages
- ✅ Setup commands must be verified against actual config files
- ✅ Sensitive data must be redacted before writing wiki pages

## Error Handling & Fallback Strategy

```yaml
preflight:
  - check: "source_path_validation"
    verify: [exists, readable, has_code_or_docs]
    action_on_failure: "abort_with_error"

  - check: "output_path_validation"
    verify: [writable, sufficient_space]
    action_on_failure: "abort_with_error"

  - check: "mcp_capability_check"
    mind_mcp_functions: [list_qdrant_collections, hybrid_search, get_paragraph_text]
    graph_mcp_functions: [list_databases, activate_project, explore_graph, list_up_entrypoint]
    action_on_failure: "fallback_to_filesystem_only"

fallback:
  when: "mcp_unavailable"
  mode: "filesystem_only_wiki"
  steps:
    1. Skip MCP queries
    2. Use README, docs/, config files for content
    3. Use grep/find for module structure discovery
    4. Mark all claims with confidence: LOW
    5. Add disclaimer to generated wiki pages

error_recovery:
  phase_0_context_discovery:
    on_mcp_timeout:
      action: "return_cached_or_partial"
      continue: true
  phase_1_structure_mapping:
    on_graph_timeout:
      action: "filesystem_module_scan"
      continue: true
  phase_2_page_generation:
    on_generation_failure:
      action: "skip_page_and_continue"
      log: "Failed to generate {page}, continuing"
  phase_3_cross_linking:
    on_unresolved_link:
      action: "mark_as_unresolved"
      continue: true
  phase_4_quality_gates:
    on_threshold_not_met:
      action: "report_gaps_and_continue"
      add_warning: true
```

## Observability & Metrics

```yaml
metrics:
  wiki_stats:
    - total_pages: "count of generated pages"
    - total_cross_links: "count of inter-page links"
    - total_diagrams: "count of Mermaid diagrams"

  evidence_quality:
    - total_claims: "total factual statements in wiki"
    - mcp_sourced: "claims with MCP evidence"
    - filesystem_sourced: "claims from filesystem"
    - evidence_coverage_pct: "mcp_sourced / total_claims"

  generation_performance:
    - pages_per_second: "generation throughput"
    - largest_page_bytes: "max page size"
    - template_usage: "templates applied vs custom"
```

## Version History & Changelog

### Version 1.0.0 (2026-05-12)

**Initial Release:**
- ✅ Structured wiki page generation (Index, Architecture, Module, API, Setup)
- ✅ MCP-assisted content discovery (mind_mcp + graph_mcp)
- ✅ Multi-format support (GitHub Wiki, Confluence, generic markdown)
- ✅ Automatic cross-linking based on module dependencies
- ✅ Mermaid diagram generation for architecture
- ✅ Input validation and sensitive data redaction
- ✅ MCP fallback with filesystem-only mode
- ✅ Wiki page templates for all page types
- ✅ Template-based bootstrap script

## Known Limitations

```yaml
limitations:
  mcp_dependent:
    - "Best results require mind_mcp + graph_mcp"
    - "Filesystem-only mode produces lower quality wiki"

  wiki_scope:
    - "Generated wiki reflects static code structure, not runtime behavior"
    - "Module discovery accuracy depends on graph_mcp parser quality"
    - "Best support: Python, JavaScript, TypeScript, Java"

  formatting:
    - "Confluence format may need manual adjustment for complex layouts"
    - "Large repositories may produce very large wiki pages"
```

## Deliverables

- `wiki/index.md` — Wiki home page with full page tree
- `wiki/architecture-overview.md` — System architecture with Mermaid diagram
- `wiki/setup-guide.md` — Step-by-step setup instructions
- `wiki/modules/*.md` — Module reference pages with dependencies
- `wiki/api/*.md` — API reference pages with endpoints
- `wiki/wiki_quality_report.md` — Evidence coverage and quality metrics

## References

### Skill-Specific References

- `references/wiki-page-template.md` — Standard wiki page structure

### Templates

- `templates/index.md` — Wiki index page template
- `templates/architecture-overview.md` — Architecture overview template with Mermaid diagram
- `templates/module-reference.md` — Module reference page template
- `templates/api-reference.md` — API reference page template
- `templates/setup-guide.md` — Setup guide template

### Scripts

- `scripts/wiki_bootstrap.py` — Bootstrap wiki/ directory and copy page templates
