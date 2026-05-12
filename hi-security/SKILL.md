---
name: hi-security
description: STRIDE + OWASP-based security audit with MCP-assisted code analysis and optional iterative auto-fix. Scans code using graph_mcp for structure discovery and mind_mcp for security policy context, then produces severity-ranked findings with fix recommendations. Supports audit-only and audit+fix modes. Use before releases, after sensitive feature additions, or for periodic compliance reviews.
version: 1.0.0
last_updated: 2026-05-12
hooks:
  pre:
    - name: mcp-health-check
      timeout: 10s
    - name: input-validation
      scope: [source_root, audit_scope]
      enable_redaction: true
  phase:
    scope_resolution:
      post: [progress-reporter]
    stride_analysis:
      pre: [mcp-health-check]
      post: [progress-reporter]
    dependency_audit:
      post: [progress-reporter]
    secret_detection:
      post: [progress-reporter]
    owasp_mapping:
      post: [progress-reporter]
    fix_execution:
      post: [progress-reporter, timeout-handler]
    report_generation:
      post: [progress-reporter]
    all_phases:
      post: [progress-reporter]
  post:
    - name: output-redaction
      apply_to: [audit_report, findings_log]
    - name: cleanup-handler
      paths: [security-audit-data/]
      keep: [*.json, *.md]
---

# HI Security

STRIDE + OWASP security audit with MCP-assisted code analysis, dependency scanning, secret detection, and optional iterative auto-fix with comprehensive security hardening.

## When To Use

- Before a release or major deployment
- After adding authentication, payment, or data-handling features
- Periodic security review (monthly/quarterly)
- Compliance check preparation (SOC 2, GDPR, PCI-DSS)
- After dependency updates or framework migrations
- When a vulnerability is reported in a dependency

## Avoid Using When

- Purely cosmetic changes (CSS, copy edits, documentation only)
- Repository has no user-facing code or data handling
- You only need dependency audit (use native `npm audit` / `pip-audit` directly)
- Quick code review without structured methodology

## Required Inputs

- Source root path
- Audit scope: glob pattern or target directory
- Mode: `audit` or `audit-fix`
- Optional: max fix iterations (default 10)
- Optional: focus area (`auth`, `data`, `api`, `infra`, `all`)

## Modes

| Mode | Behavior |
|------|----------|
| `audit` | Scan → categorize by severity → produce findings report |
| `audit-fix` | Scan → categorize → fix iteratively (Critical→High→Medium) → verify → report |

## Input Validation & Security

### Path Validation

```yaml
path_validation:
  - source_path must exist and be readable
  - scope must resolve to at least one source file
  - Block path traversal: reject "../" patterns
  - Character whitelist: [a-zA-Z0-9_\-./*]
  - Max length: 1000 characters
  - Audit scope limited to specified directory only
```

### Scope Validation

```yaml
scope_validation:
  mode:
    allowed_values: ["audit", "audit-fix"]
    default: "audit"

  focus_area:
    allowed_values: ["all", "auth", "data", "api", "infra"]
    default: "all"

  max_iterations:
    min: 1
    max: 50
    default: 10
```

## Performance & Operational Configuration

### Timeout Configuration

```yaml
timeouts:
  phase_0_scope_resolution_timeout: 30s
  phase_1_stride_analysis_timeout: 300s
  phase_2_dependency_audit_timeout: 120s
  phase_3_secret_detection_timeout: 60s
  phase_4_owasp_mapping_timeout: 60s
  phase_5_fix_execution_timeout: 600s
  phase_6_report_generation_timeout: 60s

  total_workflow_timeout: 1800s            # 30 minutes

  on_timeout:
    action: "return_partial_report"
    notify: "Audit incomplete due to timeout. Partial findings available."
```

### Resource Limits

```yaml
resource_limits:
  max_files_to_scan: 5000
  max_file_size: 10MB
  max_findings_per_category: 100
  max_fix_iterations: 50
```

