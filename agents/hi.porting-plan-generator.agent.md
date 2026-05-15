---
description: Tạo porting execution plan hoàn chỉnh từ MCP Graph call graph sau pre-porting. Phân tích dependency → topological sort → module/class/function ordering → wave-based plan. Output 2 định dạng: porting-plan.md (có giải thích) + porting-plan.json (machine-readable).
variables:
  input:
    - name: $SOURCE_FOLDER
      source: CLI --source-folder
      required: true
    - name: $MODULE_NAME
      source: CLI --module
      required: true
    - name: $OUTPUT_DIR
      source: CLI --output (default: porting-output/)
      required: false
  internal:
    - name: pre-porting-data/type-mappings.json
      source: pre-porting output
      required: true
    - name: pre-porting-data/migration-roadmap.md
      source: pre-porting output
      required: true
    - name: pre-porting-data/compat-layer-design.md
      source: pre-porting output
      required: false
  output:
    - name: porting-plan.md
      path: porting-output/porting-plan/porting-plan.md
      required: true
    - name: porting-plan.json
      path: porting-output/porting-plan/porting-plan.json
      required: true
    - name: $FIRST_MODULE
      computed: first module in plan
      required: true
handoffs:
  - label: Start File Structure Porting
    agent: hi.porting-file-structure
    prompt: |
      Bắt đầu port file structure theo porting plan trong porting-output/porting-plan.md.
      Module đầu tiên: $FIRST_MODULE. Source: $SOURCE_FOLDER. Target: Java.
      Sử dụng plan waves để biết thứ tự từng file.
  - label: Back to Orchestrator
    agent: hi.porting-cpp-to-java
    prompt: |
      Porting plan đã sẵn sàng tại porting-output/porting-plan.md + porting-plan.json.
      Tiếp tục Phase 2 - File Structure Porting theo plan.
hooks:
  pre:
    - name: mcp-health-check
      description: Verify graph_mcp + mind_mcp connectivity
      timeout: 15s
      required: true
    - name: verify-pre-porting
      description: Verify pre-porting-data/ outputs exist (type-mappings.json, migration-roadmap.md)
      required_files:
        - pre-porting-data/type-mappings.json
        - pre-porting-data/migration-roadmap.md
      required: true
    - name: verify-graph-active
      description: Verify project đã được activate trong graph_mcp
      required: true
  post:
    - name: validate-plan
      description: Verify plan có coverage 100% functions, không bỏ sót
      required: true
    - name: validate-leaf-nodes
      description: Xác nhận leaf nodes thực sự không có dependency
---

# Porting Plan Generator Agent

> **Version:** 1.0  
> **Date:** 2026-05-13  
> **Purpose:** Sinh kế hoạch porting chi tiết từ MCP Graph call graph: module→class→function ordering, wave-based plan, parallel leaf nodes.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## 🎯 Mục Tiêu

Sau khi `hi.pre-porting` hoàn tất, agent này sẽ:

1. **Dùng MCP Graph call graph** để phân tích toàn bộ dependencies giữa các module, class, function
2. **Topological sort** để xác định thứ tự porting tối ưu (dependency trước, dependents sau)
3. **Xác định leaf nodes** (không phụ thuộc vào đâu) để thực hiện song song
4. **Phát hiện circular dependencies** và đề xuất cách xử lý
5. **Output 2 định dạng**: `porting-plan.md` (human-readable, có giải thích) + `porting-plan.json` (machine-readable)

---

## 🎯 Priority #1: 1-1 Mapping — Plan Phải Tôn Trọng 1-1

> Kế hoạch porting KHÔNG được đề xuất đổi tên/refactor. 
> **Tất cả** các yếu tố sau phải GIỮ NGUYÊN từ C++ source:
> - **Package/folder path** → Java package name (GIỮ NGUYÊN 100%, chỉ thay `/` → `.`)
> - **File name** → Java file name (giữ nguyên, chỉ đổi extension)
> - **Class name** → Java class name (GIỮ NGUYÊN tuyệt đối)
> - **Function name** → Java method name (GIỮ NGUYÊN)
> - **Parameter name** → Java param name (GIỮ NGUYÊN)
> 
> Cột `Java Package` trong full listing table PHẢI là C++ folder path convert 1-1.

