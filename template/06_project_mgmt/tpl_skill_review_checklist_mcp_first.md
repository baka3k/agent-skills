# Checklist Review Skill (MCP-First, Scored) — `{skill_name}`

## 1) Thong tin Review

| Muc | Gia tri |
| --- | --- |
| Reviewer | `{name}` |
| Ngay review | `{YYYY-MM-DD}` |
| Skill | `{skill_name}` |
| Pham vi review | `SKILL.md`, `references/*`, `.github/copilot-instructions.md` |
| Nguon check runtime MCP | `{list_mcp_functions output or runtime reference}` |
| Review duration | `{X} phut` |
| Reviewer confidence | `high|medium|low` |

---

## 2) Quy trinh Review nhanh (5-10 phut)

### 2.1 Quick Scan (2 phut - Start here!)
```
☐ Check "Use when..." co WHEN + WHEN NOT
☐ Verify MCP functions exist (run: list_mcp_functions)
☐ Confirm fallback exists cho MCP failures
☐ Look for security keywords: "secret", "password", "token", "PII"
☐ Check SKILL.md vs references/* consistency
```

### 2.2 Auto-Fail Check (Don't waste time if you see these)
```
❌ No MCP function mapping
❌ Outdated MCP params
❌ Exposes secrets/PII
❌ Destructive ops without safeguards
```

### 2.3 Full Review (5-10 phut - if quick scan passes)
1. Doc `SKILL.md` va score Section A (Clarity)
2. Doc `references/*` va score Section B (MCP Mapping)
3. Score Section C (Reliability) + F (Security)
4. Doi chieu consistency va score Section D
5. Score Section E (Operability) + G (Performance) + H (Maintainability)
6. Danh dau critical/major/minor issues
7. Generate action items va final status

---

## 3) Rubric cham diem (120 diem)

### 3.1 Scoring Guide (Objective Criteria)

**Score Levels:**
- **100%**: Dat day du - tat ta cac requirements duoc thuc hien chat luong cao
- **50%**: Dat mot phan - co requirements nhung thieu hoac chat luong trung binh
- **0%**: Khong dat - missing requirements hoac chat luong kem

---

### A. Clarity & Completeness (20/120)

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| A1 | "Use when..." ro rang | 5 | WHEN + WHEN NOT rõ, 1-2 câu, specific triggers | Có WHEN thiếu WHEN NOT, hoặc 3-4 câu | Qua mơ, dài >4 câu, hoặc missing | `{0..5}` |
| A2 | Workflow chinh | 5 | ≤ 7 buoc, hanh dong cu the | 8-10 buoc hoặc tên hơi chung chung | >10 buoc hoặc tên vague | `{0..5}` |
| A3 | Input/output spec | 5 | Mỗi bước có I/O ngắn gọn, rõ ràng | Có I/O nhưng chưa đầy đủ | Thiếu I/O hoặc quá dài | `{0..5}` |
| A4 | Terminology | 5 | Thuật ngữ khó có định nghĩa ngắn hoặc ví dụ | Có một số định nghĩa | Thiếu định nghĩa hoặc ví dụ | `{0..5}` |

**Examples A1 (Use when...):**
- ✅ **100%**: "Use when onboarding to new codebase OR preparing architecture review. NOT for simple bug fixes or isolated file changes."
- ⚠️ **50%**: "Use when you need to understand codebase structure and build systems" (thiếu WHEN NOT)
- ❌ **0%**: "Use this skill to help with code stuff"

---