### Caching Strategy

```yaml
cache:
  scope_cache:
    enabled: true
    ttl: 300
    file: "security_scope_cache.json"
    cache_content:
      - resolved_file_list
      - file_type_classification
    invalidation: "on_scope_change"

  findings_cache:
    enabled: true
    ttl: 600
    file: "security_findings_cache.json"
    cache_content:
      - stride_findings
      - dependency_findings
      - secret_findings
      - owasp_mapping
    invalidation: "on_workflow_start"
```

### Progress Feedback

```yaml
progress_reporting:
  phase_start:
    - "Phase {N} started: {phase_name}"
    - "  Mode: {mode}, Focus: {focus_area}"
  phase_complete:
    - "Phase {N} complete: {phase_name}"
    - "  Findings so far: Critical={c}, High={h}, Medium={m}"
  task_progress:
    - "Scanning: {file_path} ({current}/{total})"
    - "Analyzing STRIDE: {category}"
    - "Fixing: #{finding_number} of {total} ({severity})"
  final_summary:
    - "Audit complete"
    - "Files scanned: {count}"
    - "Findings: {critical}C, {high}H, {medium}M, {low}L, {info}I"
    - "Fixes applied: {fixed_count}"
```

---

## Severity Definitions

| Severity | Description | Fix Priority |
|----------|-------------|-------------|
| **Critical** | Exploitable now — data breach, RCE, or auth bypass risk | Immediate — block release |
| **High** | Exploitable with moderate effort, significant impact | This sprint |
| **Medium** | Limited exploitability or impact | Next sprint |
| **Low** | Theoretical risk, defense-in-depth improvement | Backlog |
| **Info** | Best practice suggestion, no direct risk | Optional |

---

## Orchestration Workflow

### Phase 0: Scope Resolution (30s)

```yaml
steps:
  1. Validate inputs (source path, scope, mode, focus)
  2. Expand scope glob to file list
  3. Classify files by type (source, config, test, doc)
  4. Filter in-scope files (exclude test fixtures, examples, docs)
  5. Query mind_mcp for security policy context if available
  6. Report: "Phase 0 complete: {count} files in scope"

mcp_functions_optional:
  - mind_mcp.hybrid_search [optional]
    params:
      query: "security policy compliance requirements"
      collection: "{selected_collection}"
      limit: 10
    output:
      - results: security policy docs
    expected: "Security policies and compliance requirements"
```

### Phase 1: STRIDE Analysis (5min)

```yaml
steps:
  1. For each in-scope file, analyze per STRIDE category
  2. Use graph_mcp to discover entry points, auth flows, data paths
  3. Use mind_mcp for security documentation context
  4. Record findings with file:line, category, description
  5. Report: "Phase 1 complete: {count} STRIDE findings"

stride_categories:
  spoofing:
    checks:
      - Missing authentication on endpoints
      - Weak password hashing (MD5, SHA1)
      - JWT without expiration or server-side validation
      - Missing MFA for sensitive operations
      - Default credentials present

  tampering:
    checks:
      - SQL/NoSQL string concatenation
      - Missing CSRF tokens
      - Missing input validation
      - Unsafe deserialization
      - Unrestricted HTTP methods

  repudiation:
    checks:
      - Missing auth event logging
      - Sensitive data in logs
      - Non-append-only log storage
      - Insufficient log retention

  information_disclosure:
    checks:
      - Stack traces in error responses
      - Internal IDs in API responses
      - Plaintext sensitive data
      - HTTP endpoints for sensitive operations
      - Hardcoded secrets (detailed in Phase 3)

  denial_of_service:
    checks:
      - Missing rate limiting
      - Unbounded list queries
      - Missing request timeouts
      - ReDoS-vulnerable regex patterns
      - Unbounded background job concurrency

  elevation_of_privilege:
    checks:
      - Client-side only auth checks
      - Missing horizontal privilege checks (IDOR)
      - Weak admin endpoint protection
      - Overly permissive service accounts
      - Privilege escalation without re-authentication

mcp_functions:
  - graph_mcp.explore_graph [required]
    params:
      query: "auth authenticate authorize guard middleware"
      limit: 50
    output:
      - nodes: auth-related functions
    expected: "Authentication and authorization code"

  - graph_mcp.list_up_entrypoint [required]
    params:
      file_pattern: "{scope_pattern}"
      limit: 200
    output:
      - entry_points: API endpoints
    expected: "All API entry points for auth check"

  - graph_mcp.search_functions [required]
    params:
      query: "hash bcrypt argon2 password encrypt decrypt"
      limit: 50
    output:
      - functions: crypto-related functions
    expected: "Password handling and crypto code"

  - mind_mcp.hybrid_search [optional]
    params:
      query: "authentication authorization access control security"
      collection: "{collection}"
      limit: 15
    output:
      - results: security design docs
    expected: "Security architecture documentation"

cache_output:
  file: "security_findings_cache.json"
  section: "stride_findings"
```