---

## Tham Số

| Tham số | Mô tả | Ví dụ |
|---------|-------|-------|
| `--source-folder` | Thư mục gốc C++ source | `/path/to/cpp/src` |
| `--module` | Tên module cần lập plan (mặc định: tất cả) | `ModuleSample01` |
| `--output` | Thư mục output (mặc định: `porting-output/`) | `./output` |
| `--max-depth` | Độ sâu phân tích dependency (mặc định: 5) | `3` |
| `--parallel-limit` | Số leaf nodes tối đa cho parallel (mặc định: 10) | `5` |

---

## Phase 0: Preflight

### 0.1 Verify graph_mcp connectivity

```python
# Xác nhận project đã activate
mcp_graph_mcp_activate_project(
    source_folder="$SOURCE_FOLDER",
    parser_type="cplus",
    database_name="neo4j"
)
```

### 0.2 Load pre-porting data

```python
# Load type mappings và migration roadmap từ pre-porting
type_mappings = load_json("pre-porting-data/type-mappings.json")
migration_roadmap = load_md("pre-porting-data/migration-roadmap.md")
compat_design = load_md("pre-porting-data/compat-layer-design.md")
```

---

## Phase 1: Module-Level Ordering

### 1.1 Scan all modules

```python
# Lấy danh sách tất cả modules/files
all_functions = mcp_graph_mcp_search_functions(
    db="neo4j",
    query="$MODULE_NAME",
    limit=2000,
    content_mode="summary"
)
```

### 1.2 Build inter-module dependency graph

```python
# Sử dụng plan_dependency_order để có module ordering
module_order = mcp_graph_mcp_plan_dependency_order(
    db="neo4j",
    scope="module",
    direction="dependency_first"
)
# Returns: [{module: "ModuleSample01", dependencies: [], wave: 0}, ...]
```

### 1.3 Identify cycles giữa modules

```python
# Phát hiện strongly connected components
sccs = mcp_graph_mcp_compute_scc(
    db="neo4j",
    scope="module"
)
# Returns: [{scc_id: 1, modules: ["ModA", "ModB"], is_circular: true}, ...]
```

### 1.4 Generate Module Wave Table

| Wave | Module | Dependencies | Lý do |
|------|--------|-------------|-------|
| 0 | `UtilsLib` | (none) | Utility library, không depend vào module nào |
| 0 | `CommonTypes` | (none) | Shared types, không depend |
| 1 | `DataLayer` | `UtilsLib`, `CommonTypes` | Cần utility + types trước |
| 1 | `NetworkMgr` | `UtilsLib` | Cần utility |
| 2 | `ModuleSample01` | `DataLayer`, `NetworkMgr`, `CommonTypes` | Business logic module |
| 2 | `ModuleSample02` | `DataLayer`, `CommonTypes` | Business logic module |
| 3* | `ModA`, `ModB` | Circular: ModA↔ModB | Cần refactor interface |

> *Wave 3: circular dependency → xử lý đặc biệt

---

## Phase 2: Class-Level Ordering (per module)

Với mỗi module trong wave order:

### 2.1 Get all classes in module

```python
# Tìm tất cả classes trong module
classes = mcp_graph_mcp_search_functions(
    db="neo4j",
    query="class:$MODULE_NAME",
    limit=500,
    content_mode="summary"
)
```

### 2.2 Build class dependency graph

```python
# Với mỗi class, lấy danh sách callees (classes khác nó gọi)
for cls in classes:
    deps = mcp_graph_mcp_impact(
        function_id=cls.id,
        direction="callees",
        max_depth=1
    )
    # Phân loại callees theo class
```

### 2.3 Class topological ordering

```python
# Order classes trong module theo dependency
class_order = mcp_graph_mcp_plan_file_dependency_order(
    db="neo4j",
    module="$MODULE_NAME",
    direction="dependency_first"
)
```