### B. MCP Integration Quality (30/120)

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| B1 | Task → MCP mapping | 8 | Phase-level mapping, required/optional, param specs | Có mapping nhưng thiếu required/optional hoặc params | Missing mapping hoặc chỉ mention MCP names | `{0..8}` |
| B2 | Function validity | 6 | Tất cả functions/params khop runtime API hiện tại | Có 1-2 functions/params outdated | Nhiều functions/params sai hoặc không tồn tại | `{0..6}` |
| B3 | Preflight check | 5 | Có step validate MCP capability trước khi call | Có mention nhưng chưa cụ thể | Thiếu preflight check | `{0..5}` |
| B4 | Query mẫu + output | 5 | Có query example và output format kỳ vọng | Có query hoặc output nhưng chưa rõ | Thiếu cả hai | `{0..5}` |
| B5 | Guardrails | 3 | Có limit/batch/module scoping rõ ràng | Có một số guardrails | Thiếu guardrails | `{0..3}` |
| B6 | End-to-end flow | 3 | MCP call sequence logic, có error handling | Có flow nhưng chưa tối ưu | Flow rời rạc hoặc khó follow | `{0..3}` |

**Examples B1 (Task → MCP mapping):**
- ✅ **100%**: "Phase 1: mind_mcp.get_project_context() [required] + graph_mcp.get_module_inventory() [required]. Phase 2: graph_mcp.analyze_dependencies(module) [optional, if complex]"
- ⚠️ **50%**: "Use mind_mcp and graph_mcp in phase 1" (thiếu required/optional và params)
- ❌ **0%**: "We use MCP tools"

---

### C. Reliability & Resilience (20/120)

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| C1 | Fallback strategy | 6 | Fallback rõ ràng: degraded mode + alternative tools | Có fallback nhưng chưa đầy đủ | Thiếu fallback | `{0..6}` |
| C2 | Confidence rules | 5 | Co rule provenance: mind_mcp|graph_mcp|filesystem | Có một số confidence levels | Thiếu confidence indicators | `{0..5}` |
| C3 | Conflict resolution | 5 | Co rule khi mind vs graph evidence bị lệch | Có một số conflict handling | Thiếu conflict resolution | `{0..5}` |
| C4 | Anti-hallucination | 4 | Không khẳng định nếu thiếu evidence | Có một số safeguards | Thiếu anti-hallucination rules | `{0..4}` |

**Examples C1 (Fallback strategy):**
- ✅ **100%**: "If MCP unavailable: (1) Use filesystem tools + (2) Manual doc review + (3) Log degraded mode + (4) Notify user of limitations"
- ⚠️ **50%**: "Use filesystem tools if MCP fails" (thiếu degraded mode và notification)
- ❌ **0%**: "If MCP fails, give up"

---

### D. Consistency & Alignment (15/120)

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| D1 | SKILL.md vs references/* | 8 | Không có mâu thuẫn workflow + MCP functions | Có 1-2 inconsistencies nhỏ | Nhiều mâu thuẫn lớn | `{0..8}` |
| D2 | Copilot instructions sync | 4 | Intent/flow đồng bộ hoàn toàn | Có một số misalignments | Thiếu alignment | `{0..4}` |
| D3 | Cross-skill consistency | 3 | Terminology và patterns consistent với other skills | Có một số inconsistencies | Thiếu consistency | `{0..3}` |

---

### E. Operability (10/120)

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| E1 | Review efficiency | 5 | Reviewer có thể kết luận trong 5-10 phút | Cần 10-20 phút | >20 phút hoặc khó kết luận | `{0..5}` |
| E2 | Quality gates | 3 | Có clear criteria và next actions cụ thể | Có một số gates | Thiếu quality gates | `{0..3}` |
| E3 | Actionable feedback | 2 | Feedback cụ thể, có priority và effort estimates | Feedback chung chung | Thiếu actionable feedback | `{0..2}` |

---

### F. Security & Privacy (10/120) **[NEW - CRITICAL]**

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| F1 | Input validation | 3 | Validate + sanitize: paths, queries, params | Có một số validation | Thiếu validation | `{0..3}` |
| F2 | Sensitive data handling | 3 | Redaction rules cho secrets/PII, detection logic | Có một số handling | Thiếu sensitive data protection | `{0..3}` |
| F3 | Access boundaries | 2 | File/module scope checks, permission limits | Có một số boundaries | Thiếu access controls | `{0..2}` |
| F4 | Audit logging | 2 | What to log vs redact specified | Có một số logging guidance | Thiếu logging guidance | `{0..2}` |

**Examples F1 (Input validation):**
- ✅ **100%**: "Validate user input: (1) Block '../' in paths, (2) Limit query length to 1000 chars, (3) Sanitize special chars, (4) Whitelist allowed modules"
- ⚠️ **50%**: "Check for valid paths" (quá chung chung)
- ❌ **0%**: No validation mentioned

**Examples F2 (Sensitive data):**
- ✅ **100%**: "Redact patterns: API keys, passwords, tokens, PII. Use regex: /\\b[A-Za-z0-9]{32,}\\b/, /password.*/, /token.*/. Log: '[REDACTED]'"
- ⚠️ **50%**: "Don't log sensitive data" (không cụ thể)
- ❌ **0%**: No redaction mentioned

