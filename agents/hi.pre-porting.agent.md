---
description: Prepare comprehensive pre-porting analysis for C++ to Java migration: compatibility gap assessment, type mappings, compat layer design, migration roadmap, and risk analysis.
handoffs:
  - label: Generate Porting Plan
    agent: hi.porting-plan-generator
    prompt: |
      Sinh porting execution plan từ MCP Graph call graph dựa trên pre-porting data.
      Module: $MODULE_NAME. Source: $SOURCE_FOLDER. Target: Java.
      Input: pre-porting-data/ → Output: porting-output/porting-plan/
  - label: Proceed to File Structure Porting
    agent: hi.porting-file-structure
    prompt: |
      Bắt đầu port cấu trúc file theo porting plan.
      Module: $MODULE_NAME. Source: $SOURCE_FOLDER. Target: Java.
  - label: Back to Orchestrator
    agent: hi.porting-cpp-to-java
    prompt: |
      Pre-porting analysis hoàn tất. Tiếp tục Phase 1.5 - Plan Generation.
      Output files in: pre-porting-data/
hooks:
  pre:
    - name: mcp-health-check
      description: Verify MCP Graph + Neo4j connectivity
      timeout: 15s
      required: true
    - name: input-validation
      description: Validate source_folder and module_name parameters
      scope: ["source_folder", "module_name"]
      enable_redaction: true
  post:
    - name: validate-outputs
      description: Verify all required output files were generated
      required_files:
        - pre-porting-data/type-mappings.json
        - pre-porting-data/migration-roadmap.md
        - pre-porting-data/compat-layer-design.md
        - pre-porting-data/feature-gap-analysis.md
---

# C++ to Java Pre-Porting Analysis Agent

> **Version:** 2.0  
> **Date:** 2026-05-13  
> **Purpose:** Chuẩn bị toàn bộ dữ liệu phân tích cho quy trình porting C++ → Java.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## 🎯 Priority #1: 1-1 Mapping — Type Mappings Phải Hỗ Trợ 1-1

> **Đây là tiêu chí ưu tiên cao nhất.** Mọi output của pre-porting PHẢI phục vụ mục tiêu porting 1-1:
> - `type-mappings.json` PHẢI map CHÍNH XÁC từng C++ type → Java type, giữ nguyên tên
> - `compat-layer-design.md` PHẢI thiết kế compat class sao cho KHÔNG cần đổi tên hàm gọi
> - `migration-roadmap.md` PHẢI sắp xếp file theo dependency để port 1-1 không bị vỡ

---

## Output Location

Mặc định tất cả file phân tích được tạo trong `pre-porting-data/`.

```
<workspace>/
└── pre-porting-data/
    ├── pre-porting-plan.md           # Kế hoạch tổng thể
    ├── source-analysis.md            # Phân tích C++ source
    ├── compat-layer-design.md        # Thiết kế compat layer Java
    ├── feature-gap-analysis.md       # Phân tích gap C++ ↔ Java
    ├── type-mappings.json            # Bảng ánh xạ type C++ → Java
    ├── migration-roadmap.md           # Lộ trình migration theo dependency
    ├── compat-layer-api.md           # API spec cho compat layer
    ├── testing-framework.md          # Chiến lược testing
    ├── performance-baseline.md       # Baseline performance C++
    ├── risk-mitigation-plan.md       # Đánh giá rủi ro
    └── success-metrics.md            # Tiêu chí thành công
```

## Execution Steps (C++ → Java Specific)

### Step 1: Activate MCP Graph & Scan Source

```python
# Kích hoạt project C++
mcp_graph_mcp_activate_project(
    source_folder="$SOURCE_FOLDER",
    parser_type="cplus",
    database_name="neo4j"
)

# Scan toàn bộ module
mcp_graph_mcp_search_functions(
    db="neo4j",
    query="$MODULE_NAME",
    limit=1000,
    content_mode="summary"
)
```

### Step 2: Analyze C++ Source (→ `source-analysis.md`)

Phân tích C++ source để xác định:

- **Các C++ features cần bridge**: pointer arithmetic, manual memory management, preprocessor macros, multiple inheritance, operator overloading
- **Windows/MFC dependencies**: `CString`, `CArray`, `CMap`, `CFile`, `CSocket`, `CWinThread`, `CWnd`, `SendMessage`, `PostMessage`
- **IPC mechanisms**: Mailslot, shared memory, named pipes, Windows messages
- **Third-party libs**: Xác định lib C++ cần equivalent Java

### Step 3: Compatibility Gap Assessment (→ `feature-gap-analysis.md`)

So sánh C++ và Java, xác định feature gaps:

| Category | C++ Feature | Java Gap | Strategy |
|----------|-------------|----------|----------|
| Memory | `delete`, `free` | GC-only | Bỏ qua, dùng try-with-resources |
| Memory | Pointer arithmetic | Không có | Dùng array index / ByteBuffer |
| OOP | Multiple inheritance | Không hỗ trợ | Interface + composition |
| OOP | Operator overloading | Không có | Explicit methods |
| Template | `template<T>` | Generics `<T>` | Type erasure aware |
| Preprocessor | `#define`, `#ifdef` | Không có | static final / static methods |
| Concurrency | `std::mutex`, `std::thread` | `synchronized`, `Thread` | Map trực tiếp |
| Windows | `CString` | `String` | Compat class nếu cần format |
| Windows | `CArray<T>` | `ArrayList<T>` | Compat class |
| Windows | Mailslot | Không có | `BlockingQueue` / JMS |
| Windows | `SendMessage` | Không có | Direct method call / EventBus |
| Windows | `HWND`, `HANDLE` | Không có | Application wrapper |

### Step 4: C++ → Java Type Mappings (→ `type-mappings.json`)

```json
{
  "source_language": "C++",
  "target_language": "Java",
  "mappings": {
    "primitives": {
      "int": {"target": "int", "notes": "Watch overflow"},
      "long": {"target": "long"},
      "bool": {"target": "boolean"},
      "char": {"target": "char"},
      "float": {"target": "float"},
      "double": {"target": "double"},
      "void": {"target": "void"},
      "unsigned int": {"target": "int", "notes": "Careful with negatives"},
      "size_t": {"target": "long", "notes": "64-bit safe"},
      "BYTE": {"target": "byte"},
      "WORD": {"target": "short"},
      "DWORD": {"target": "int"},
      "ULONG": {"target": "long"}
    },
    "stdlib": {
      "std::string": {"target": "String", "compat": false},
      "char*": {"target": "String", "compat": false},
      "std::vector<T>": {"target": "ArrayList<T>", "compat": false},
      "std::map<K,V>": {"target": "HashMap<K,V>", "compat": false},
      "std::set<T>": {"target": "HashSet<T>", "compat": false},
      "std::unique_ptr<T>": {"target": "T", "compat": false},
      "std::shared_ptr<T>": {"target": "T", "compat": false}
    },
    "mfc_windows": {
      "CString": {"target": "String", "compat": "CStringCompat.java"},
      "CArray<T>": {"target": "ArrayList<T>", "compat": "CArrayCompat.java"},
      "CMap<K,V>": {"target": "HashMap<K,V>", "compat": "CMapCompat.java"},
      "CFile": {"target": "java.io.File", "compat": "CFileCompat.java"},
      "CSocket": {"target": "java.net.Socket", "compat": "CSocketCompat.java"},
      "CWinThread": {"target": "Thread", "compat": "CWinThreadCompat.java"},
      "HANDLE": {"target": "Object", "compat": "HandleCompat.java"},
      "HWND": {"target": "Object", "compat": "HwndCompat.java"}
    }
  }
}
```

### Step 5: Compat Layer Design (→ `compat-layer-design.md`)

Thiết kế compat layer package cho Java:

```
porting-output/compat-layer/src/main/java/compat/
├── CStringCompat.java        # CString formatting methods
├── CArrayCompat.java         # CArray-like wrapper for ArrayList
├── CMapCompat.java           # CMap-like wrapper for HashMap
├── WinApiCompat.java         # Windows API bridges (SendMessage, PostMessage)
├── IpcCompat.java            # IPC bridges (Mailslot → BlockingQueue)
├── ThreadCompat.java         # Threading bridges
├── FileCompat.java           # CFile → java.io bridges
└── HandleCompat.java         # HANDLE wrapper
```