### 2.4 Generate Class Order Table (per module)

**Module: ModuleSample01**

| Order | Class | Dependencies | Wave | Lý do |
|-------|-------|-------------|------|-------|
| 1 | `CModuleSampleConfig` | (none) | 0 | Config class, không depend |
| 2 | `CModuleSampleData` | (none) | 0 | Data struct, không depend |
| 3 | `CModuleSampleUtility` | `CModuleSampleConfig`, `CModuleSampleData` | 1 | Cần config + data |
| 4 | `CModuleSampleHandler` | `CModuleSampleUtility` | 2 | Cần utility |
| 5 | `CModuleSampleActivity` | `CModuleSampleHandler`, `CModuleSampleData` | 3 | Main activity class |
| 🔄 | `CModuleSampleA`, `CModuleSampleB` | Circular: A↔B | * | Extract interface |

---

## Phase 3: Function-Level Ordering (per class)

Với mỗi class trong class order:

### 3.1 Get all methods

```python
# Lấy tất cả methods của class
methods = mcp_graph_mcp_query_subgraph(
    db="neo4j",
    function_id=class_entry_id,
    direction="callees",
    max_depth=1,
    content_mode="summary"
)
```

### 3.2 Build function call graph

```python
# Với mỗi method, lấy callees
for method in methods:
    callees = mcp_graph_mcp_impact(
        function_id=method.id,
        direction="callees",
        max_depth=1
    )
```

### 3.3 Function topological ordering

```python
# Order functions trong class theo dependency
func_order = mcp_graph_mcp_plan_function_dependency_order(
    db="neo4j",
    class_id=class_entry_id,
    direction="dependency_first"
)
```

### 3.4 Generate Function Order Table (per class)

**Class: CModuleSampleActivity**

| Order | Function | Signature | Dependencies | Wave | Leaf? | Lý do |
|-------|----------|-----------|-------------|------|-------|-------|
| 1 | `InitInstance` | `BOOL InitInstance()` | (none) | 0 | 🌿 | Khởi tạo, không gọi ai |
| 2 | `LoadConfig` | `BOOL LoadConfig(CString)` | (none) | 0 | 🌿 | Đọc config từ file |
| 3 | `SetupHandlers` | `void SetupHandlers()` | `InitInstance`, `LoadConfig` | 1 | | Cần init + config |
| 4 | `DoWork` | `BOOL DoWork(DWORD, LPTSTR)` | `SetupHandlers` | 2 | | Main work logic |
| 5 | `OnReceive` | `void OnReceive(LPVOID, DWORD)` | `DoWork` | 3 | | Xử lý message |
| 6 | `Cleanup` | `void Cleanup()` | `OnReceive` | 4 | | Cleanup sau cùng |

> 🌿 = Leaf node: không bị function nào khác trong module depend vào → **Có thể port song song**

---

## Phase 4: Identify Leaf Nodes cho Parallel Execution

### 4.1 Định nghĩa Leaf Node

Một function/class/module là **leaf** nếu:
- Nó **không được gọi bởi** bất kỳ function/class/module nào khác trong scope porting
- Nó **chỉ gọi ra ngoài** (là consumer, không phải provider)

### 4.2 Leaf Detection Algorithm

```python
# 1. Build full call graph (caller → callee)
# 2. Đảo ngược: callee → callers
# 3. Leaf = node có 0 callers trong scope
all_nodes = get_all_functions_in_scope()
callers_map = {}  # callee_id → [caller_ids]

for node in all_nodes:
    callees = mcp_graph_mcp_impact(node.id, direction="callees", max_depth=1)
    for callee in callees:
        callers_map.setdefault(callee.id, []).append(node.id)

leaf_nodes = [n for n in all_nodes if n.id not in callers_map]
```

### 4.3 Leaf Node Table