---

### G. Performance & UX (10/120) **[NEW]**

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| G1 | Timeout handling | 3 | MCP call timeouts specified, graceful degradation | Có timeout nhưng chưa optimal | Thiếu timeout handling | `{0..3}` |
| G2 | Optimization | 3 | Batch vs single-call decisions, parallelization | Có một số optimization | Thiếu optimization | `{0..3}` |
| G3 | Progress feedback | 2 | User visibility into long operations | Có một số feedback | Thiếu progress indication | `{0..2}` |
| G4 | Caching strategy | 2 | Repeated MCP calls cached, memoization | Có một số caching | Thiếu caching | `{0..2}` |

---

### H. Maintainability (5/120) **[NEW]**

| ID | Criteria | Max | 100% (Full) | 50% (Partial) | 0% (None) | Score |
|----|----------|-----|-------------|---------------|-----------|-------|
| H1 | Versioning | 2 | Changelog cho breaking changes | Có một số versioning info | Thiếu versioning | `{0..2}` |
| H2 | Technical debt flags | 1 | Known limitations, TODO markers | Có một số flags | Thiếu debt indicators | `{0..1}` |
| H3 | Observability | 2 | Metrics definition, what to track | Có một些 telemetry info | Thiếu observability | `{0..2}` |

---

### Total Score Calculation

```
total_score = A + B + C + D + E + F + G + H
max_score = 120
percentage = (total_score / 120) * 100
```

---

## 4) Critical Fail Rules (Enhanced)

### 4.1 CRITICAL Issues (Auto-Fail)

Danh dau `CRITICAL` neu gap mot trong cac loi sau:
1. ✅ **Missing explicit Task → MCP function mapping**
2. ✅ **Uses invalid/outdated MCP function or parameters for current runtime**
3. ✅ **Missing fallback for MCP unavailable/degraded cases**
4. ⚠️ **NEW: Security vulnerability** - Exposes secrets, PII, or bypasses access controls
5. ⚠️ **NEW: Data corruption risk** - Destructive operations without safeguards

**Impact:** Bất kỳ `CRITICAL` nào → status = `fail` (bất kể tổng điểm)

### 4.2 MAJOR Issues (Must Fix Before Pass)