### Phase 2: Dependency Audit (2min)

```yaml
steps:
  1. Detect tech stack from config files (package.json, requirements.txt, go.mod, etc.)
  2. Run appropriate dependency audit tool
  3. Parse output for known vulnerabilities (CVEs)
  4. Record findings with CVE ID, severity, fix version
  5. Report: "Phase 2 complete: {count} dependency findings"

dependency_audit_commands:
  nodejs: "npm audit --json"
  python: "pip-audit --format json"
  go: "govulncheck ./..."
  ruby: "bundle audit check --update"
  java_maven: "mvn dependency-check:check"
  rust: "cargo audit"

finding_format:
  - cve: "CVE ID if available"
  - package: "Affected package name and version"
  - severity: "critical|high|medium|low"
  - fix_version: "Version with fix"
  - recommendation: "Upgrade command or workaround"
```

### Phase 3: Secret Detection (1min)

```yaml
steps:
  1. Scan all in-scope files for secret patterns
  2. Apply regex patterns from reference checklist
  3. Skip false positives in test files, examples, and placeholders
  4. Record findings with file:line, pattern matched, context
  5. Report: "Phase 3 complete: {count} secrets detected"

secret_patterns:
  - Generic API keys
  - AWS access key IDs (AKIA*)
  - JWT tokens
  - Hardcoded passwords
  - Private keys (PEM format)
  - GitHub tokens (ghp_*)
  - Stripe keys (sk_live_*, sk_test_*)
  - Bearer tokens
  - Database connection strings with credentials

false_positive_exclusions:
  - Files matching *.test.*, *.spec.*, *.example
  - Files in test/, tests/, __tests__/, fixtures/
  - Placeholder values: YOUR_KEY_HERE, <your-token>, TODO
```

### Phase 4: OWASP Top 10 Mapping (1min)

```yaml
steps:
  1. Map all STRIDE findings to OWASP Top 10 categories
  2. Map dependency audit findings to A06 (Vulnerable Components)
  3. Map secret exposures to A02 (Cryptographic Failures) or A05 (Security Misconfiguration)
  4. Add OWASP category to each finding
  5. Report: "Phase 4 complete: Findings mapped to OWASP"

owasp_categories:
  A01: "Broken Access Control"
  A02: "Cryptographic Failures"
  A03: "Injection"
  A04: "Insecure Design"
  A05: "Security Misconfiguration"
  A06: "Vulnerable and Outdated Components"
  A07: "Identification and Authentication Failures"
  A08: "Software and Data Integrity Failures"
  A09: "Security Logging and Monitoring Failures"
  A10: "Server-Side Request Forgery (SSRF)"
```

### Phase 5: Fix Execution (10min, only in audit-fix mode)