```
📊 LEAF NODES — Có thể port SONG SONG
═══════════════════════════════════════════════════════════
Module          Class            Function               Wave
───────────────────────────────────────────────────────────
UtilsLib        CStringUtil      Trim                   W0
UtilsLib        CStringUtil      Split                  W0
CommonTypes     CTypeDefs        GetTypeName            W0
CommonTypes     CEnumHelper      ToString               W0
DataLayer       CDbConfig        LoadDbConfig           W1
NetworkMgr      CSocketInit      InitWinsock            W1
ModuleSample01          CModuleSampleConfig      LoadConfig             W2
ModuleSample01          CModuleSampleData        Serialize              W2
ModuleSample02          CModuleSample02Config    LoadConfig             W2
...
───────────────────────────────────────────────────────────
Total leaf nodes: 47 / 215 functions (21.8%)
═══════════════════════════════════════════════════════════
```

---

## Phase 5: Generate Complete Execution Plan

> **YÊU CẦU BẮT BUỘC:** Plan phải liệt kê **tất cả** module/class/function trong scope (KHÔNG phải ví dụ).
> Mỗi function nhận 1 **số thứ tự GLOBAL duy nhất** (F001, F002, ...), không phân theo wave.

### 5.1 Consolidated Full Listing (BẮT BUỘC)

Sau khi có đủ wave/class/function ordering từ Phase 1-4, tạo **1 bảng duy nhất liệt kê tất cả functions**:

```markdown
# 📋 FULL PORTING LIST — ModuleSample01

**Tổng cộng:** 5 modules | 23 classes | 215 functions | 4 waves | 47 leaf nodes
═══════════════════════════════════════════════════════════════════════════════════

| STT | ID     | Module       | Class                | Function          | Signature                     | C++ File           | Java Package  | Wave | Leaf | Dependencies         |
|-----|--------|-------------|----------------------|-------------------|-------------------------------|--------------------|---------------|------|------|----------------------|
| 1   | F001   | UtilsLib     | CStringUtil          | Trim              | CString Trim(CString)         | utils/CString.cpp  | utils         | W0   | 🌿   | —                    |
| 2   | F002   | UtilsLib     | CStringUtil          | Split             | CArray<CString> Split(...)    | utils/CString.cpp  | utils         | W0   | 🌿   | —                    |
| 3   | F003   | UtilsLib     | CStringUtil          | Format            | CString Format(CString, ...)  | utils/CString.cpp  | utils         | W0   | 🌿   | —                    |
| ... | ...    | ...          | ...                  | ...               | ...                           | ...                | ...           | ...  | ...  | ...                  |
| 45  | F045   | DataLayer    | CDbConfig            | LoadDbConfig      | BOOL LoadDbConfig(CString)    | data/DbConfig.cpp  | data          | W1   |      | F003                |
| 46  | F046   | DataLayer    | CDbConfig            | ParseConnection   | BOOL ParseConnection(LPTSTR)  | data/DbConfig.cpp  | data          | W1   |      | F003                |
| ... | ...    | ...          | ...                  | ...               | ...                           | ...                | ...           | ...  | ...  | ...                  |
| 210 | F210   | ModuleSample01 | CModuleSampleActivity | DoWork            | BOOL DoWork(DWORD, LPTSTR)    | act/Activity.cpp   | act           | W3   |      | F045, F167          |
| 211 | F211   | ModuleSample01 | CModuleSampleActivity | OnReceive         | void OnReceive(LPVOID,DWORD)  | act/Activity.cpp   | act           | W3   |      | F210                |
| 212 | F212   | ModuleSample01 | CModuleSampleActivity | Cleanup           | void Cleanup()                | act/Activity.cpp   | act           | W4   |      | F211                |
| ... | ...    | ...          | ...                  | ...               | ...                           | ...                | ...           | ...  | ...  | ...                  |
| 215 | F215   | ModuleSample01 | CModuleSampleDispatcher | Dispatch       | void Dispatch(DWORD)          | act/Dispatcher.cpp | act           | W4   | 🌿   | —                    |
═══════════════════════════════════════════════════════════════════════════════════
```

**Quy tắc đánh số:**

