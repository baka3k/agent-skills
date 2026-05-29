---
description: Orchestrate end-to-end deep codebase discovery with automatic Mermaid architecture diagrams, module dependency graphs, and structured synthesis — combining mind_mcp knowledge retrieval, graph_mcp semantic exploration, and chained repo-recon → tech-build-audit → module-summary-report skills for rapid onboarding.
variables:
  input:
    - name: $REPO_ROOT
      source: CLI --repo-root
      required: true
    - name: $PROJECT_ID
      source: CLI --project
      required: true
    - name: $SCOPE
      source: CLI --scope (default: full; options: full, backend, frontend, infra, focused)
      required: false
    - name: $AUDIENCE
      source: CLI --audience (default: mixed; options: engineering, management, mixed)
      required: false
    - name: $GEN_DIAGRAM
      source: CLI --mermaid (default: true; options: true, false)
      required: false
      description: Tự động sinh Mermaid diagrams (architecture overview + module dependency graph)
  preflight:
    - name: discovery-bundle
      source: output file (write)
      required: true
    - name: discovery-report
      source: output file (write)
      required: true
    - name: architecture-diagram
      source: output file (write) — Mermaid .mmd
      required: false
    - name: module-dependency-diagram
      source: output file (write) — Mermaid .mmd
      required: false
handoffs:
  - label: Run Repo Recon (Phase 1)
    agent: hi.repo-recon
    prompt: |
      Chạy repo-recon để tạo module inventory và entry-point map.
      Repo: $REPO_ROOT. Scope: $SCOPE. Depth: deep.
      Output: recon-data/
  - label: Run Tech Build Audit (Phase 2)
    agent: hi.tech-build-audit
    prompt: |
      Chạy tech-build-audit để phân tích stack, build, CI/CD.
      Repo: $REPO_ROOT. Depth: deep.
      Output: audit-data/
  - label: Generate Module Summary (Phase 3)
    agent: hi.module-summary-report
    prompt: |
      Tổng hợp toàn bộ findings thành architecture summary.
      Inventory: recon-data/module-inventory.json. Audit: audit-data/tech-stack.json.
      Repo: $REPO_ROOT. Audience: $AUDIENCE.
      Output: summary-data/
  - label: Generate Architecture Diagrams (Phase 4)
    agent: hi.module-summary-report
    prompt: |
      Từ module inventory và dependency data, sinh Mermaid architecture diagrams:
      1. System Architecture Overview (mermaid graph TD) — toàn bộ hệ thống ở mức high-level
      2. Module Dependency Graph (mermaid graph LR) — quan hệ phụ thuộc giữa các module
      Inventory: recon-data/module-inventory.json. Tech: audit-data/tech-stack.json.
      Repo: $REPO_ROOT.
      Output: discovery-data/diagrams/
hooks:
  pre:
    - name: mcp-health-check
      description: Verify MCP Graph + Mind connectivity
      timeout: 15s
      required: true
    - name: skill-chain-verification
      description: Verify repo-recon, tech-build-audit, module-summary-report skills are available
      skills: [repo-recon, tech-build-audit, module-summary-report]
    - name: input-validation
      description: Validate repo path, project ID, scope, and audience parameters
      scope: ["repo_root", "project_id", "scope", "audience"]
      enable_redaction: true
  post:
    - name: validate-outputs
      description: Verify all required output files were generated
      required_files:
        - discovery-data/discovery-report.md
        - discovery-data/module-inventory.json
        - discovery-data/tech-audit.md
        - discovery-data/risks.md
        - discovery-data/module-summary.md
      optional_files:
        - discovery-data/diagrams/architecture-overview.mmd
        - discovery-data/diagrams/module-dependency-graph.mmd
        - discovery-data/diagrams/architecture-overview.png
        - discovery-data/diagrams/module-dependency-graph.png
---

# Deep Codebase Discovery Agent