```yaml
steps:
  1. Sort findings by severity: Critical → High → Medium
  2. For each finding (up to max_iterations):
     a. Apply one targeted fix
     b. Run verification (tests, lint) to confirm no regression
     c. If verification passes: mark as fixed
     d. If verification fails: revert fix, mark as failed, continue
  3. Skip Low and Info findings (document only)
  4. Report: "Phase 5 complete: {fixed}/{attempted} fixes applied"

fix_workflow:
  per_finding:
    1. Read file at finding location
    2. Apply minimal targeted fix (not full refactor)
    3. Run verify_command from project config
    4. On pass: commit fix
    5. On fail: revert, log failure reason
    6. Advance to next finding

  fix_guard_rules:
    - Never fix more than one issue per iteration
    - Test must pass before advancing to next fix
    - Critical auth changes require manual review
    - Do not modify test files or configuration secrets
```

### Phase 6: Report Generation (1min)

```yaml
steps:
  1. Aggregate all findings by severity
  2. Generate summary statistics
  3. Format findings table with file:line references
  4. Include fix recommendations for each finding
  5. Add OWASP coverage summary
  6. Generate next-step recommendations
  7. Report: "Phase 6 complete: Audit report generated"

report_sections:
  - summary: "Files scanned, findings by severity, fix attempts"
  - findings_table: "#, Severity, Category, File:Line, Description, Recommendation"
  - owasp_coverage: "OWASP category distribution"
  - dependency_status: "CVEs found, packages affected"
  - secret_exposure: "Secrets detected, location"
  - recommendations: "Prioritized fix list"
```

---

## Fix Mode Details

When mode is `audit-fix`:

1. **Fix ordering**: Critical before High before Medium. Low and Info are document-only.
2. **One fix at a time**: Apply, verify, commit or revert before next.
3. **Verification gate**: Run project test suite after each fix. Fail = revert.
4. **Commit convention**: `security(fix-{N}): {category} — {short description}`
5. **Iteration cap**: Stop after `max_iterations` fixes even if more remain.
6. **Auth restrictions**: Changes to authentication/authorization code are flagged for manual review.

---

## Output Contract

```yaml
output_location: "{project_root}/security-audit/"

files:
  - "audit_report_{timestamp}.md"       # Full findings report
  - "audit_summary_{timestamp}.md"      # Executive summary
  - "findings_{timestamp}.json"         # Machine-readable findings
  - "fix_log_{timestamp}.md"            # Fix mode: applied fixes log
```

### Report Format

```markdown
# Security Audit Report — {ProjectName}

## Summary
- **Date**: {timestamp}
- **Mode**: {audit|audit-fix}
- **Scope**: {scope_description}
- **Files scanned**: {count}
- **Findings**: {critical}C, {high}H, {medium}M, {low}L, {info}I
- **Fixes applied**: {fixed_count} / {attempted_count}

## Findings

| # | Severity | STRIDE | OWASP | File:Line | Description | Recommendation |
|---|----------|--------|-------|-----------|-------------|----------------|
| 1 | Critical | Spoofing | A07 | auth/login.ts:42 | No rate limiting on login | Add rate-limiter middleware |

## Dependency Vulnerabilities
| Package | Version | CVE | Severity | Fix Version |
|---------|---------|-----|----------|-------------|
| ... | ... | ... | ... | ... |

## OWASP Coverage
| Category | Findings Count |
|----------|---------------|
| A01 Broken Access Control | {count} |
| ... | ... |
```

---

## Non-Negotiable Rules

- ✅ Never skip authentication checks on API endpoints
- ✅ Never recommend fixing Critical issues with Low-effort workarounds
- ✅ Every finding must include file:line reference (no vague claims)
- ✅ Secret detection matches must be verified (reduce false positives)
- ✅ Fix mode must verify after each fix — no blind batch fixing
- ✅ Auth-related fixes require manual review flag
- ✅ Never log or store detected secrets in plaintext
- ✅ Dependency audit must run for the actual detected stack

---

## Error Handling & Fallback Strategy