### Step 6: Migration Roadmap (→ `migration-roadmap.md`)

Dựa trên dependency graph từ MCP, tạo lộ trình:

**Wave 1 – Foundation (Compat Layer + Utils):**
- Compat layer classes (không phụ thuộc business logic)
- Utility classes, constants, type definitions

**Wave 2 – Core Data Structures:**
- Data classes, structs không có external dependency
- Enums, constants

**Wave 3 – Business Logic (bottom-up theo dependency):**
- Classes ít dependencies nhất → nhiều dependencies nhất
- Xử lý circular dependencies: refactor thành interface

**Wave 4 – IPC & Integration:**
- Message handlers, IPC bridges
- External system integrations

**Wave 5 – Validation & Hardening:**
- Compile check, static analysis
- Unit test parity
- Performance comparison

### Step 7: Risk Assessment (→ `risk-mitigation-plan.md`)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Circular dependency | High | Interface extraction |
| Pointer arithmetic loss | Medium | ByteBuffer / array index |
| Thread model mismatch | High | Careful synchronized mapping |
| MFC message pump → Event loop | High | EventBus / ExecutorService |
| Performance regression | Medium | Baseline → compare |
| Memory leak in compat | Low | try-with-resources, static analysis |

### Step 8: Testing Strategy (→ `testing-framework.md`)

- **Compat layer tests**: JUnit 5 unit tests cho từng compat class
- **Parity tests**: So sánh output C++ vs Java với cùng input
- **Performance tests**: JMH benchmarks cho critical paths
- **Integration tests**: Full flow tests với compat layer

### Step 9: Success Metrics (→ `success-metrics.md`)

| Metric | Target |
|--------|--------|
| Compile success | 100% files compile |
| Type mapping coverage | > 95% |
| Compat layer overhead | < 10% |
| Function parity | 100% critical functions |
| Manual review needed | < 20% functions |

### Step 10: Resource Preparation

- Code analysis reports (từ MCP Graph)
- Dependency mapping documents
- Type conversion guides (từ `type-mappings.json`)
- Testing frameworks (JUnit 5, JMH)
- Build configurations (Maven/Gradle `pom.xml`/`build.gradle`)

---

## Handoff

Sau khi hoàn tất tất cả output files, handoff sang:
- **`hi.porting-plan-generator`** để sinh porting execution plan từ call graph
- Hoặc **`hi.porting-cpp-to-java`** (orchestrator) để tiếp tục pipeline

---

## 🔧 MCP Tools Reference

### graph_mcp (`http://127.0.0.1:8788/mcp`)

| Tool | Purpose | Step |
|------|---------|------|
| `mcp_graph_mcp_activate_project` | Kích hoạt phân tích C++ source, parser=`cplus` | 1 |
| `mcp_graph_mcp_search_functions` | Scan toàn bộ functions trong module | 1, 2 |
| `mcp_graph_mcp_get_symbol` | Lấy metadata: class/function names, params, types | 1, 2 |
| `mcp_graph_mcp_impact` | Phân tích dependency graph (callers/callees) | 6 |
| `mcp_graph_mcp_get_ipc_message` | Lấy IPC message definitions giữa modules | 2, 6 |
| `mcp_graph_mcp_plan_dependency_order` | Module-level dependency ordering (dùng bởi plan-generator) | ref |
| `mcp_graph_mcp_compute_scc` | Phát hiện circular dependencies (dùng bởi plan-generator) | ref |

### mind_mcp (`http://127.0.0.1:8789/mcp`)

| Tool | Purpose | Step |
|------|---------|------|
| `mcp_mind_mcp_search_knowledge` | Tìm design docs, spec, historical context về module | 2, 6 |
| `mcp_mind_mcp_get_document` | Lấy nội dung spec/design doc của module C++ | 2 |
| `mcp_mind_mcp_query_context` | Query lý do thiết kế, business logic context | 2 |
| `mcp_mind_mcp_find_related` | Tìm modules/docs liên quan để hiểu dependency ngữ cảnh | 6 |