> **Version:** 2.0  
> **Date:** 2026-05-19  
> **Purpose:** Đánh giá kỹ thuật end-to-end codebase — cấu trúc, stack, critical flows, rủi ro — trong một lần chạy duy nhất.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## 🎯 What This Agent Does

Đây là **orchestrator agent** — phối hợp 3 skill + diagram generation để tạo bức tranh toàn diện về codebase **có thể xem được ngay**:

```
deep-codebase-discovery
├── repo-recon             → Module inventory + entry-point map
├── tech-build-audit       → Stack, build system, CI/CD, platform
├── module-summary-report  → Báo cáo kiến trúc tóm tắt + rủi ro
└── DIAGRAM GENERATION     → Mermaid architecture + dependency diagrams ✨
```

### Pipeline thực hiện

1. **Preflight** — Kiểm tra MCP health, validate skills availability
2. **Phase 1 - MCP Knowledge** — mind_mcp: lấy context dự án, domain entities
3. **Phase 2 - Semantic Exploration** — graph_mcp: module mapping, call graph, critical flows
4. **Phase 3 - Synthesis** — Kết hợp repo-recon + tech-build-audit outputs
5. **Phase 4 - Reconciliation** — Đối chiếu chéo, phát hiện inconsistencies
6. **Phase 5 - Bundle** — Đóng gói tất cả output + sinh báo cáo rủi ro
7. **Phase 6 - Diagram Generation**  — Tự động sinh Mermaid diagrams từ module inventory

---

## When To Use

- Onboarding lần đầu vào codebase lớn hoặc xa lạ
- Cần đánh giá kỹ thuật end-to-end: structure + stack + flows + risks
- Chuẩn bị architecture review, handover documentation, migration assessment
- Cần một output duy nhất có tất cả thông tin

## Avoid Using When

- Chỉ cần một câu trả lời hẹp (module map đơn thuần → dùng repo-recon)
- Chỉ debug một bug path cụ thể (dùng bug-impact-analyzer)
- Repo quá nhỏ, scan tay là đủ
- Không có quyền truy cập MCP Graph/Mind

---

## Input Parameters

| Parameter     | Required | Default   | Description                                                |
|---------------|----------|-----------|------------------------------------------------------------|
| `--repo-root`  | Yes      | —         | Đường dẫn tuyệt đối tới repository                         |
| `--project`    | Yes      | —         | Project identifier cho MCP contexts (database/collection)  |
| `--scope`      | No       | `full`    | Phạm vi: full, backend, frontend, infra, focused           |
| `--audience`   | No       | `mixed`   | Đối tượng: engineering, management, mixed                  |
| `--mermaid`   | No       | `true`    | Tự động sinh Mermaid diagrams (architecture + dependency)   |

---

## Output Location

Tất cả output được tạo trong `discovery-data/`.

```
<workspace>/
└── discovery-data/
    ├── discovery-report.md              # Báo cáo tổng thể (có embed Mermaid)
    ├── module-inventory.json            # Module map + dependencies
    ├── module-summary.md                # Tóm tắt từng module (responsibility, deps, risk)
    ├── entry-point-map.json             # Entry points
    ├── tech-audit.md                    # Stack, build, CI/CD, platform
    ├── critical-flows.md                # Critical call flows
    ├── risks.md                         # Prioritized risks & mitigations
    └── diagrams/                        # ✨ Mermaid diagrams (auto-generated)
        ├── architecture-overview.mmd    # System-level architecture (graph TD)
        ├── module-dependency-graph.mmd  # Module dependency relations (graph LR)
        ├── architecture-overview.png    # Rendered PNG (nếu có renderMermaidDiagram)
        └── module-dependency-graph.png  # Rendered PNG
```

---

## Scope Levels

| Level     | Mô tả                                                              |
|-----------|--------------------------------------------------------------------|
| `full`     | Toàn bộ codebase: backend + frontend + infra                      |
| `backend`  | Chỉ backend services, API, database                                |
| `frontend` | Chỉ frontend apps, UI components                                   |
| `infra`    | Chỉ infrastructure configs (Docker, CI/CD, K8s, cloud)            |
| `focused`  | Module/domain cụ thể do user chỉ định                             |

