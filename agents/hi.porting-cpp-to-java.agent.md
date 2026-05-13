---
description: Master agent điều phối quy trình porting từ C++ sang Java. Tích hợp MCP Graph để trace, phân tích dependencies, và sinh code Java tương ứng.
handoffs:
  - label: Phase 1 – Pre-Porting Analysis
    agent: hi.pre-porting
    prompt: |
      Chuẩn bị dữ liệu và phân tích trước khi porting cho module: $MODULE_NAME.
      Source folder: $SOURCE_FOLDER. Target: Java.
      Output to: pre-porting-data/
  - label: Phase 1.5 – Generate Porting Plan
    agent: hi.porting-plan-generator
    prompt: |
      Sinh porting execution plan từ MCP Graph call graph.
      Module: $MODULE_NAME. Source: $SOURCE_FOLDER.
      Dựa trên pre-porting-data/ để có type mappings + compat info.
      Output: porting-output/porting-plan/ (porting-plan.md + porting-plan.json)
  - label: Phase 2 – File Structure Porting
    agent: hi.porting-file-structure
    prompt: |
      Port cấu trúc file (classes, interfaces, skeletons) cho module: $MODULE_NAME.
      Source folder: $SOURCE_FOLDER. Target: Java.
      Theo thứ tự trong: porting-output/porting-plan/porting-plan.json
  - label: Phase 3 – Function Porting (per file)
    agent: hi.porting-function
    prompt: |
      Port từng function với logic chi tiết cho file: $CURRENT_FILE.
      Source folder: $SOURCE_FOLDER. Target: Java.
      Sử dụng file structure đã port làm skeleton.
  - label: Validate & Report
    agent: hi.porting-cpp-to-java
    prompt: |
      Chạy validation compile & tạo porting report tổng hợp.
      Porting output folder: porting-output/
hooks:
  pre:
    - name: input-validation
      description: Validate required inputs (source_folder, module_name)
      required: true
    - name: mcp-health-check
      description: Verify MCP Graph connectivity before starting
      timeout: 15s
      required: true
  post:
    - name: cleanup-temp
      description: Clean up intermediate artifacts, keep final output
      paths: ["porting-output/"]
      keep: ["*.java", "*.md", "*.json"]
    - name: generate-summary
      description: Generate tổng kết porting report
---

# C++ to Java Porting Orchestrator (Master Agent)

> **Version:** 2.0  
> **Date:** 2026-05-13  
> **Purpose:** Điều phối end-to-end quy trình porting C++ → Java với MCP Graph support.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## Tham Số Bắt Buộc

| Tham số | Mô tả | Ví dụ |
|---------|-------|-------|
| `--source-folder` | Đường dẫn thư mục chứa C++ source | `/path/to/cpp/src` |
| `--module` | Tên module cần port | `module1` |
| `--output` | Thư mục output (mặc định: `porting-output/`) | `./output/module1` |

## Tham Số Tùy Chọn

| Tham số | Mô tả |
|---------|-------|
| `--file` | Port 1 file cụ thể (thay vì cả module) |
| `--function` | Port 1 function cụ thể |
| `--dry-run` | Chỉ phân tích, không sinh code |
| `--skip-validation` | Bỏ qua bước validate compile |

---

## Mục Tiêu

1. **Trace & Understand**: Dùng MCP Graph để hiểu cấu trúc C++ source
2. **Map**: Ánh xạ C++ constructs → Java equivalents
3. **Generate**: Sinh Java code với cấu trúc tương đương
4. **Validate**: Kiểm tra tính đúng đắn của code sinh ra

---

## 🎯 Priority #1: 1-1 Mapping Enforcement

> **ĐÂY LÀ TIÊU CHÍ ƯU TIÊN CAO NHẤT — TUYỆT ĐỐI KHÔNG ĐƯỢC VI PHẠM**

