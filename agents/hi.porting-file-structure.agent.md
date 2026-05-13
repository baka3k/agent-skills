---
description: Port cấu trúc file từ C++ sang Java: extract skeleton từ MCP Graph, generate Java file với 1-1 mapping class/function/params, phân tích compat requirements.
handoffs:
  - label: Port Functions in This File
    agent: hi.porting-function
    prompt: |
      Port từng function trong file $CURRENT_FILE với logic chi tiết.
      Skeleton đã có, chỉ cần điền implementation.
      Source: $SOURCE_FOLDER. Target: Java.
      Dùng type-mappings.json và compat-layer-design.md từ pre-porting-data/.
  - label: Next File (Batch Processing)
    agent: hi.porting-file-structure
    prompt: |
      Tiếp tục port file structure cho file tiếp theo trong migration worklist.
      Worklist: $WORKLIST. Current index: $CURRENT_INDEX.
  - label: Back to Orchestrator
    agent: hi.porting-cpp-to-java
    prompt: |
      File structure porting hoàn tất cho tất cả files. Tiếp tục Phase 3 - Function Porting.
hooks:
  pre:
    - name: mcp-health-check
      description: Verify MCP Graph connectivity
      timeout: 15s
      required: true
    - name: load-type-mappings
      description: Load type-mappings.json from pre-porting-data/
      required: true
  post:
    - name: validate-skeleton
      description: Verify generated Java skeleton compiles
---

# C++ to Java File Structure Porting Agent

> **Version:** 2.0  
> **Date:** 2026-05-13  
> **Purpose:** Port cấu trúc file C++ → Java: extract skeleton, generate 1-1 mapped Java file.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## Tham Số

| Tham số | Mô tả | Ví dụ |
|---------|-------|-------|
| `--file` | C++ file cần port | `module1/SampleClassName.cpp` |
| `--source-folder` | Thư mục gốc C++ source | `/path/to/cpp/src` |
| `--output` | Thư mục output (mặc định: `porting-output/`) | `./output` |

---

## Quy Trình

### Step 1: Extract Skeleton từ MCP Graph

```python
# Đảm bảo project đã được activate
mcp_graph_mcp_activate_project(
    source_folder="$SOURCE_FOLDER",
    parser_type="cplus",
    database_name="neo4j"
)

# Tìm tất cả symbols trong file C++
symbols = mcp_graph_mcp_search_functions(
    db="neo4j",
    query="path:$CURRENT_FILE",
    limit=500,
    content_mode="full"
)

# Với mỗi symbol, lấy metadata chi tiết
for sym in symbols:
    detail = mcp_graph_mcp_get_symbol(
        db="neo4j",
        node_id=sym.id
    )
    # Extract: class name, function names, param names, types, parent class
```

### Step 2: Generate Java Skeleton (1-1 Mapping)

**CRITICAL RULES:**

1. **Package = C++ folder path**: `module1/sub/` → `package module1.sub;`
2. **File name = C++ file name**: `SampleClassName.cpp` → `SampleClassName.java`
3. **Class name = C++ class name**: `SampleClassName` → `SampleClassName` (GIỮ NGUYÊN)
4. **Method names = C++ method names**: `DoWork` → `DoWork` (GIỮ NGUYÊN)
5. **Param names = C++ param names**: `lpszParam` → `lpszParam` (GIỮ NGUYÊN)
6. **ONLY convert types**: `BOOL` → `boolean`, `LPTSTR` → `String`, `DWORD` → `int`, etc.

**Ví dụ skeleton output:**

```java
package module1;

import java.util.ArrayList;
import java.util.HashMap;
import compat.CStringCompat;
import compat.WinApiCompat;

/**
 * Ported from: module1/SampleClassName.cpp
 * Original class: SampleClassName
 */
public class SampleClassName {

    // Ported from: SampleClassName.h - member variables
    private String m_strName;       // CString → String (via CStringCompat)
    private int m_nValue;           // int → int
    private boolean m_bActive;      // BOOL → boolean

    // Ported from: SampleClassName::DoWork(DWORD dwParam, LPTSTR lpszData)
    public int DoWork(int dwParam, String lpszData) {
        // TODO: Port implementation from C++
        throw new UnsupportedOperationException("Not yet ported");
    }

    // Ported from: SampleClassName::OnReceive(LPVOID lpData, DWORD dwSize)
    public void OnReceive(Object lpData, int dwSize) {
        // TODO: Port implementation from C++
        throw new UnsupportedOperationException("Not yet ported");
    }
}
```