| Cột | Ý nghĩa | Định dạng |
|-----|---------|-----------|
| **STT** | Số thứ tự trong bảng (1, 2, 3...) | Integer |
| **ID** | Mã function duy nhất toàn cục | `F` + 3 digits (`F001`) |
| **Module** | Tên module C++ (GIỮ NGUYÊN) | String |
| **Class** | Tên class C++ (GIỮ NGUYÊN) | String |
| **Function** | Tên function C++ (GIỮ NGUYÊN) | String |
| **Signature** | Function signature với types C++ | String |
| **C++ File** | File path relative to source folder | Path |
| **Java Package** | Package name = C++ folder path (GIỮ NGUYÊN) | Package |
| **Wave** | Wave number (W0, W1, W2...) | String |
| **Leaf** | 🌿 nếu là leaf node | Marker |
| **Dependencies** | F-IDs của các function cần port trước | F001, F002... |

### 5.2 Grouped by Wave (kèm trong porting-plan.md)

Sau bảng full listing, thêm các bảng grouped theo wave:

```markdown
## 🔄 WAVE 0 — Foundation (14 functions — CÓ THỂ SONG SONG)

| STT | ID   | Module    | Class         | Function    | Leaf |
|-----|------|-----------|---------------|-------------|------|
| 1   | F001 | UtilsLib  | CStringUtil   | Trim        | 🌿   |
| 2   | F002 | UtilsLib  | CStringUtil   | Split       | 🌿   |
| 3   | F003 | UtilsLib  | CStringUtil   | Format      | 🌿   |
| ... | ...  | ...       | ...           | ...         | ...  |

## 🔄 WAVE 1 — Foundational Consumers (38 functions)

| STT | ID   | Module     | Class      | Function       | Depends On |
|-----|------|------------|------------|----------------|------------|
| 15  | F015 | DataLayer  | CDbConfig  | LoadDbConfig   | F003       |
| 16  | F016 | DataLayer  | CDbConfig  | ParseConnection| F003       |
| ... | ...  | ...        | ...        | ...            | ...        |
```

### 5.3 porting-plan.json — Phải có "conversion_list" flat

```json
{
  "plan_version": "1.0",
  "source_folder": "/path/to/cpp/src",
  "scope": "ModuleSample01",
  "summary": {
    "total_items": 215,
    "total_modules": 5,
    "total_classes": 23,
    "total_functions": 215,
    "waves": 4,
    "circular_dependencies": 1,
    "leaf_nodes": 47,
    "parallel_batches": 8
  },
  "conversion_list": [
    {
      "stt": 1,
      "id": "F001",
      "module": "UtilsLib",
      "class": "CStringUtil",
      "function": "Trim",
      "signature": "CString Trim(CString)",
      "cpp_file": "utils/CString.cpp",
      "java_package": "utils",
      "java_class": "CStringUtil.java",
      "wave": 0,
      "is_leaf": true,
      "dependencies": [],
      "compat_needed": ["CStringCompat"]
    },
    {
      "stt": 2,
      "id": "F002",
      "module": "UtilsLib",
      "class": "CStringUtil",
      "function": "Split",
      "signature": "CArray<CString> Split(CString, TCHAR)",
      "cpp_file": "utils/CString.cpp",
      "java_package": "utils",
      "java_class": "CStringUtil.java",
      "wave": 0,
      "is_leaf": true,
      "dependencies": [],
      "compat_needed": ["CStringCompat", "CArrayCompat"]
    }
  ],
  "waves": [
    {
      "wave": 0,
      "items": ["F001", "F002", "F003", ...],
      "can_parallel": true
    }
  ],
  "leaf_nodes": ["F001", "F002", "F003", ...],
  "circular_dependencies": [...]
}
```

### 5.4 Output Files (Updated)

```
porting-output/
└── porting-plan/
    ├── porting-plan.md              # ✅ BẮT BUỘC: Full listing table (tất cả functions)
    │                                   + grouped by wave
    │                                   + leaf nodes list
    │                                   + circular deps
    ├── porting-plan.json            # machine-readable (có conversion_list)
    ├── leaf-nodes.md                # Danh sách leaf nodes cho parallel
    └── circular-deps.md             # Circular dependencies + resolution
```

---

