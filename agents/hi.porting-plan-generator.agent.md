---
description: Tạo porting execution plan hoàn chỉnh từ MCP Graph call graph sau pre-porting. Phân tích dependency → topological sort → module/class/function ordering → wave-based plan. Output 2 định dạng: porting-plan.md (có giải thích) + porting-plan.json (machine-readable).
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

> Kế hoạch porting KHÔNG được đề xuất đổi tên/refactor. Mọi function/class/file/module name trong plan phải GIỮ NGUYÊN từ C++ source.

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

### 5.1 Plan Structure

```markdown
# Porting Execution Plan: <Module>

## 📊 Summary
- Total modules: N
- Total classes: M
- Total functions: K
- Waves: W
- Circular dependencies: C
- Leaf nodes (parallel): L

## 🔄 Wave 0: Foundation (No Dependencies)
### Module: UtilsLib (Leaf Module)
#### Class: CStringUtil (Leaf Class)
| # | Function | Leaf | Notes |
|---|----------|------|-------|
| 0.1 | Trim | 🌿 | String utility |
| 0.2 | Split | 🌿 | String utility |
| 0.3 | Format | 🌿 | String utility → needs CStringCompat |

## 🔄 Wave 1: Utils Consumers
### Module: DataLayer
#### Class: CDbConfig
| # | Function | Dependencies | Notes |
|---|----------|-------------|-------|
| 1.1 | LoadDbConfig | UtilsLib.CStringUtil.Format | Cần compat CString |

## 🔄 Wave 2: Business Logic
...

## 🔄 Wave N: Circular Dependencies (Special Handling)
| SCC | Modules | Resolution |
|-----|---------|------------|
| SCC-1 | ModA ↔ ModB | Extract interface IModBridge |
```

### 5.2 Output Files

```
porting-output/
└── porting-plan/
    ├── porting-plan.md          # Full plan với giải thích
    ├── porting-plan.json        # Machine-readable structured plan
    ├── leaf-nodes.md            # Danh sách leaf nodes cho parallel
    ├── circular-deps.md         # Circular dependencies + resolution
    └── dependency-graph.dot     # (optional) GraphViz visualization
```

### 5.3 porting-plan.json Structure

```json
{
  "plan_version": "1.0",
  "generated_at": "2026-05-13T10:00:00Z",
  "source_folder": "/path/to/cpp/src",
  "scope": "ModuleSample01",
  "summary": {
    "total_modules": 5,
    "total_classes": 23,
    "total_functions": 215,
    "waves": 4,
    "circular_dependencies": 1,
    "leaf_nodes": 47,
    "parallel_batches": 8
  },
  "waves": [
    {
      "wave": 0,
      "label": "Foundation - No Dependencies",
      "can_parallel": true,
      "modules": [
        {
          "module": "UtilsLib",
          "is_leaf": true,
          "classes": [
            {
              "class": "CStringUtil",
              "is_leaf": true,
              "functions": [
                {"order": "0.1", "name": "Trim", "signature": "CString Trim(CString)", "leaf": true, "dependencies": [], "compat_needed": ["CStringCompat"]},
                {"order": "0.2", "name": "Split", "signature": "CArray<CString> Split(CString, TCHAR)", "leaf": true, "dependencies": [], "compat_needed": ["CStringCompat", "CArrayCompat"]}
              ]
            }
          ]
        }
      ]
    }
  ],
  "leaf_nodes": [
    {"module": "UtilsLib", "class": "CStringUtil", "function": "Trim", "wave": 0},
    {"module": "UtilsLib", "class": "CStringUtil", "function": "Split", "wave": 0}
  ],
  "circular_dependencies": [
    {
      "scc_id": 1,
      "modules": ["ModA", "ModB"],
      "resolution": "Extract interface IModBridge, implement in both"
    }
  ],
  "execution_order": [
    {"batch": 1, "parallel": true, "items": ["0.1", "0.2", "0.3", ...]},
    {"batch": 2, "parallel": false, "items": ["1.1", "1.2"], "depends_on": [1]}
  ]
}
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

## Phase 7: Generate Output Files

### 7.1 porting-plan.md (Human-Readable)

Định dạng Markdown với:
- ✅ Số thứ tự rõ ràng (0.1, 0.2, 1.1, 1.2, ...)
- ✅ Giải thích **lý do** cho mỗi ordering decision
- ✅ Leaf node markers (🌿)
- ✅ Compat layer requirements
- ✅ Circular dependency warnings
- ✅ Wave summary

### 7.2 porting-plan.json (Machine-Readable)

Định dạng JSON với:
- ✅ Structured waves → modules → classes → functions
- ✅ Dependency graph edges
- ✅ Leaf node list cho parallel execution
- ✅ Circular deps với resolution
- ✅ Compat requirements per function

---

## 🔧 MCP Tools Reference

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
  │     ├─ Assign sequential numbers
  │     ├─ Group parallel batches
  │     └─ Output: porting-plan.md + porting-plan.json
  │
  ├─ Phase 6: Circular Dependency Handling
  │     ├─ Analyze each SCC
  │     ├─ Propose resolution strategy
  │     └─ Output: circular-deps.md
  │
  └─ Phase 7: Finalize & Handoff
        ├─ Validate plan completeness
        ├─ Handoff → hi.porting-file-structure (Phase 1)
        └─ Handoff → hi.porting-cpp-to-java (Orchestrator)
```