| Rule | Mô tả | Ví dụ C++ → Java |
|------|-------|-------------------|
| **R1** | **Package path** = C++ folder path (GIỮ NGUYÊN 100%) | `module1/sub/` → `package module1.sub;` |
| **R2** | **File name** = C++ file name, chỉ đổi extension | `SampleClassName.cpp` → `SampleClassName.java` |
| **R3** | **Class name** = C++ class name (KHÔNG refactor) | `SampleClassName` → `SampleClassName` |
| **R4** | **Method name** = C++ method name (GIỮ NGUYÊN) | `DoWork` → `DoWork` |
| **R5** | **Parameter name** = C++ param name (GIỮ NGUYÊN Hungarian) | `dwParam` → `dwParam` |
| **R6** | **Variable name** = C++ var name (GIỮ NGUYÊN) | `m_strName` → `m_strName` |
| **R7** | **Chỉ convert** type + syntax, KHÔNG đổi tên | `BOOL` → `boolean`, `CString` → `String` |

**Enforcement mechanism:**
- Sau mỗi phase, sub-agent PHẢI báo cáo danh sách tên đã giữ nguyên vs tên đã đổi
- Nếu phát hiện vi phạm 1-1 → **DỪNG NGAY**, báo lỗi, yêu cầu fix
- File output validate: so sánh class/method/param names giữa C++ source và Java output

**Lý do:** 1-1 mapping để dễ trace back, diff, verify correctness. Mọi refactor/naming convention sẽ làm SAU khi port hoàn tất.

---

## Coordination Loop (Vòng Lặp Điều Phối)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR LOOP                                  │
│                                                                           │
│  START ──► [1] Pre-Porting ──► [1.5] Plan Generator ──┐                  │
│    ▲                                                     │                  │
│    │                                                     ▼                  │
│    │                                        [2] File Structure Porting     │
│    │                                                     │                  │
│    │                                                     ▼                  │
│    │                                        [3] Function Porting           │
│    │                                                     │                  │
│    │                              ┌──────────────────────┼──────────┐      │
│    │                              ▼                      ▼          ▼      │
│    │                          file_1.java           file_2.java file_N.java│
│    │                              │                      │          │      │
│    │                              └──────────────────────┼──────────┘      │
│    │                                                     ▼                  │
│    └──────────────────────── [4] Validate & Report ◄─────┘                 │
│                              │                                             │
│                              ▼                                             │
│                            END                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

Quy tắc điều phối:
- **Phase 1 → Phase 1.5**: Sau khi pre-porting có type-mappings.json + migration-roadmap.md → sinh plan
- **Phase 1.5 → Phase 2**: Plan generator tạo porting-plan.md/json → bắt đầu port file structure theo plan
- **Phase 2 → Phase 3**: Với mỗi file trong plan, handoff sang Function Porting
- **Phase 3 → Loop**: Lặp lại cho từng file đến khi hết plan
- **Phase 3 → Phase 4**: Khi tất cả files đã port, chạy Validate & Report
- **Nếu lỗi ở bất kỳ phase nào**: Dừng và báo cáo, không tiếp tục

---

## Phase 1: Discovery (Khám Phá C++ Source)

### 1.1 Activate MCP Graph

```python
# Sử dụng source_folder từ tham số --source-folder
mcp_graph_mcp_activate_project(
    source_folder="$SOURCE_FOLDER",
    parser_type="cplus",
    database_name="neo4j"
)
```

### 1.2 Search Module/File cần port

```python
# Tìm tất cả functions trong module
result = mcp_graph_mcp_search_functions(
    db="neo4j",
    query="$MODULE_NAME",
    limit=500,
    content_mode="summary",
    include_raw_fields=False
)
```

### 1.3 Identify Entry Points & Key Classes

Phân loại theo pattern:

- **Entry points**: `*EntryPoint`, `StartWork`, `DoWork`, `main`, `Init*`
- **Handlers**: `On*`, `Handle*`, `Evt*`, `Rcv*`
- **Core classes**: Classes có nhiều callers nhất

