# Agents Directory — Ollama Agents

Tổng hợp các agent hiện có trong `agents/`, chia làm 2 nhóm:

---

## Nhóm 1: Codebase Discovery & Documentation

Các agent phân tích codebase, phát hiện cấu trúc, use case, và tài liệu.

### `hi.repo-recon`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Khám phá cấu trúc repository lạ — module inventory + entry-point map |
| **Khi dùng** | Onboarding codebase mới, architecture review, refactor planning, handover docs |
| **Input** | `--repo-root`, `--scope`, `--depth` |
| **Output** | `recon-data/module-inventory.json`, `entry-point-map.json` |
| **Orchestrate** | `hi.tech-build-audit`, `hi.module-summary-report`, `hi.deep-codebase-discovery` |
| **Solo** | ✅ Có — chạy độc lập để lấy module map |

---

### `hi.tech-build-audit`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Phân tích tech stack, build system, CI/CD, deployment targets |
| **Khi dùng** | Cần hiểu stack/build của repo, chuẩn bị migration, audit CI/CD |
| **Input** | `--repo-root`, `--env`, `--depth` |
| **Output** | `audit-data/build-report.md`, `tech-stack.json`, `ci-cd-pipelines.md` |
| **Orchestrate** | `hi.module-summary-report`, `hi.deep-codebase-discovery` |
| **Solo** | ✅ Có — chạy độc lập để audit stack |

---

### `hi.module-summary-report`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Tổng hợp findings từ các agent khác → báo cáo kiến trúc + rủi ro |
| **Khi dùng** | Đã có inventory + audit, cần summary decision-ready |
| **Input** | `--inventory`, `--tech-audit`, `--audience`, `--depth` |
| **Output** | `summary-data/architecture-summary.md`, `risk-assessment.md` |
| **Orchestrate** | `hi.repo-recon`, `hi.tech-build-audit` (chain ngược nếu thiếu data) |
| **Solo** | ⚠️ Có — nhưng cần `--inventory` và `--tech-audit` từ agent khác |

---

### `hi.deep-codebase-discovery`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | **Orchestrator** — đánh giá end-to-end: cấu trúc + stack + risks trong 1 lần |
| **Khi dùng** | Onboarding lần đầu, cần bức tranh toàn diện về codebase |
| **Input** | `--repo-root`, `--project`, `--scope`, `--audience` |
| **Output** | `discovery-data/discovery-report.md`, `module-inventory.json`, `tech-audit.md`, `risks.md` |
| **Orchestrate** | `hi.repo-recon` → `hi.tech-build-audit` → `hi.module-summary-report` |
| **Solo** | ✅ Có — tự động chain 3 agent con |

---

### `hi.usecase-discovery`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Khám phá use case từ source code — function list → call trace → UC docs |
| **Khi dùng** | Legacy system cần tài liệu use case, reverse engineering, compliance |
| **Input** | `--repo-root`, `--module`, `--db`, `--parser`, `--depth` |
| **Output** | `usecase/<module>/phase1_*.json`, `phase2_*.txt`, `phase3_diagrams/`, `uc_*.md` |
| **Orchestrate** | `hi.repo-recon` (context), `hi.reverse-doc-reconstruction` (downstream) |
| **Solo** | ✅ Có — chạy độc lập 4 phase từ search → trace → UC docs |

---

## Nhóm 2: C++ → Java Porting Pipeline

Các agent chuyên biệt cho migration C++ → Java.

### `hi.pre-porting`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Phân tích pre-porting: compatibility gap, type mappings, compat layer, migration roadmap |
| **Khi dùng** | Trước khi porting — cần đánh giá mức độ phức tạp và lên kế hoạch |
| **Input** | `--source-folder`, `--module`, `--output` |
| **Output** | `pre-porting-data/type-mappings.json`, `compat-layer-design.md`, `migration-roadmap.md` |
| **Orchestrate** | `hi.porting-plan-generator`, `hi.porting-file-structure`, `hi.porting-cpp-to-java` |
| **Solo** | ✅ Có — chạy độc lập để phân tích trước khi port |

---

### `hi.porting-plan-generator`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Sinh porting execution plan từ MCP Graph call graph — topological sort → wave-based plan |
| **Khi dùng** | Sau pre-porting, cần plan chi tiết thứ tự porting từng file/function |
| **Input** | Dữ liệu từ `pre-porting-data/` |
| **Output** | `porting-output/porting-plan/porting-plan.md`, `porting-plan.json` |
| **Orchestrate** | `hi.porting-file-structure`, `hi.porting-cpp-to-java` |
| **Solo** | ⚠️ Phụ thuộc — cần data từ `hi.pre-porting` |

