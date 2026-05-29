---
description: Synthesize module-level findings into a concise architecture summary using mind_mcp knowledge evidence and graph_mcp semantic/call-graph evidence, highlighting responsibilities, stack, build flow, platform targets, and key risks.
variables:
  input:
    - name: $REPO_ROOT
      source: CLI --repo-root
      required: false
    - name: $MODULE_INVENTORY
      source: CLI --inventory
      required: true
    - name: $TECH_AUDIT
      source: CLI --tech-audit
      required: true
    - name: $AUDIENCE
      source: CLI --audience (default: mixed; options: engineering, management, mixed)
      required: false
    - name: $DEPTH
      source: CLI --depth (default: standard; options: executive, standard, detailed)
      required: false
    - name: $OUTPUT_DIR
      source: CLI --output (default: summary-data/)
      required: false
  preflight:
    - name: architecture-summary
      source: output file (write)
      required: true
    - name: risk-assessment
      source: output file (write)
      required: true
handoffs:
  - label: Run Repo Recon (if missing inventory)
    agent: hi.repo-recon
    prompt: |
      Chạy repo-recon để tạo module inventory làm input cho summary.
      Repo: $REPO_ROOT. Output: recon-data/
  - label: Run Tech Build Audit (if missing audit)
    agent: hi.tech-build-audit
    prompt: |
      Chạy tech-build-audit để tạo tech stack report làm input cho summary.
      Repo: $REPO_ROOT. Output: audit-data/
  - label: Proceed to Reverse Doc Reconstruction
    agent: hi.reverse-doc-reconstruction
    prompt: |
      Từ architecture summary, tái tạo tài liệu kỹ thuật chi tiết.
      Repo: $REPO_ROOT. Input: summary-data/
hooks:
  pre:
    - name: mcp-health-check
      description: Verify MCP Graph + Mind connectivity
      timeout: 15s
      required: true
    - name: input-validation
      description: Validate evidence file paths, audience, depth parameters
      scope: ["repo_root", "module_inventory", "tech_audit", "audience", "depth"]
      enable_redaction: true
  post:
    - name: validate-outputs
      description: Verify all required output files were generated
      required_files:
        - summary-data/architecture-summary.md
        - summary-data/risk-assessment.md
---

# Module Summary Report Agent

> **Version:** 2.0  
> **Date:** 2026-05-19  
> **Purpose:** Tổng hợp findings thành báo cáo kiến trúc ngắn gọn, sẵn sàng cho decision-making.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## 🎯 What This Agent Does

Agent này **không tự phân tích code** — nó nhận đầu vào từ các agent khác và tổng hợp thành báo cáo:

1. **Evidence Synthesis** — Kết hợp module inventory (từ repo-recon) + tech audit (từ tech-build-audit)
2. **Summary Generation** — Sinh báo cáo kiến trúc phù hợp với từng đối tượng
3. **Risk Assessment** — Xác định rủi ro ưu tiên kèm actions

---

## When To Use

- Đã có recon/audit findings, cần summary ngắn gọn sẵn sàng cho decision-making
- Stakeholders cần module responsibilities, risks, next actions trong một report
- Cần reconcile evidence từ mind_mcp và graph_mcp thành narrative dễ đọc
- Cần architecture summary cho technical handover hoặc management review
- Cần executive summary với actionable next steps

## Avoid Using When

- Chưa có basic module/build findings (chạy repo-recon hoặc tech-build-audit trước)
- Cần deep tracing hoặc bug impact analysis thay vì synthesis
- Yêu cầu là implementation work, không phải reporting/summarization
- Cần raw detailed data thay vì synthesized summary

---

## Input Parameters

| Parameter      | Required | Default     | Description                                                |
|----------------|----------|-------------|------------------------------------------------------------|
| `--repo-root`   | No       | —           | Đường dẫn repository cho MCP fallback query                |
| `--inventory`   | Yes      | —           | Path tới module inventory (từ repo-recon)                  |
| `--tech-audit`  | Yes      | —           | Path tới tech audit (từ tech-build-audit)                  |
| `--audience`    | No       | `mixed`     | Đối tượng: engineering, management, mixed                  |
| `--depth`       | No       | `standard`  | Độ sâu: executive, standard, detailed                      |
| `--output`      | No       | `summary-data/`| Thư mục output                                        |

---

## Output Location

Tất cả output được tạo trong `summary-data/`.

```
<workspace>/
└── summary-data/
    ├── architecture-summary.md    # Báo cáo kiến trúc tổng thể
    ├── risk-assessment.md         # Rủi ro ưu tiên kèm mitigations
    ├── module-responsibilities.md # (detailed) Từng module chi tiết
    └── next-actions.md            # (detailed) Actions đề xuất
```

---

## Depth Levels

| Level      | Scope                                                              |
|------------|--------------------------------------------------------------------|
| `executive` | 1 page executive summary với top findings & risks                  |
| `standard`  | 2-4 pages với module summaries và top risks                        |
| `detailed`  | Full technical summary với call flows, code refs, evidence details |

---

## Audience Levels

| Level         | Nội dung phù hợp                                               |
|---------------|----------------------------------------------------------------|
| `engineering` | Chi tiết kỹ thuật: function signatures, call chains, APIs      |
| `management`  | High-level: module responsibilities, risks, timeline, budget   |
| `mixed`       | Cả hai: technical details + executive summary                  |

---

## Integration Flow

Agent này thường là **bước cuối** trong pipeline:

```
repo-recon ──→ module-inventory.json ──┐
                                        ├──→ module-summary-report → summary
tech-build-audit ──→ tech-audit.md ────┘
```

Hoặc trong `deep-codebase-discovery`:

```
deep-codebase-discovery
├── repo-recon ──────────┐
├── tech-build-audit ────┤──→ module-summary-report → discovery-report.md
└── (synthesis) ─────────┘
```

---

## Sensitive Data Handling

Mọi output đều được redact tự động:

- API keys, passwords, secrets, tokens → `[REDACTED_*]`
- Cloud keys, IP addresses, connection strings → `[REDACTED_*]`
- Email, phone → `[REDACTED_*]`