---

## Audience Levels

| Level         | Output phù hợp cho                                          |
|---------------|-------------------------------------------------------------|
| `engineering` | Technical deep-dive: function signatures, call chains, APIs |
| `management`  | High-level summary: module responsibilities, risks, timeline|
| `mixed`       | Cả hai: technical details + executive summary               |

---

## 🅿️ Phase 6: Diagram Generation ✨ (auto if `--mermaid true`)

**Goal:** Tự động sinh Mermaid diagrams từ `module-inventory.json` và `critical-flows.md` để có thể xem trực quan ngay.

### Diagram 1: System Architecture Overview (`architecture-overview.mmd`)

```mermaid
graph TD
    subgraph "Frontend"
        FE[React/Vue/Angular App]
    end
    subgraph "Backend Services"
        API[API Gateway] --> AUTH[Auth Service]
        API --> BIZ[Business Logic]
        BIZ --> DB[(Database)]
    end
    subgraph "Infrastructure"
        CICD[CI/CD Pipeline]
        MON[Monitoring]
    end
    FE --> API
    CICD --> FE
    CICD --> API
```

**Quy tắc sinh:**
- Dùng `graph TD` (top-down) cho system-level view
- Gom module theo layer: Frontend / Backend / Infrastructure / Data
- Mỗi module = 1 node với tên hiển thị ngắn gọn
- Edge = dependency direction (A → B nghĩa là A depends on B)
- Style: dùng `subgraph` để nhóm các module cùng layer

### Diagram 2: Module Dependency Graph (`module-dependency-graph.mmd`)

```mermaid
graph LR
    subgraph "Core Modules"
        CM1[config-service] --> CM2[logging]
        CM2 --> CM3[error-handler]
    end
    subgraph "Domain Modules"
        DM1[user-service] --> CM1
        DM2[order-service] --> DM1
        DM2 --> CM3
    end
    subgraph "API Layer"
        API[routes] --> DM1
        API --> DM2
    end
```

**Quy tắc sinh:**
- Dùng `graph LR` (left-right) để dễ đọc dependency chain
- Nhóm theo domain/feature thay vì layer
- Edge label (nếu có) = kiểu dependency: `import`, `call`, `event`, `db`
- Màu sắc (nếu render): core = xanh, domain = tím, api = cam

### Diagram 3: Critical Flow (embedded in `discovery-report.md`)

Nếu phát hiện critical flow trong Phase 2, embed sequence diagram:

```mermaid
sequenceDiagram
    Client->>API: Request
    API->>Auth: Validate token
    Auth-->>API: OK
    API->>Service: Process
    Service->>DB: Query
    DB-->>Service: Result
    Service-->>API: Response
    API-->>Client: 200 OK
```

### Cách dùng

| Công cụ | Cách render |
|---------|-------------|
| VS Code | Mở file `.mmd`, dùng extension `Markdown Preview Mermaid Support` |
| CLI | `renderMermaidDiagram` tool có sẵn |
| Export PNG | Auto nếu tool `renderMermaidDiagram` available |
| GitHub | Copy paste vào markdown, GitHub render Mermaid native |

---

## Sensitive Data Handling

Mọi output đều được redact tự động:

- API keys, bearer tokens, credentials → `[REDACTED_*]`
- Database URLs, IP addresses → `[REDACTED_*]`
- Email, phone, SSN → `[REDACTED_*]`

---

## Quick Start — Dùng Ngay

```bash
# Chạy full discovery + diagrams cho repo hiện tại
agent hi.deep-codebase-discovery \
  --repo-root /path/to/your/repo \
  --project my-project \
  --scope full \
  --audience mixed \
  --mermaid true
```

**Kết quả:** Mở `discovery-data/discovery-report.md` hoặc `discovery-data/diagrams/architecture-overview.mmd` để xem ngay.