### 1.4 Handoff sang Pre-Porting

Sau khi discovery hoàn tất, handoff sang `hi.pre-porting` để chuẩn bị:
- Compatibility gap analysis
- Type mappings C++→Java
- Migration roadmap với dependency order

---

## Phase 1.5: Porting Plan Generation

> **Sau khi pre-porting hoàn tất** (có `type-mappings.json`, `migration-roadmap.md`),
> handoff sang `hi.porting-plan-generator` để sinh execution plan chi tiết.

### 1.5.1 Input từ Pre-Porting

```
pre-porting-data/
├── type-mappings.json        → Type mapping rules cho plan
├── migration-roadmap.md      → High-level module roadmap
├── compat-layer-design.md    → Compat requirements per module
└── feature-gap-analysis.md   → C++ features cần bridge
```

### 1.5.2 Plan Generator Process

Agent `hi.porting-plan-generator` sẽ:

1. **Dùng MCP Graph call graph** để trace toàn bộ dependencies
2. **Module ordering**: `plan_dependency_order` → wave-based module sequence
3. **Class ordering** (per module): `plan_file_dependency_order` → class sequence
4. **Function ordering** (per class): `plan_function_dependency_order` → function sequence
5. **Leaf node detection**: Xác định functions không có dependency → parallel execution
6. **Circular dependency handling**: `compute_scc` → đề xuất resolution

### 1.5.3 Output

```
porting-output/porting-plan/
├── porting-plan.md            # Full plan + giải thích lý do từng bước
├── porting-plan.json          # Machine-readable structured plan
├── leaf-nodes.md              # 🌿 Parallel-executable functions
└── circular-deps.md           # ⚠️ Circular dependencies + resolution
```

### 1.5.4 Sử dụng Plan

- **Phase 2 (File Structure)**: Đọc `porting-plan.json` → port file theo wave order
- **Phase 3 (Function)**: Đọc function order trong plan → port từng function
- **Parallel execution**: Các function trong cùng wave + là leaf → port song song

---

## Phase 2: C++ → Java Mapping Rules (Reference)

> Các mapping rules này được dùng làm reference chung cho tất cả sub-agents.
> Chi tiết type mappings cụ thể sẽ do `hi.pre-porting` generate ra file `type-mappings.json`.

### 2.1 Type Mappings

| C++ Type               | Java Type          | Notes                         |
| ---------------------- | ------------------ | ----------------------------- |
| `int`, `long`          | `int`, `long`      | Xem xét overflow              |
| `char*`, `std::string` | `String`           | Immutable trong Java          |
| `bool`                 | `boolean`          |                               |
| `void*`                | `Object`           | Cần cast rõ ràng              |
| `std::vector<T>`       | `ArrayList<T>`     |                               |
| `std::map<K,V>`        | `HashMap<K,V>`     |                               |
| `std::set<T>`          | `HashSet<T>`       |                               |
| `std::unique_ptr<T>`   | `T`                | Java có GC                    |
| `std::shared_ptr<T>`   | `T`                | Java có GC                    |
| `T*` (pointer)         | `T` (reference)    | Java không có pointer         |
| `T&` (reference)       | `T`                | Pass by reference cho objects |
| `const T&`             | `final T`          | Immutable reference           |
| `unsigned int`         | `int`              | Cẩn thận với negative         |
| `size_t`               | `int` hoặc `long`  | Tùy context                   |
| `BYTE`, `UCHAR`        | `byte`             | Signed trong Java             |
| `WORD`, `USHORT`       | `short` hoặc `int` |                               |
| `DWORD`, `ULONG`       | `int` hoặc `long`  |                               |

### 2.2 Construct Mappings