## Phase 6: Circular Dependency Handling

### 6.1 Detection

```python
sccs = mcp_graph_mcp_compute_scc(
    db="neo4j",
    scope="all"
)
# Filter non-trivial SCCs (size > 1 = circular)
circular = [scc for scc in sccs if len(scc.members) > 1]
```

### 6.2 Resolution Strategies

| Pattern | Strategy | Example |
|---------|----------|---------|
| A↔B (2 classes) | Extract interface | `IModBridge` → A & B implement |
| A→B→C→A (3+ classes) | Break weakest link | Refactor C→A thành callback |
| Module A↔Module B | Shared interface package | `common-api/` package |
| Self-referencing | Accept, document | Recursive call, port as-is |

### 6.3 Circular Deps in Plan

```markdown
## ⚠️ Circular Dependencies

### SCC-1: CModuleSampleHandler ↔ CModuleSampleDispatcher
- **CModuleSampleHandler::ProcessMessage** gọi **CModuleSampleDispatcher::Dispatch**
- **CModuleSampleDispatcher::Dispatch** gọi **CModuleSampleHandler::HandleResponse**
- **Resolution**: Extract interface `IMessageHandler`:
  - `CModuleSampleHandler` implements `IMessageHandler`
  - `CModuleSampleDispatcher` depends on `IMessageHandler` (not CModuleSampleHandler directly)
- **Porting order**: Interface → CModuleSampleDispatcher → CModuleSampleHandler
```

---

## Phase 7: Validate Plan Completeness

> **BẮT BUỘC:** Trước khi handoff, PHẢI xác nhận plan bao phủ 100% functions.

### 7.1 Coverage Check

```python
# So sánh: tổng functions từ MCP Graph vs tổng items trong conversion_list
total_in_source = len(all_functions)          # từ Phase 1.1
total_in_plan = len(conversion_list)           # từ Phase 5.3
missing = total_in_source - total_in_plan

if missing > 0:
    print(f"❌ WARNING: {missing} functions NOT in plan!")
    # Identify thiếu functions và add vào cuối plan với wave "UNSCHEDULED"
```

### 7.2 Numbering Validation

```python
# Xác nhận:
# - Mọi function đều có ID duy nhất (F001..F{total})
# - Không trùng ID, không gap
# - STT sequential từ 1 → total
# - Mọi dependency reference đều trỏ đến ID có tồn tại
```

### 7.3 Handoff

```markdown
✅ Plan validated: {total_items} items | {waves} waves | {leaf_nodes} leaf nodes
Handoff → hi.porting-file-structure: Phase 2 — File Structure Porting
```

### graph_mcp (`http://127.0.0.1:8788/mcp`)

| Tool | Purpose | Phase |
|------|---------|-------|
| `mcp_graph_mcp_activate_project` | Kích hoạt C++ project analysis | 0 |
| `mcp_graph_mcp_search_functions` | Scan toàn bộ functions trong scope | 1 |
| `mcp_graph_mcp_get_symbol` | Lấy metadata chi tiết (name, params, type) | 1, 2, 3 |
| `mcp_graph_mcp_impact` | Phân tích callees/callers của 1 node | 2, 3, 4 |
| `mcp_graph_mcp_query_subgraph` | Query subgraph quanh 1 node | 3 |
| `mcp_graph_mcp_plan_dependency_order` | **KEY** — Module-level dependency ordering | 1 |
| `mcp_graph_mcp_plan_file_dependency_order` | **KEY** — File/class-level dependency ordering | 2 |
| `mcp_graph_mcp_plan_function_dependency_order` | **KEY** — Function-level dependency ordering | 3 |
| `mcp_graph_mcp_compute_scc` | **KEY** — Phát hiện circular dependencies | 1, 6 |
| `mcp_graph_mcp_topological_sort` | Topological sort cho dependency graph | 1, 2, 3 |
| `mcp_graph_mcp_find_paths` | Tìm đường dẫn giữa 2 nodes (verify dependency) | 2, 3 |

### mind_mcp (`http://127.0.0.1:8789/mcp`)

