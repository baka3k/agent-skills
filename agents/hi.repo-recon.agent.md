---
description: Build structural understanding of an unfamiliar repository by combining mind_mcp knowledge retrieval with graph_mcp semantic code exploration, producing module inventory and entry-point map.
variables:
  input:
    - name: $REPO_ROOT
      source: CLI --repo-root
      required: true
    - name: $FOCUS_SCOPE
      source: CLI --scope (default: all; options: backend, frontend, infra, data, all)
      required: false
    - name: $DEPTH
      source: CLI --depth (default: standard; options: quick, standard, deep)
      required: false
  preflight:
    - name: module-inventory
      source: output file (write)
      required: true
    - name: entry-point-map
      source: output file (write)
      required: true
handoffs:
  - label: Run Tech Build Audit
    agent: hi.tech-build-audit
    prompt: |
      Phân tích stack, build system, CI/CD từ repo đã được recon.
      Repo: $REPO_ROOT.
  - label: Generate Module Summary Report
    agent: hi.module-summary-report
    prompt: |
      Tổng hợp module inventory thành báo cáo kiến trúc ngắn gọn.
      Inventory: recon-data/module-inventory.json. Audit: audit-data/tech-stack.json.
      Repo: $REPO_ROOT.
  - label: Proceed to Deep Discovery
    agent: hi.deep-codebase-discovery
    prompt: |
      Kết hợp repo-recon output vào deep codebase discovery pipeline.
      Repo: $REPO_ROOT. Scope: $FOCUS_SCOPE.
hooks:
  pre:
    - name: mcp-health-check
      description: Verify MCP Graph + Mind connectivity
      timeout: 15s
      required: true
    - name: input-validation
      description: Validate repo path, focus scope, and depth parameters
      scope: ["repo_root", "focus_scope", "depth"]
      enable_redaction: true
  post:
    - name: validate-outputs
      description: Verify all required output files were generated
      required_files:
        - recon-data/module-inventory.json
        - recon-data/entry-point-map.json
---

# Repo Recon Agent

> **Version:** 2.0  
> **Date:** 2026-05-19  
> **Purpose:** Khám phá và xây dựng hiểu biết cấu trúc về một repository lạ.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## 🎯 What This Agent Does

Agent này giúp bạn hiểu nhanh một codebase xa lạ bằng cách:

1. **Knowledge Retrieval (mind_mcp)**: Lấy context dự án từ MCP knowledge base.
2. **Semantic Exploration (graph_mcp)**: Khám phá module, file, function qua call-graph.
3. **Filesystem Scan**: Cross-check cấu trúc thư mục thực tế.
4. **Inventory Generation**: Tạo module inventory và entry-point map.

---

## When To Use

- Bạn cần hiểu nhanh cấu trúc một repository mới
- Bạn cần xác định module boundaries và entry points trước khi phân tích sâu
- Bạn chuẩn bị cho refactor/audit/documentation
- Bạn đang onboard vào codebase mới không có tài liệu
- Bạn cần tạo handover documentation hoặc architecture review

## Avoid Using When

- Đã có module inventory hiện tại, chỉ cần synthesis (dùng module-summary-report)
- Chỉ debug một bug path cụ thể (dùng bug-impact-analyzer)
- Chỉ cần phân tích stack/build (dùng tech-build-audit)
- Cần đánh giá kỹ thuật end-to-end (dùng deep-codebase-discovery)

---

## Input Parameters

| Parameter    | Required | Default   | Description                                       |
|-------------|----------|-----------|---------------------------------------------------|
| `--repo-root` | Yes      | —         | Đường dẫn tuyệt đối tới repository               |
| `--scope`     | No       | `all`     | Phạm vi focus: backend, frontend, infra, data, all |
| `--depth`     | No       | `standard`| Độ sâu: quick, standard, deep                      |

---

## Output Location

Tất cả output được tạo trong thư mục `recon-data/`.

```
<workspace>/
└── recon-data/
    ├── module-inventory.json       # Danh sách module, file chính, dependencies
    ├── entry-point-map.json        # Entry points (CLI, API, UI routes, services)
    └── key-functions.json          # (standard/deep) Function signatures quan trọng
```

---

## Depth Levels

| Level    | Scope                                                              |
|----------|--------------------------------------------------------------------|
| `quick`   | Module boundaries và entry points cơ bản                           |
| `standard`| Module boundaries, entry points, key functions per module          |
| `deep`    | Tất cả standard + call graph expansion và integration boundaries   |

---

## Integration Boundaries (deep mode)

Khi chạy ở chế độ `deep`, agent sẽ phân tích thêm:

- **IPC**: REST/gRPC calls, message queues, event streams
- **Database**: Tables, collections, queries chính
- **External services**: API clients, third-party integrations
- **File I/O**: File formats, paths, storage patterns

---

## Sensitive Data Handling

Mọi output đều được redact tự động theo các patterns:

- API keys, password, secret, token → `[REDACTED_*]`
- IP addresses, hostnames, URLs → `[REDACTED_*]`
- Connection strings, cloud keys → `[REDACTED_*]`
- Email, phone numbers → `[REDACTED_*]`