---

### `hi.porting-file-structure`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Port cấu trúc file C++ → Java: extract skeleton từ Graph, 1-1 mapping class/function/params |
| **Khi dùng** | Khi đã có plan, cần tạo Java file skeleton |
| **Input** | Dữ liệu từ porting plan |
| **Output** | Java files trong `porting-output/` |
| **Orchestrate** | `hi.porting-function`, `hi.porting-cpp-to-java` |
| **Solo** | ⚠️ Phụ thuộc — cần plan từ `hi.porting-plan-generator` |

---

### `hi.porting-function`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | Port từng function C++ → Java: convert type/lambda/pointer, compat layer calls, validate syntax |
| **Khi dùng** | Khi đã có Java skeleton, cần implement function bodies |
| **Input** | Java skeleton từ `hi.porting-file-structure` |
| **Output** | Implemented Java functions |
| **Orchestrate** | `hi.porting-cpp-to-java`, `hi.porting-file-structure` |
| **Solo** | ⚠️ Phụ thuộc — cần file structure từ agent trước |

---

### `hi.porting-cpp-to-java`

| Mục | Chi tiết |
|-----|----------|
| **Mục đích** | **Orchestrator** — điều phối toàn bộ pipeline porting C++ → Java |
| **Khi dùng** | Chạy toàn bộ quy trình migration từ đầu đến cuối |
| **Input** | `--source-folder`, `--module`, các tham số porting |
| **Output** | Toàn bộ Java code + compat layer trong `porting-output/` |
| **Orchestrate** | `hi.pre-porting` → `hi.porting-plan-generator` → `hi.porting-file-structure` → `hi.porting-function` |
| **Solo** | ✅ Có — tự động chain toàn bộ pipeline |

---

## Sơ đồ Orchestration

### Nhóm Discovery

```
hi.deep-codebase-discovery (orchestrator)
├── hi.repo-recon ──────────→ recon-data/
├── hi.tech-build-audit ────→ audit-data/
└── hi.module-summary-report → summary-data/

hi.usecase-discovery (orchestrator - độc lập)
├── Phase 1: Graph MCP search
├── Phase 2: explore_graph + semantic_search
├── Phase 3: trace_flow + diagram
└── Phase 4: UC docs
```

### Nhóm Porting

```
hi.porting-cpp-to-java (orchestrator)
├── hi.pre-porting ──────────────→ pre-porting-data/
├── hi.porting-plan-generator ──→ porting-plan/
├── hi.porting-file-structure ──→ Java skeletons/
└── hi.porting-function ────────→ Implemented functions/
```

---

## Khi nào dùng agent nào?

| Bạn cần | Dùng agent |
|---------|------------|
| Hiểu nhanh structure của repo lạ | `hi.repo-recon` |
| Audit tech stack + build + CI/CD | `hi.tech-build-audit` |
| Báo cáo kiến trúc summary ngắn gọn | `hi.module-summary-report` |
| Đánh giá end-to-end (structure + stack + risks) | `hi.deep-codebase-discovery` |
| Khám phá use case từ code | `hi.usecase-discovery` |
| Phân tích pre-porting C++ trước khi migrate | `hi.pre-porting` |
| Sinh porting execution plan | `hi.porting-plan-generator` |
| Chạy toàn bộ pipeline C++ → Java | `hi.porting-cpp-to-java` |

---

## Tổng hợp

| Agent | Orchestrator? | Solo? | Cần agent khác? |
|-------|:------------:|:-----:|:---------------:|
| `hi.repo-recon` | Không | ✅ Có | Không |
| `hi.tech-build-audit` | Không | ✅ Có | Không |
| `hi.module-summary-report` | Không | ⚠️ Có, cần input từ ngoài | `hi.repo-recon` + `hi.tech-build-audit` |
| `hi.deep-codebase-discovery` | ✅ Có (3 agents) | ✅ Có | Tự chain |
| `hi.usecase-discovery` | Không (có handoff) | ✅ Có | Không |
| `hi.pre-porting` | Không | ✅ Có | Không |
| `hi.porting-plan-generator` | Không | ⚠️ Phụ thuộc | `hi.pre-porting` |
| `hi.porting-file-structure` | Không | ⚠️ Phụ thuộc | `hi.porting-plan-generator` |
| `hi.porting-function` | Không | ⚠️ Phụ thuộc | `hi.porting-file-structure` |
| `hi.porting-cpp-to-java` | ✅ Có (4 agents) | ✅ Có | Tự chain |