| Tool | Purpose | Phase |
|------|---------|-------|
| `mcp_mind_mcp_search_knowledge` | Tìm design docs giải thích module relationships | 1, 6 |
| `mcp_mind_mcp_get_document` | Lấy architecture diagram, module dependency spec | 1 |
| `mcp_mind_mcp_query_context` | Query lý do thiết kế (vd: tại sao A↔B circular) | 6 |
| `mcp_mind_mcp_find_related` | Tìm modules liên quan trong cùng business domain | 1 |

---

## Batch Execution

```
START
  │
  ├─ Phase 0: Preflight (verify MCP + pre-porting data)
  │
  ├─ Phase 1: Module-Level Ordering
  │     ├─ Scan all modules
  │     ├─ plan_dependency_order → wave table
  │     ├─ compute_scc → circular deps
  │     └─ Output: Module Wave Table
  │
  ├─ Phase 2: Class-Level Ordering (for each module, in wave order)
  │     ├─ Get all classes in module
  │     ├─ plan_file_dependency_order → class order
  │     └─ Output: Class Order Table per module
  │
  ├─ Phase 3: Function-Level Ordering (for each class, in order)
  │     ├─ Get all methods in class
  │     ├─ plan_function_dependency_order → function order
  │     └─ Output: Function Order Table per class
  │
  ├─ Phase 4: Leaf Node Detection
  │     ├─ Build reverse call graph
  │     ├─ Identify nodes with 0 callers
  │     └─ Output: Leaf Node Table
  │
  ├─ Phase 5: Generate Execution Plan
  │     ├─ Merge all ordering data
  │     ├─ Assign global sequential IDs (F001..F{N})
  │     ├─ Build consolidated full listing table (TẤT CẢ functions)
  │     ├─ Group by wave
  │     └─ Output: porting-plan.md + porting-plan.json
  │
  ├─ Phase 6: Circular Dependency Handling
  │     ├─ Analyze each SCC
  │     ├─ Propose resolution strategy
  │     └─ Output: circular-deps.md
  │
  └─ Phase 7: Validate Plan Completeness
        ├─ Validate 100% coverage (all functions in plan)
        ├─ Validate numbering (no gap, no duplicate ID)
        ├─ Validate dependencies (all refs point to existing IDs)
        └─ Handoff → hi.porting-file-structure (Phase 2)
```

---

## Example: porting-plan.md Snippet