| C++ Construct      | Java Equivalent                       |
| ------------------ | ------------------------------------- |
| `class`            | `class`                               |
| `struct`           | `class` (public fields) hoặc `record` |
| `enum`             | `enum`                                |
| `#define CONST`    | `static final`                        |
| `#define MACRO(x)` | `static method` hoặc inline           |
| `namespace`        | `package`                             |
| `template<T>`      | `<T>` generics                        |
| `virtual` method   | Abstract/interface method             |
| `override`         | `@Override`                           |
| `static` member    | `static`                              |
| `friend class`     | Package-private hoặc inner class      |
| `operator+`        | Method `add()`                        |
| `destructor ~`     | `close()` + `AutoCloseable`           |
| `try/catch`        | `try/catch`                           |
| `throw`            | `throw`                               |

### 2.3 Memory Management

| C++ Pattern    | Java Equivalent                |
| -------------- | ------------------------------ |
| `new T()`      | `new T()` (GC handles cleanup) |
| `delete ptr`   | (không cần - GC)               |
| `malloc/free`  | (không dùng - GC)              |
| RAII pattern   | `try-with-resources`           |
| Smart pointers | Regular references             |

### 2.4 Concurrency Mappings

| C++                       | Java                                  |
| ------------------------- | ------------------------------------- |
| `std::thread`             | `Thread` hoặc `ExecutorService`       |
| `std::mutex`              | `synchronized` hoặc `ReentrantLock`   |
| `std::condition_variable` | `Object.wait/notify` hoặc `Condition` |
| `std::atomic<T>`          | `AtomicInteger`, `AtomicReference`    |
| `volatile`                | `volatile` (khác semantics!)          |

---

## Phase 3: Porting Execution (via Sub-Agents)

> **Tất cả sub-agents PHẢI tuân theo thứ tự trong `porting-output/porting-plan/porting-plan.json`**

### 3.1 File-Level Porting → Handoff to `hi.porting-file-structure`

Với mỗi file trong plan (theo wave order):

1. Handoff đến `hi.porting-file-structure` với file path cụ thể
2. Sub-agent sẽ extract skeleton, map package, tạo Java file skeleton
3. Kết quả: `<exact_path>/<FileName>.java` với class + method stubs

### 3.2 Function-Level Porting → Handoff to `hi.porting-function`

Với mỗi file đã có skeleton (theo function order trong plan):

1. Handoff đến `hi.porting-function` với file path + function name
2. Sub-agent sẽ extract function body, convert logic, fill implementation
3. Kết quả: Function body đã được port với logic tương đương

### 3.3 Parallel Execution (Leaf Nodes)

Các function được đánh dấu 🌿 trong `porting-plan/leaf-nodes.md`:
- **Có thể port song song** trong cùng wave
- Không phụ thuộc lẫn nhau → an toàn để parallel
- Orchestrator có thể spawn multiple `hi.porting-function` agents đồng thời

### 3.3 Header File Handling

| C++ Header Content  | Java Equivalent               |
| ------------------- | ----------------------------- |
| Class declaration   | Trong cùng `.java` file       |
| Function prototypes | Interface hoặc abstract class |
| `#include`          | `import`                      |
| `#define`           | `static final` trong class    |
| `typedef`           | Không cần hoặc wrapper class  |
| `extern`            | `public static`               |

---

## Phase 4: Special Patterns

### 4.1 Windows API / MFC Mappings

| C++/MFC          | Java Equivalent                 |
| ---------------- | ------------------------------- |
| `CString`        | `String`                        |
| `CArray`         | `ArrayList`                     |
| `CMap`           | `HashMap`                       |
| `CFile`          | `java.io.File` + streams        |
| `CSocket`        | `java.net.Socket`               |
| `CThread`        | `Thread`                        |
| `CEvent`         | `CountDownLatch` / `Semaphore`  |
| `HWND`, `HANDLE` | Application-specific wrapper    |
| `SendMessage`    | Method call / Event bus         |
| `PostMessage`    | Async queue / `ExecutorService` |