Danh dau `MAJOR` neu gap cac loi sau:
6. ✅ **SKILL.md and references/* contradict core workflow logic**
7. ⚠️ **NEW: Edge case uncovered** - No handling for empty results, timeouts, or errors
8. ⚠️ **NEW: Performance regression** - O(n²) or worse complexity in common path

**Impact:** Cần fix trước khi pass, nhưng có thể conditional với action items

---

## 5) Pass/Fail Thresholds (Updated for 120 points)

```
pass:        total_score >= 102  (≥85%) and no CRITICAL
conditional: 84 <= total_score <= 101  (70-84%), no CRITICAL, required action items
fail:        total_score < 84   (<70%) or any CRITICAL
```

**Note:** Conditional status requires explicit action items với effort estimates.

---

## 6) Enhanced Output Schema

```json
{
  "skill_name": "repo-recon",
  "review_metadata": {
    "reviewer": "name",
    "date": "YYYY-MM-DD",
    "review_duration_minutes": 8,
    "mcp_runtime_version": "v2.3.1",
    "reviewer_confidence": "high|medium|low"
  },
  "scoring": {
    "total_score": 87,
    "max_score": 120,
    "percentage": 72.5,
    "status": "conditional",
    "section_scores": {
      "clarity_completeness": {"score": 18, "max": 20, "percent": 90},
      "mcp_integration": {"score": 24, "max": 30, "percent": 80},
      "reliability_resilience": {"score": 16, "max": 20, "percent": 80},
      "consistency_alignment": {"score": 12, "max": 15, "percent": 80},
      "operability": {"score": 7, "max": 10, "percent": 70},
      "security_privacy": {"score": 5, "max": 10, "percent": 50},
      "performance_ux": {"score": 8, "max": 10, "percent": 80},
      "maintainability": {"score": 5, "max": 5, "percent": 100}
    }
  },
  "issues": {
    "critical": [
      "SEC-001: No input validation for user-provided file paths"
    ],
    "major": [
      "PERF-001: No timeout handling for MCP calls",
      "EDGE-001: Missing handling for empty graph_mcp results"
    ],
    "minor": [
      "DOC-001: Section A4 missing terminology definition",
      "MAINT-001: No versioning information"
    ]
  },
  "evidence": {
    "mcp_functions_valid": ["mind_mcp.get_context", "graph_mcp.traverse"],
    "mcp_functions_invalid": [],
    "mcp_params_outdated": [],
    "files_reviewed": ["SKILL.md", "references/repo-recon.md"],
    "consistency_checks_passed": 2,
    "consistency_checks_failed": 1
  },
  "action_items": {
    "must_fix_before_pass": [
      {
        "id": "SEC-001",
        "title": "Add input validation for file paths",
        "description": "Implement path validation: block '../', limit length, sanitize special chars",
        "impact": "critical",
        "estimated_effort": "30m",
        "priority": 1
      }
    ],
    "should_fix_soon": [
      {
        "id": "PERF-001",
        "title": "Add timeout handling",
        "description": "Specify 30s timeout for MCP calls with graceful degradation",
        "impact": "major",
        "estimated_effort": "1h",
        "priority": 2
      },
      {
        "id": "EDGE-001",
        "title": "Handle empty graph_mcp results",
        "description": "Add check for empty results and fallback to filesystem tools",
        "impact": "major",
        "estimated_effort": "45m",
        "priority": 3
      }
    ]
  },
  "recommendations": {
    "approval": "conditional",
    "next_review_date": "2025-05-01",
    "notes": "Strong MCP integration but needs security hardening. Address critical items before production use."
  }
}
```

---

## 7) Enhanced Test Suite (Expanded from 4 to 8 cases)

### 7.1 Core Test Cases

| # | Scenario | Expected Score | Expected Status | Key Issues |
|---|----------|----------------|-----------------|------------|
| 1 | **Perfect skill** | 115-120/120 | `pass` | None |
| 2 | **Outdated MCP params** | 0-40/120 | `fail` | CRITICAL: Invalid params |
| 3 | **Inconsistent docs** | 0-50/120 | `fail` | CRITICAL/Major: Contradictions |
| 4 | **Vague mapping** | 70-85/120 | `conditional` | Major: Missing function map |
| 5 | **Security gap** | 0-60/120 | `fail` | CRITICAL: Exposes secrets |
| 6 | **Missing edge cases** | 80-95/120 | `conditional` | MAJOR: Uncovered edge case |
| 7 | **Performance issue** | 85-100/120 | `conditional` | MAJOR: O(n²) complexity |
| 8 | **Good but outdated** | 100-110/120 | `pass` (if updated) | Minor: Versioning outdated |

### 7.2 Test Case Details

**Test Case 1: Perfect skill**
```
✅ A: 20/20 - Clear WHEN/WHEN NOT, ≤7 steps, I/O clear, terminology defined
✅ B: 28/30 - Excellent MCP mapping, 1 minor gap in guardrails
✅ C: 18/20 - Strong fallback, 1 minor gap in conflict resolution
✅ D: 14/15 - Perfect alignment, 1 minor terminology inconsistency
✅ E: 9/10 - Efficient review, 1 minor action item gap
✅ F: 10/10 - Comprehensive security measures
✅ G: 9/10 - Excellent performance, 1 minor caching gap
✅ H: 5/5 - Perfect maintainability
→ Total: 113/120 (94.2%) → PASS
```

**Test Case 5: Security gap**
```
✅ A: 18/20 - Good clarity
✅ B: 25/30 - Good MCP integration
✅ C: 16/20 - Decent fallback
❌ F: 2/10 - CRITICAL: No input validation, exposes PII in logs, no access boundaries
→ Status: FAIL (CRITICAL security vulnerability)
→ Action: Must add input validation + redaction before any use
```

---

## 8) Anti-Patterns Catalog

### 8.1 MCP Integration Anti-Patterns

```
❌ BAD:    "Call graph_mcp for everything"
✅ GOOD:   "Phase 1: graph_mcp.get_module_inventory() [required]
            Phase 2: graph_mcp.get_call_graph(module) [optional, if complex]"

❌ BAD:    "If MCP fails, give up"
✅ GOOD:   "Fallback: (1) Filesystem tools + (2) Manual doc review
            (3) Log degraded mode + (4) Notify user of limitations"

❌ BAD:    "Use mind_mcp to get context"
✅ GOOD:   "Phase 1: mind_mcp.get_project_context() [required]
            Params: { include_readme: true, include_docs: true }
            Expected: { overview: string, tech_stack: string[] }"
```

### 8.2 Security Anti-Patterns

```
❌ BAD:    "User input passed directly to MCP query"
✅ GOOD:   "Validate + sanitize user input:
            - Block '../' in file paths
            - Limit query length to 1000 chars
            - Whitelist allowed modules
            - Sanitize special characters: ;, |, &, $"

❌ BAD:    "Log the query results"
✅ GOOD:   "Log query results with redaction:
            - Redact API keys: /\\b[A-Za-z0-9]{32,}\\b/g → '[REDACTED]'
            - Redact passwords: /password.*/gi → '[REDACTED]'
            - Redact tokens: /token.*/gi → '[REDACTED]'
            - Redact PII: email, phone, SSN patterns"