```markdown
# 🚀 Porting Execution Plan: ModuleSample01

> Generated: 2026-05-13 | Source: /path/to/cpp/src | Scope: ModuleSample01

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| Modules | 3 (UtilsLib, DataLayer, ModuleSample01) |
| Classes | 12 |
| Functions | 87 |
| Waves | 4 |
| Circular Deps | 1 |
| Leaf Nodes | 23 (26.4%) |
| **STT Range** | **F001 → F087** |

---

## 📋 FULL PORTING LIST (87 functions)

| STT | ID   | Module       | Class                     | Function          | Signature                     | C++ Path           | Java Pkg     | Wave | Leaf | Depends On  |
|-----|------|-------------|---------------------------|-------------------|-------------------------------|--------------------|--------------|------|------|-------------|
| 1   | F001 | UtilsLib    | CStringUtil               | Trim              | CString Trim(CString)         | utils/CString.cpp  | utils        | W0   | 🌿   | —           |
| 2   | F002 | UtilsLib    | CStringUtil               | Split             | CArray<CString> Split(...)    | utils/CString.cpp  | utils        | W0   | 🌿   | —           |
| 3   | F003 | UtilsLib    | CStringUtil               | Format            | CString Format(CString, ...)  | utils/CString.cpp  | utils        | W0   | 🌿   | —           |
| 4   | F004 | UtilsLib    | CFileUtil                 | FileExists        | BOOL FileExists(CString)      | utils/CFile.cpp    | utils        | W0   | 🌿   | —           |
| 5   | F005 | UtilsLib    | CFileUtil                 | ReadAllText       | CString ReadAllText(CString)  | utils/CFile.cpp    | utils        | W0   | 🌿   | F004        |
| ... | ...  | ...         | ...                       | ...               | ...                           | ...                | ...          | ...  | ...  | ...         |
| 23  | F023 | DataLayer   | CDbConfig                 | LoadDbConfig      | BOOL LoadDbConfig(CString)    | data/DbConfig.cpp  | data         | W1   |      | F003, F005  |
| 24  | F024 | DataLayer   | CDbConfig                 | ParseConnection   | BOOL ParseConnection(LPTSTR)  | data/DbConfig.cpp  | data         | W1   |      | F003        |
| ... | ...  | ...         | ...                       | ...               | ...                           | ...                | ...          | ...  | ...  | ...         |
| 85  | F085 | ModuleSample01 | CModuleSampleActivity   | DoWork            | BOOL DoWork(DWORD, LPTSTR)    | act/Activity.cpp   | act          | W3   |      | F023, F067  |
| 86  | F086 | ModuleSample01 | CModuleSampleActivity   | OnReceive         | void OnReceive(LPVOID, DWORD) | act/Activity.cpp   | act          | W3   |      | F085        |
| 87  | F087 | ModuleSample01 | CModuleSampleActivity   | Cleanup           | void Cleanup()                | act/Activity.cpp   | act          | W4   |      | F086        |

---

## 🔄 WAVE 0 — Foundation (No Dependencies — CAN PARALLEL)

| STT | ID   | Module    | Class         | Function    | Leaf |
|-----|------|-----------|---------------|-------------|------|
| 1   | F001 | UtilsLib  | CStringUtil   | Trim        | 🌿   |
| 2   | F002 | UtilsLib  | CStringUtil   | Split       | 🌿   |
| 3   | F003 | UtilsLib  | CStringUtil   | Format      | 🌿   |
| 4   | F004 | UtilsLib  | CFileUtil     | FileExists  | 🌿   |
| 5   | F005 | UtilsLib  | CFileUtil     | ReadAllText |      |
| ... | ...  | ...       | ...           | ...         | ...  |

## 🔄 WAVE 1 — Utility Consumers

| STT | ID   | Module     | Class      | Function        | Depends On |
|-----|------|------------|------------|-----------------|------------|
| 23  | F023 | DataLayer  | CDbConfig  | LoadDbConfig    | F003, F005 |
| 24  | F024 | DataLayer  | CDbConfig  | ParseConnection | F003       |

## 🔄 WAVE 2 — Business Logic

...

## 🔄 WAVE 3 — Top-Level (Circular)

...

---

## 🌿 LEAF NODES — Parallel Execution Candidates

| ID   | Module    | Class         | Function    | Wave |
|------|-----------|---------------|-------------|------|
| F001 | UtilsLib  | CStringUtil   | Trim        | W0   |
| F002 | UtilsLib  | CStringUtil   | Split       | W0   |
| F003 | UtilsLib  | CStringUtil   | Format      | W0   |
| F004 | UtilsLib  | CFileUtil     | FileExists  | W0   |
| ...  | ...       | ...           | ...         | ...  |

---

## ⚠️ CIRCULAR DEPENDENCIES

### SCC-1: CModuleSampleHandler ↔ CModuleSampleDispatcher
- **CModuleSampleHandler::ProcessMessage** → CModuleSampleDispatcher::Dispatch
- **CModuleSampleDispatcher::Dispatch** → CModuleSampleHandler::HandleResponse
- **Resolution:** Extract `IMessageHandler` interface
| ... | ... | ... | ... | ... | ... | ... |
| 4.1 | ModuleSample01 | CModuleSampleActivity | DoWork | 4 | | 2.3, 3.1 |
| 4.2 | ModuleSample01 | CModuleSampleActivity | OnReceive | 4 | | 4.1 |
| 4.3 | ModuleSample01 | CModuleSampleActivity | Cleanup | 4 | | 4.2 |

**Total: 87 functions | 4 waves | 23 leaf nodes (parallel) | 1 circular dep**
```

---

**Owner**: Hiep  
**Version**: 1.0 — 2026-05-13