```yaml
preflight:
  - check: "source_path_validation"
    verify: [exists, readable, has_code]
    action_on_failure: "abort_with_error"

  - check: "scope_resolution"
    verify: [scope_has_files, files_readable]
    action_on_failure: "abort_with_error"

  - check: "mcp_capability_check"
    mind_mcp_functions: [list_qdrant_collections, hybrid_search]
    graph_mcp_functions: [list_databases, activate_project, explore_graph, list_up_entrypoint]
    action_on_failure: "continue_with_filesystem_only"

fallback:
  when: "mcp_unavailable"
  mode: "filesystem_only_audit"
  steps:
    1. Skip MCP queries for auth flow discovery
    2. Use grep/find for pattern-based code analysis
    3. Use filesystem for dependency file detection
    4. Run secret detection normally (no MCP needed)
    5. Mark MCP-dependent STRIDE checks as lower confidence

error_recovery:
  phase_0_scope_resolution:
    on_empty_scope: "abort_with_error"
  phase_1_stride_analysis:
    on_mcp_timeout: "continue_with_filesystem_patterns"
  phase_2_dependency_audit:
    on_tool_missing: "skip_and_warn"
  phase_3_secret_detection:
    on_large_file: "skip_file_and_continue"
  phase_5_fix_execution:
    on_verification_failure: "revert_fix_and_continue"
  phase_6_report_generation:
    on_partial_data: "generate_partial_report"
```

---

## Observability & Metrics

```yaml
metrics:
  audit_scope:
    - files_scanned: "total files analyzed"
    - lines_analyzed: "total lines of code"
    - scan_duration_seconds: "total analysis time"

  findings:
    - critical_count
    - high_count
    - medium_count
    - low_count
    - info_count
    - total_findings

  fix_metrics:
    - fixes_attempted
    - fixes_applied
    - fixes_failed
    - fixes_reverted
    - verification_failures

  mcp_performance:
    - mcp_calls_total
    - mcp_cache_hit_rate
```

---

## Version History & Changelog

### Version 1.0.0 (2026-05-12)

**Initial Release:**
- ✅ STRIDE-based security analysis (6 threat categories)
- ✅ OWASP Top 10 mapping for all findings
- ✅ MCP-assisted code discovery (graph_mcp for auth flows, mind_mcp for security policies)
- ✅ Dependency audit with auto-detected stack
- ✅ Secret detection with 8 regex pattern categories
- ✅ Severity-ranked findings (Critical → Info)
- ✅ Optional audit-fix mode with iterative fix + verify
- ✅ Comprehensive input validation and output redaction
- ✅ MCP fallback with filesystem-only mode
- ✅ Reference checklist (stride-owasp-checklist.md)

---

## Known Limitations

```yaml
limitations:
  analysis_scope:
    - "Static analysis only — cannot detect runtime vulnerabilities"
    - "Business logic flaws partially detected through pattern matching"
    - "Distributed system auth flows may span repositories not in scope"

  dependency_audit:
    - "Requires project-specific audit tool installed"
    - "May miss transitive dependencies without lockfile"
    - "Vendor-patched dependencies may show false CVEs"

  secret_detection:
    - "Pattern-based — may miss custom secret formats"
    - "False positives possible in comments and documentation"
    - "Cannot detect secrets in binary files"

  fix_mode:
    - "Automated fixes may require manual review for correctness"
    - "Auth-related changes are conservative (flag for review)"
    - "Fixes limited to one-at-a-time to prevent cascading failures"
```

---

## Deliverables

- `audit_report_{timestamp}.md` — Complete findings with file:line references and fix recommendations
- `audit_summary_{timestamp}.md` — Executive summary with severity distribution and OWASP coverage
- `findings_{timestamp}.json` — Machine-readable findings for integration with issue trackers
- `fix_log_{timestamp}.md` — Applied fixes log (audit-fix mode only)

---

## References

### Skill-Specific References

- `references/stride-owasp-checklist.md` — Complete STRIDE checklist, OWASP mapping, secret patterns, dependency commands