```

### 8.3 Performance Anti-Patterns

```
❌ BAD:    "For each module, call graph_mcp.get_info()"  (O(n) MCP calls)
✅ GOOD:   "Batch call: graph_mcp.get_modules_info([modules])  (1 MCP call)"

❌ BAD:    "No timeout specified"
✅ GOOD:   "Timeout: 30s per MCP call, 5min total workflow
            On timeout: Return partial results + notify user"

❌ BAD:    "Call graph_mcp.get_context() multiple times with same params"
✅ GOOD:   "Cache graph_mcp.get_context() results, invalidate on workflow start"
```

---

## 9) Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│  SKILL REVIEW CHEAT SHEET                              │
├────────────────────────────────────────────────────────┤
│  5-min Quick Scan (Start here)                         │
│  ────────────────────────────────                      │
│  ☐ Check "Use when..." has WHEN + WHEN NOT             │
│  ☐ Verify MCP functions exist (list_mcp_functions)     │
│  ☐ Confirm fallback exists for MCP failures            │
│  ☐ Look for "secret", "password", "token", "PII"       │
│  ☐ Check SKILL.md vs references/* consistency          │
│  ☐ Verify input validation exists                      │
│  ☐ Check for timeout handling                          │
├────────────────────────────────────────────────────────┤
│  Auto-Fail (Don't waste time if you see these)         │
│  ──────────────────────────────────────────────────    │
│  ❌ No MCP function mapping                            │
│  ❌ Outdated MCP params                                │
│  ❌ Exposes secrets/PII                                │
│  ❌ Destructive ops without safeguards                 │
│  ❌ No input validation                                │
├────────────────────────────────────────────────────────┤
│  Scoring Quick Reference                               │
│  ────────────────────────                              │
│  A: Clarity        20pts  (100%: WHEN/WHEN NOT, ≤7 steps) │
│  B: MCP Integration 30pts  (100%: Phase map, valid APIs) │
│  C: Reliability    20pts  (100%: Fallback, confidence)    │
│  D: Consistency    15pts  (100%: No contradictions)       │
│  E: Operability    10pts  (100%: 5-10min review)         │
│  F: Security       10pts  (100%: Validate + redact)      │
│  G: Performance    10pts  (100%: Timeouts + caching)     │
│  H: Maintainability 5pts  (100%: Versioning + flags)     │
│  ─────────────────────                                  │
│  TOTAL: 120pts                                          │
│  Pass: ≥102pts (85%) + no CRITICAL                      │
├────────────────────────────────────────────────────────┤
│  Critical Issue Examples                                │
│  ──────────────────────                                 │
│  CRITICAL: "No Task → MCP mapping"                      │
│  CRITICAL: "Uses deprecated function graph_mcp.v1()"    │
│  CRITICAL: "No fallback for MCP failures"               │
│  CRITICAL: "User input passed directly to query"        │
│  CRITICAL: "Logs API keys in plain text"                │
│  MAJOR: "No handling for empty results"                 │
│  MAJOR: "O(n²) complexity in common path"               │
└────────────────────────────────────────────────────────┘
```