### 4.2 IPC / Message Passing

```python
# Tìm IPC messages trong module
ipc = mcp_graph_mcp_get_ipc_message(
    sender="ModuleA",
    receiver="ModuleB"
)
```

Chuyển đổi:

- Mailslot → `BlockingQueue` hoặc message broker
- Shared memory → Shared objects với synchronization
- Named pipes → `PipedInputStream/OutputStream` hoặc sockets

### 4.3 Callback / Function Pointer

| C++                         | Java                                 |
| --------------------------- | ------------------------------------ |
| Function pointer            | Interface + lambda                   |
| `std::function<R(Args...)>` | `Function<T,R>`, `Consumer<T>`, etc. |
| Callback registration       | Listener pattern                     |

---

## Phase 5: Output Structure

### 5.1 Generated Files

```
porting-output/
├── <module>/
│   ├── src/main/java/
│   │   └── <package>/
│   │       ├── <ClassName>.java
│   │       └── ...
│   ├── porting-report.md          # Báo cáo porting
│   ├── type-mappings-used.json    # Type mappings đã dùng
│   ├── unmapped-constructs.md     # Các construct chưa map được
│   └── manual-review-needed.md    # Cần review thủ công
├── pre-porting-data/              # Output từ hi.pre-porting
│   ├── type-mappings.json
│   ├── migration-roadmap.md
│   └── ...
├── porting-plan/                  # Output từ hi.porting-plan-generator (NEW)
│   ├── porting-plan.md            # Plan execution đầy đủ + giải thích
│   ├── porting-plan.json          # Machine-readable structured plan
│   ├── leaf-nodes.md              # Danh sách leaf nodes (parallel)
│   └── circular-deps.md           # Circular dependencies + resolution
└── compat-layer/
    └── src/main/java/
        └── compat/
            ├── CString.java       # Compat cho CString
            ├── WinApi.java        # Compat cho Windows API
            └── ...
```

### 5.2 Porting Report Template

```markdown
# Porting Report: <Module>

## Summary
- Source files: X
- Generated Java files: Y
- Functions ported: Z
- Manual review needed: N

## Type Mappings Applied
| C++ Type | Java Type | Count |
|----------|-----------|-------|
| ...      | ...       | ...   |

## Unmapped Constructs
- [ ] `construct1` - Reason

## Manual Review Required
1. File: `X.java`, Line: Y - Reason
```

---

## Phase 6: Validation

### 6.1 Compile Check

```bash
cd porting-output/<module>
javac -d target/classes src/main/java/**/*.java
```

### 6.2 Static Analysis

- Chạy linter (Checkstyle, SpotBugs)
- Kiểm tra null safety
- Kiểm tra resource leaks

### 6.3 Logic Verification

So sánh behavior:

1. Identify test cases từ C++ (nếu có)
2. Port test cases sang JUnit
3. Verify outputs match

---

## Usage

```bash
# Port toàn bộ module
@agent hi.porting-cpp-to-java \
  --source-folder /path/to/cpp/src \
  --module module1 \
  --output ./porting-output

# Port 1 file cụ thể
@agent hi.porting-cpp-to-java \
  --source-folder /path/to/cpp/src \
  --file module1/SampleClassName.cpp

# Dry-run (chỉ phân tích)
@agent hi.porting-cpp-to-java \
  --source-folder /path/to/cpp/src \
  --module module1 \
  --dry-run
```

---

## Best Practices

1. **Port theo dependency order**: Port các utility/base classes trước (theo `migration-roadmap.md`)
2. **Tạo compat layer sớm**: Cho các Windows/MFC APIs trước khi port business logic
3. **Giữ nguyên naming**: 1-1 mapping để dễ trace back về source
4. **Document unmapped**: Ghi rõ những gì cần manual review vào `unmapped-constructs.md`
5. **Incremental**: Port từng file/function, validate compile liên tục
6. **Preserve comments**: Giữ comments từ C++ source trong Java code