---

## Example: porting-plan.md Snippet

```markdown
# 🚀 Porting Execution Plan: ModuleSample01

> Generated: 2026-05-13 | Source: /path/to/cpp/src | MCP: graph_mcp + mind_mcp

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| Modules | 3 (UtilsLib, DataLayer, ModuleSample01) |
| Classes | 12 |
| Functions | 87 |
| Waves | 4 |
| Circular Deps | 1 (CModuleSampleHandler ↔ CModuleSampleDispatcher) |
| Leaf Nodes | 23 (26.4%) — can be ported in parallel |

---

## 🔄 WAVE 0 — Foundation (No Dependencies) — CAN PARALLEL

> Các module/class/function không phụ thuộc vào bất kỳ thành phần nào khác.
> **Có thể port song song tất cả items trong wave này.**

### Module: UtilsLib (🌿 Leaf Module)

**Lý do:** Module utility thuần, không import bất kỳ module nào khác trong dự án.

#### Class: CStringUtil (🌿 Leaf Class)

| # | Function | Signature | 🌿 | Compat | Lý do ưu tiên |
|---|----------|-----------|-----|--------|---------------|
| **0.1** | `Trim` | `CString Trim(CString)` | 🌿 | CStringCompat | Không gọi hàm nào khác → làm đầu tiên |
| **0.2** | `Split` | `CArray<CString> Split(CString, TCHAR)` | 🌿 | CStringCompat, CArrayCompat | Độc lập với Trim |
| **0.3** | `Format` | `CString Format(CString, ...)` | 🌿 | CStringCompat | Độc lập |

#### Class: CFileUtil (🌿 Leaf Class)

| # | Function | Signature | 🌿 | Compat | Lý do |
|---|----------|-----------|-----|--------|------|
| **0.4** | `FileExists` | `BOOL FileExists(CString)` | 🌿 | CStringCompat, CFileCompat | Độc lập |
| **0.5** | `ReadAllText` | `CString ReadAllText(CString)` | 🌿 | CStringCompat, CFileCompat | Độc lập, gọi FileExists nội bộ |

---

## 🔄 WAVE 1 — Utility Consumers

> Các class/function phụ thuộc vào Wave 0.

### Module: DataLayer

**Lý do:** DataLayer cần CStringUtil.Format (Wave 0) và CFileUtil.ReadAllText (Wave 0).

#### Class: CDbConfig

| # | Function | Dependencies | Compat | Lý do thứ tự |
|---|----------|-------------|--------|-------------|
| **1.1** | `LoadDbConfig` | 0.3 (Format), 0.5 (ReadAllText) | CStringCompat, CFileCompat | Cần đọc config file → parse string |

---

## 🌿 LEAF NODES — Parallel Execution Candidates

Các function này có thể được port **đồng thời** (không phụ thuộc lẫn nhau):

| Batch | Functions | Module | Class |
|-------|-----------|--------|-------|
| P0 | 0.1, 0.2, 0.3 | UtilsLib | CStringUtil |
| P0 | 0.4, 0.5 | UtilsLib | CFileUtil |
| P1 | 1.3, 1.4 | DataLayer | CDbHelper |
| P2 | 2.7, 2.8, 2.9 | ModuleSample01 | CModuleSampleData |

---

## ⚠️ CIRCULAR DEPENDENCIES

### SCC-1: CModuleSampleHandler ↔ CModuleSampleDispatcher

- **CModuleSampleHandler::ProcessMessage** → CModuleSampleDispatcher::Dispatch
- **CModuleSampleDispatcher::Dispatch** → CModuleSampleHandler::HandleResponse
- **Resolution:** Extract `IMessageHandler` interface
  ```
  IMessageHandler (port first)
    ├── CModuleSampleDispatcher (port second, depends on IMessageHandler)
    └── CModuleSampleHandler (port third, implements IMessageHandler)
  ```

---

## 📋 FULL EXECUTION ORDER

| # | Module | Class | Function | Wave | Leaf | Depends On |
|---|--------|-------|----------|------|------|-----------|
| 0.1 | UtilsLib | CStringUtil | Trim | 0 | 🌿 | — |
| 0.2 | UtilsLib | CStringUtil | Split | 0 | 🌿 | — |
| 0.3 | UtilsLib | CStringUtil | Format | 0 | 🌿 | — |
| 0.4 | UtilsLib | CFileUtil | FileExists | 0 | 🌿 | — |
| 0.5 | UtilsLib | CFileUtil | ReadAllText | 0 | 🌿 | 0.4 |
| 1.1 | DataLayer | CDbConfig | LoadDbConfig | 1 | | 0.3, 0.5 |
| 1.2 | DataLayer | CDbConfig | ParseConnection | 1 | | 0.3 |
| ... | ... | ... | ... | ... | ... | ... |
| 4.1 | ModuleSample01 | CModuleSampleActivity | DoWork | 4 | | 2.3, 3.1 |
| 4.2 | ModuleSample01 | CModuleSampleActivity | OnReceive | 4 | | 4.1 |
| 4.3 | ModuleSample01 | CModuleSampleActivity | Cleanup | 4 | | 4.2 |

**Total: 87 functions | 4 waves | 23 leaf nodes (parallel) | 1 circular dep**
```

---

**Owner**: baka3k  
**Version**: 1.0 — 2026-05-13