---

## 10) Review Checklist (Interactive Format)

### A. Clarity & Completeness (20/120)

**A1. "Use when..." rõ rang (5đ)**
- [ ] 100%: WHEN + WHEN NOT rõ, 1-2 câu, specific triggers
- [ ] 50%: Có WHEN nhưng thiếu WHEN NOT, hoặc 3-4 câu
- [ ] 0%: Qua mơ, dài >4 câu, hoặc missing

**Evidence**: [Paste "Use when..." section here]
**Score**: [0-5]
**Notes**: ___________________

**A2. Workflow chinh (5đ)**
- [ ] 100%: ≤ 7 buoc, hanh dong cu the
- [ ] 50%: 8-10 buoc hoặc tên hơi chung chung
- [ ] 0%: >10 buoc hoặc tên vague

**Score**: [0-5]
**Notes**: ___________________

*(Continue for A3, A4...)*

---

## 11) Ket qua Review (Fill in)

| Truong | Gia tri |
| --- | --- |
| total_score | `{0..120}` |
| percentage | `{0..100}%` |
| critical_count | `{N}` |
| major_count | `{N}` |
| minor_count | `{N}` |
| status | `pass|conditional|fail` |
| summary | `{1-3 dong}` |

### Critical Issues (if any)
1. `{issue description}`
2. `{...}`

### Major Issues (if any)
1. `{issue description}`
2. `{...}`

### Top Fixes (max 5, priority order)
1. **[CRITICAL/MAJOR]** `{fix description}` - `{effort estimate}`
2. **[MAJOR]** `{...}` - `{...}`
3. **[MINOR]** `{...}` - `{...}`
4. **[MINOR]** `{...}` - `{...}`
5. **[MINOR]** `{...}` - `{...}`

### Recommendations
- **Approval**: `{pass/conditional/fail}`
- **Next review date**: `{YYYY-MM-DD}`
- **Notes**: `{additional context}`

---

## 12) Reviewer Notes

```
- Review completed in: {X} minutes
- MCP runtime version: {version}
- Files reviewed: {list}
- Confidence level: {high/medium/low}
- Additional context: {any observations}
```