---

## Troubleshooting

| Issue                | Solution                                  |
| -------------------- | ----------------------------------------- |
| Circular dependency  | Refactor thành interface + implementation |
| Multiple inheritance | Interface cho additional parents          |
| Operator overloading | Explicit methods (`add()`, `equals()`)    |
| Preprocessor macros  | Inline hoặc static methods                |
| Pointer arithmetic   | Array indexing hoặc ByteBuffer            |
| Global variables     | Singleton hoặc dependency injection       |
| MCP Graph không kết nối | Kiểm tra Neo4j đang chạy, verify parser_type |

---

## Related Agents

| Agent | Vai trò | Khi nào gọi |
|-------|---------|-------------|
| `hi.pre-porting` | Chuẩn bị analysis + compat layer | Phase 1 |
| `hi.porting-plan-generator` | **Sinh porting execution plan (module→class→function order)** | Phase 1.5 |
| `hi.porting-file-structure` | Port cấu trúc file (skeleton) | Phase 2 |
| `hi.porting-function` | Port logic từng function | Phase 3 |
| `hi.porting-cpp-to-java` | Orchestrator + Validate | Phase 4 (self-handoff) |

---

---

## 🔧 MCP Tools Reference

### graph_mcp (`http://127.0.0.1:8788/mcp`)

| Tool | Purpose | Dùng ở Phase |
|------|---------|-------------|
| `mcp_graph_mcp_activate_project` | Kích hoạt phân tích C++ source folder + parser_type=`cplus` | 1, 1.5 |
| `mcp_graph_mcp_search_functions` | Tìm functions theo tên/pattern/file trong module | 1, 1.5 |
| `mcp_graph_mcp_get_symbol` | Lấy metadata chi tiết: names, params, types, body | 1, 1.5, 2, 3 |
| `mcp_graph_mcp_get_node_details` | Lấy full code node (alternative get_symbol) | 3 |
| `mcp_graph_mcp_impact` | Phân tích dependency graph (callers/callees) | 1, 1.5, 2, 3 |
| `mcp_graph_mcp_find_paths` | Tìm đường dẫn giữa 2 functions | 1.5, 2 |
| `mcp_graph_mcp_query_subgraph` | Query subgraph quanh 1 node | 1, 1.5, 2 |
| `mcp_graph_mcp_get_ipc_message` | Lấy IPC message definitions giữa modules | 1, 1.5, 2 |
| `mcp_graph_mcp_annotate_node` | Gán metadata (compat requirements) vào node | 2 |
| `mcp_graph_mcp_plan_dependency_order` | **KEY** — Module-level dependency ordering cho plan | 1.5 |
| `mcp_graph_mcp_plan_file_dependency_order` | **KEY** — File/class-level dependency ordering | 1.5 |
| `mcp_graph_mcp_plan_function_dependency_order` | **KEY** — Function-level dependency ordering | 1.5 |
| `mcp_graph_mcp_compute_scc` | **KEY** — Phát hiện circular dependencies | 1.5 |
| `mcp_graph_mcp_topological_sort` | Topological sort dependency graph | 1.5 |

### mind_mcp (`http://127.0.0.1:8789/mcp`)

| Tool | Purpose | Dùng ở Phase |
|------|---------|-------------|
| `mcp_mind_mcp_search_knowledge` | Tìm tài liệu, design docs, historical context về module C++ | 1, 2 |
| `mcp_mind_mcp_get_document` | Lấy nội dung tài liệu cụ thể (spec, design doc) | 1, 2 |
| `mcp_mind_mcp_query_context` | Query historical context: tại sao module được thiết kế như vậy | 1 |
| `mcp_mind_mcp_find_related` | Tìm modules/docs liên quan đến module đang port | 1, 2 |

---

**Owner**: baka3k  
**Version**: 2.0 — 2026-05-13