### Step 3: C++ Header → Java Handling

| C++ (.h) Content | Java Action |
|------------------|-------------|
| Class declaration | Merge vào `.java` file |
| `#include` | Convert thành `import` |
| `#define CONST` | `private static final` |
| `#define MACRO(x)` | `private static` method |
| `typedef` | Nếu cần, tạo wrapper class |
| `extern` var | `public static` field |
| Forward declaration | `import` (Java resolves automatically) |

### Step 4: Analyze Compat Requirements (→ `compat-requirements.md`)

Với mỗi file, phân tích và ghi nhận:

```markdown
# Compat Requirements: SampleClassName.java

## Compat Classes Needed
| C++ Type | Compat Class | Status |
|----------|-------------|--------|
| CString | CStringCompat | Required |
| CArray<CModuleSampleData> | CArrayCompat | Required |
| SendMessage | WinApiCompat | Required |

## Manual Review Points
- [ ] Line 45: Pointer cast `(LPVOID)dwData` → Object with unsafe cast
- [ ] Line 78: Mailslot read → BlockingQueue conversion
```

### Step 5: Output Structure

```
porting-output/<module>/src/main/java/<package>/
├── SampleClassName.java          # Skeleton với method stubs
├── CModuleSampleData.java              # (nếu có trong worklist)
├── ...
└── compat-requirements/
    ├── SampleClassName-compat.md
    └── ...
```

### Step 6: Validate Skeleton

```bash
# Compile check skeleton
cd porting-output/<module>
javac -d target/classes src/main/java/**/*.java
```

---

## 1-1 Mapping Rules (CRITICAL - NHẮC LẠI)

1. **Package/Folder**: Giữ NGUYÊN 100% — `abc/abc/abc/` → `package abc.abc.abc;`
2. **File Name**: `File.cpp` → `File.java` (GIỮ NGUYÊN tên)
3. **Class Name**: `CClassName` → `CClassName` (GIỮ NGUYÊN, kể cả prefix C)
4. **Method Name**: `DoWork` → `DoWork` (GIỮ NGUYÊN)
5. **Param Name**: `dwParam` → `dwParam` (GIỮ NGUYÊN Hungarian notation)
6. **Only Convert**: Type annotations + syntax

**Mục đích**: 1-1 mapping để dễ trace back, verify correctness, và compare diff.

---

## MCP Tools Reference

### graph_mcp (`http://127.0.0.1:8788/mcp`)

| Tool | Purpose |
|------|---------|
| `mcp_graph_mcp_activate_project` | Khởi tạo phân tích C++ source |
| `mcp_graph_mcp_search_functions` | Tìm tất cả symbols trong file |
| `mcp_graph_mcp_get_symbol` | Lấy metadata (names, types, params) |
| `mcp_graph_mcp_impact` | Phân tích dependencies |
| `mcp_graph_mcp_get_ipc_message` | Phân tích IPC link |

### mind_mcp (`http://127.0.0.1:8789/mcp`)

| Tool | Purpose |
|------|---------|
| `mcp_mind_mcp_search_knowledge` | Tìm design docs, class diagrams của file C++ |
| `mcp_mind_mcp_get_document` | Lấy spec/design doc để hiểu cấu trúc class |
| `mcp_mind_mcp_find_related` | Tìm file/class liên quan để hiểu dependency ngữ cảnh |

---

## Batch Processing Loop

Khi được gọi từ orchestrator với nhiều files:

```
for each file in $WORKLIST:
    1. Extract skeleton cho file hiện tại
    2. Generate Java skeleton file
    3. Analyze compat requirements
    4. Validate compile
    5. Nếu còn file: handoff → hi.porting-file-structure (file tiếp theo)
    6. Nếu hết file: handoff → hi.porting-cpp-to-java (orchestrator)
```
