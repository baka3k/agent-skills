---
description: Discover and document use cases from source code using Graph MCP across 4 phases: initial discovery, semantic keyword search, trace/validate, and UC consolidation.
variables:
  input:
    - name: $REPO_ROOT
      source: CLI --repo-root
      required: true
    - name: $MODULE_NAME
      source: CLI --module
      required: true
    - name: $OUTPUT_DIR
      source: CLI --output (default: usecase/)
      required: false
    - name: $PARSER_TYPE
      source: CLI --parser (default: cplus)
      required: false
    - name: $SEARCH_DEPTH
      source: CLI --depth (default: 6)
      required: false
    - name: $DB_NAME
      source: CLI --db (default: neo4j)
      required: false
    - name: $FUNC_LIMIT
      source: CLI --func-limit (default: 500)
      required: false
  preflight:
    - name: uc-docs
      source: output file (write)
      required: true
    - name: phase1-results
      source: output file (write)
      required: true
    - name: phase2-results
      source: output file (write)
      required: true
    - name: phase3-diagrams
      source: output file (write)
      required: true
handoffs:
  - label: Run Repo Recon (for module context)
    agent: hi.repo-recon
    prompt: |
      Chạy repo-recon để có module inventory và entry-point map cho module.
      Repo: $REPO_ROOT. Scope: $MODULE_NAME. Depth: deep.
  - label: Generate Reverse Documentation
    agent: hi.reverse-doc-reconstruction
    prompt: |
      Từ use case đã phát hiện, tái tạo tài liệu kỹ thuật đầy đủ.
      Repo: $REPO_ROOT. Module: $MODULE_NAME. Input: $OUTPUT_DIR.
hooks:
  pre:
    - name: mcp-health-check
      description: Verify MCP Graph connectivity
      timeout: 15s
      required: true
    - name: input-validation
      description: Validate repo path, module name, depth parameters
      scope: ["repo_root", "module_name", "parser_type"]
      enable_redaction: true
  post:
    - name: validate-outputs
      description: Verify UC documentation artifacts were generated
      required_files:
        - usecase/phase1_functions.json
        - usecase/phase2_keywords.md
        - usecase/phase3_diagrams/
      optional_files:
        - usecase/uc_list.md
---

# Use Case Discovery Agent

> **Version:** 2.0  
> **Date:** 2026-05-19  
> **Purpose:** Khám phá và tạo tài liệu use case từ source code bằng Graph MCP — semantic search, function list, call tracing, và diagram generation.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## 🎯 Core Strategy

```
Graph MCP: Module-level breadth (functions, paths, IPC)
Graph MCP: Symbol-level depth (code bodies, callers, details)
+ semantic_search: Natural language fallback for hidden concepts

Workflow: explore_graph/semantic_search → search_functions → trace_flow → UC docs
```

### Content Mode Best Practices

| Mode | Khi nào dùng | Lợi ích |
|------|-------------|---------|
| `name` | Breadth queries (search, paths, subgraph) | Giảm 80-90% payload |
| `summary` | Filter/classify functions | Cân bằng thông tin & hiệu suất |
| `code` | Detail analysis — CHỈ cho nodes quan trọng | Full source khi cần |

---

## Pipeline: 4 Phases

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4
Graph MCP     Graph MCP    Graph MCP    UC Docs
(breadth)   (keywords)   (trace)     (output)
  │             │            │
  │        semantic_search   │
  │        (fallback)        │
  └──────────────────────────┘
```

---

## 🅿️ Phase 1: Initial Discovery (Graph MCP)

**Goal:** Get breadth-first view of module's functions, classes, and inter-module relationships.

### P1.1 — Activate Project & Database

```python
mcp_graph_mcp_activate_project(
    source_folder="$REPO_ROOT",
    parser_type="$PARSER_TYPE",
    database_name="$DB_NAME"
)
```

### P1.2 — Search All Functions in Module

```python
result = mcp_graph_mcp_search_functions(
    db="$DB_NAME",
    query="$MODULE_NAME",
    limit=$FUNC_LIMIT,
    content_mode="summary",
    include_raw_fields=False
)
```

**Extract:** function_id, name, file_path, class_name

**Decision — Classify by name pattern:**

| Pattern | Role |
|---------|------|
| `*EntryPoint`, `StartWork`, `DoWork`, `Main`, `Init` | Entry points |
| `Evt*`, `On*`, `Handle*`, `Receive*` | Handlers |
| `Start*`, `End*`, `Cleanup*` | Lifecycle |

**Output:** `usecase/<module>/phase1_functions.json`

### P1.3 — Check Inter-Module Dependencies

```python
paths = mcp_graph_mcp_find_path_between_module(
    source_modules=["$MODULE_NAME"],
    target_modules=["<related_module>"],
    max_depth=$SEARCH_DEPTH,
    content_mode="name",
    include_raw_fields=False
)
```

### P1.4 — Check IPC Messages

```python
ipc_msgs = mcp_graph_mcp_get_ipc_message(
    senders=["$MODULE_NAME"],
    receivers=["<related_module>"]
)
```

**Extract:** message_id, category, sender, receiver → dùng cho UC actor mapping

**Output:** `usecase/<module>/phase1_dependencies.json`

---

## 🅿️ Phase 2: Keyword Discovery (Graph MCP + semantic_search)

**Goal:** Tìm hidden UCs bị ẩn sau domain jargon qua multi-pass search bằng Graph MCP và semantic_search.

### P2.1 — Build Keyword Taxonomy

Cho mỗi module, xây dựng keyword list covering:

| # | Loại | Ví dụ (generic) |
|---|------|-----------------|
| 1 | Module name variants | `$MODULE_NAME`, `$MODULE_NAME_lower`, `$MODULE_NAME01` |
| 2 | English domain terms | `Payment`, `Refund`, `Cancel`, `Approve`, `Calculate`, `Validate` |
| 3 | Japanese romaji | `Shiharai` (payment), `Haraimodoshi` (refund), `Torikeshi` (cancel) |
| 4 | Japanese kanji | `支払` (payment), `払戻` (refund), `取消` (cancel) |
| 5 | Struct/field names | `PaymentData`, `RefundRequest`, `TransactionID`, `approvalStatus` |
| 6 | UI/Comm IDs | `CID_PaymentSample_*`, `COMM_Refund_Sample*`, `MSG_Approve_Sample*` |

**Output:** `usecase/<module>/keywords.txt`

### P2.2 — Multi-Pass Semantic Search

Strategy: **`explore_graph` (primary)** + **`semantic_search` (fallback)**

```python
# Pass 1: Module name (done in Phase 1)

# Pass 2: English domain terms — tìm function/class liên quan
result = mcp_graph_mcp_explore_graph(
    query="Find payment, refund, cancel, approve related functions in $MODULE_NAME",
    mode="hybrid",
    top_k=50
)

# Pass 3: Japanese terms — tìm function/class dùng tên JP
result = mcp_graph_mcp_explore_graph(
    query="Shiharai payment Haraimodoshi refund Torikeshi cancel functions in $MODULE_NAME",
    mode="hybrid",
    top_k=50
)

# Pass 4: Struct/ID names — search exact function names
result = mcp_graph_mcp_search_functions(
    db="$DB_NAME",
    query="PaymentData RefundRequest TransactionID approvalStatus",
    limit=50,
    content_mode="summary",
    include_raw_fields=False
)

# Pass 5 (fallback): Nếu explore_graph không đủ kết quả, dùng semantic_search
# semantic_search tìm qua workspace codebase dạng natural language
search_fallback = semantic_search(
    query="$MODULE_NAME module betting payment refund logic"
)
```

**Decision:** Union all hits → new symbol candidates not found in Phase 1

**Output:** `usecase/<module>/phase2_keyword_hits.txt`

### P2.3 — Fetch Symbol Details for Top Candidates

Dùng `search_functions(content_mode="code")` + `get_node_details()` thay cho `find_symbol`:

```python
# Tìm function và lấy code body
graph_result = mcp_graph_mcp_search_functions(
    db="neo4j",
    query="<SymbolName>",
    limit=5,
    content_mode="code",
    include_raw_fields=True
)

# Lấy metadata chi tiết
node_detail = mcp_graph_mcp_get_node_details(
    function_id="<id_from_above>",
    include_body=True
)
```

**Extract:** body, parameters, return_type, file_path, class_name

### P2.4 — Find References

Dùng `find_function_call_paths()` + `trace_flow()` thay cho `find_referencing_symbols`:

```python
# Cách 1: Tìm ai gọi function này
paths = mcp_graph_mcp_find_function_call_paths(
    start_function_id="<caller>",
    end_function_id="<target>",
    max_depth=$SEARCH_DEPTH
)

# Cách 2: Trace flow từ entry point
flow = mcp_graph_mcp_trace_flow(
    start_function_id="<entry_point>",
    max_depth=$SEARCH_DEPTH
)
```

**Extract:** caller function_ids, file:line, call chain

**Decision — Cluster symbols by:**

- Same entry point caller (control flow)
- Same struct/class usage (data flow)
- Same file/module (proximity)

**Output:** `usecase/<module>/phase2_symbols.json`

---

## 🅿️ Phase 3: Trace & Validate (Graph MCP)

**Goal:** Map keywords → Graph function IDs → trace call paths → validate → generate diagrams.

### P3.1 — Map Keywords → Graph Function IDs

Cho mỗi key symbol từ Phase 2:

```python
graph_result = mcp_graph_mcp_search_functions(
    db="$DB_NAME",
    query="<SymbolName>",
)
```

**Match:** by file_path + name → extract function_id

### P3.2 — Trace Call Paths

```python
path = mcp_graph_mcp_find_function_call_paths(
    db="neo4j",
    start_function_id=<entry_point_id>,
    end_function_id=<target_symbol_id>,
    max_depth=$SEARCH_DEPTH
)
```

**Extract:** intermediate function_ids (the call chain)

**Decision:**
- If path found → proceed to P3.3
- If no path → check IPC (P3.4)
- If still not found → `semantic_search(query="$MODULE_NAME connection between <entry> and <target>")` để tìm code kết nối

### P3.3 — Validate Path (Graph MCP)

Dùng `trace_flow` và `explore_graph`:

```python
# Cách 1: Trace flow từ entry point để verify call chain
flow = mcp_graph_mcp_trace_flow(
    start_function_id=<entry_id>,
    max_depth=$SEARCH_DEPTH
)
# Check: <target_function> có trong flow chain không?

# Cách 2: Dùng explore_graph để semantic search indirect calls
explore = mcp_graph_mcp_explore_graph(
    query="How does $MODULE_NAME function <X> call function <Y>",
    mode="hybrid"
)
```

**Check:** Nếu không xuất hiện trong flow → flag discrepancy hoặc indirect call

### P3.4 — Handle IPC/Indirect Calls

Nếu path bị đứt:

```python
# Step 1: Check IPC message
ipc = mcp_graph_mcp_get_ipc_message(
    senders=["$MODULE_NAME"],
    receivers=["<related_module>"]
)

# Step 2: Search IPC code bằng explore_graph
explore = mcp_graph_mcp_explore_graph(
    query="SendMessage ReceiveMessage CID communication in $MODULE_NAME",
    mode="hybrid"
)

# Step 3 (fallback): semantic_search tìm qua workspace
search = semantic_search(
    query="$MODULE_NAME SendMessage CID communication pattern"
)
```

**Extract:** IPC bridge points → add to flow

### P3.5 — Generate Sequence Diagram

```python
diagram = mcp_graph_mcp_generetate_diagram_by_code(
    db="neo4j",
    start_function_id=<entry_id>,
    end_function_id=<end_id>,
    max_depth=$SEARCH_DEPTH
)
```

**Output:** `usecase/<module>/seq_<uc_name>.mmd`

**Annotate:** Add ROLE/RISK/FLOW tags từ function bodies (search_functions content_mode="code"):
- **Performance:** `< e.g., < 500ms for step 3>`
- **Validation:** `< e.g., Check balance > bet amount>`

---

## 🅿️ Phase 4: UC Consolidation

**Goal:** Group flows into use cases và tạo UC markdown documents.

### P4.1 — Group Flows into Use Cases

**Cluster by:**

- Entry point (same entry → same UC family)
- Domain concept (same struct/data → same UC)
- Actor (Member/Operator/Host triggers)

**Decision:** Mỗi cluster = 1 UC candidate

### P4.2 — Create UC Markdown

Mỗi UC: `usecase/<module>/uc<XXX>_<name>.md`

Template:

```markdown
# Use Case: <Title>

## Meta

| Field    | Value                     |
|----------|---------------------------|
| UC ID    | uc_<module>_<XXX>         |
| Module   | $MODULE_NAME              |
| Priority | High/Medium/Low           |
| Risk     | HIGH/MEDIUM/LOW           |

## Actors

- **Primary:** <Actor> (via terminal UI)
- **Secondary:** <System1>, <System2>

## Main Flow

1. **[Entry]** <Actor> triggers <entry_point> — [file.cpp:line](file.cpp#Lline)
2. System validates X — <FunctionName> — [file.cpp:line](file.cpp#Lline)
3. System calls Y — [file.cpp:line](file.cpp#Lline)
4. System processes result — <FunctionName>
5. **[End]** Result

## Alternative Flows

- **A1:** <Description> — <FunctionName> — [file.cpp:line](file.cpp#Lline)

## Error Flows

- **E1:** <Error condition> — <FunctionName> — [file.cpp:line](file.cpp#Lline)

## Code References

| Symbol | File:Line | Role | Notes |
|--------|-----------|------|-------|
| `EntryPoint` | [file:line](file#Lline) | ENTRYPOINT | Main dispatcher |
| `FunctionX` | [file:line](file#Lline) | SERVICE | Validates |
| `StructY` | [file:line](file#Lline) | DATA | Data struct |

## Sequence Diagram

```mermaid
<paste from Phase 3.5>
```

## Metrics

- **Coverage:** Entry points traced: X/Y
- **Error paths:** Covered: X/Y
```

**Annotate HIGH-RISK:** Các step liên quan đến money, auth, host communication

**Output:** `usecase/<module>/uc*.md`

---

## Decision Tree for Hidden UCs

**Problem:** UC hidden behind domain jargon (e.g., `取消` = cancel, `支払` = payment)

**Solution:** Multi-pass keyword strategy (Phase 2):

```
1. Module name        → Phase 1 (search_functions)
2. English domain     → Phase 2 (explore_graph / semantic_search)
3. Japanese romaji    → Phase 2 (explore_graph)
4. Japanese kanji     → Phase 2 (explore_graph)
5. Struct/field names → Phase 2 (search_functions) + Phase 1
6. UI/Comm IDs        → Phase 2 (explore_graph) + IPC (get_ipc_message)

Decision: Union all passes → comprehensive coverage
```

---

## Checklist & Quality Gates

### Phase 1 Checklist

- [ ] Activated project/database
- [ ] Ran `search_functions` cho module name
- [ ] Identified entry points (≥3)
- [ ] Checked inter-module paths
- [ ] Checked IPC messages nếu không có direct paths
- [ ] Saved results to `usecase/<module>/phase1_*.json`

### Phase 2 Checklist

- [ ] Built keyword taxonomy (EN + JP + struct names + IDs)
- [ ] Ran `explore_graph` cho domain keywords (≥3 queries)
- [ ] Ran `semantic_search` fallback nếu explore_graph thiếu kết quả
- [ ] Ran `search_functions` cho struct/ID names
- [ ] Fetched symbol details với `search_functions(content_mode="code")`
- [ ] Fetched call paths với `find_function_call_paths` / `trace_flow`
- [ ] Saved results to `usecase/<module>/phase2_*.txt`

### Phase 3 Checklist

- [ ] Mapped keywords → Graph function IDs
- [ ] Traced ≥1 end-to-end path
- [ ] Validated path với `trace_flow` / `explore_graph`
- [ ] Handled IPC/indirect calls (`get_ipc_message` + `explore_graph`)
- [ ] Used `semantic_search` fallback nếu path bị đứt
- [ ] Generated sequence diagram
- [ ] Saved diagram to `usecase/<module>/seq_*.mmd`

### Phase 4 Checklist

- [ ] Grouped flows into UC candidates (≥3 UCs)
- [ ] Created UC markdown files (≥1)
- [ ] Added code references (≥5 per UC)
- [ ] Documented ≥1 alt flow và ≥1 error flow
- [ ] Tagged HIGH-RISK nodes
- [ ] Saved to `usecase/<module>/uc*.md`

### Coverage Gates

| Gate | Target |
|------|--------|
| UC_COVERAGE | ≥ 80% |
| ENTRY_COVERAGE | ≥ 90% |
| ERROR_PATH_COVERAGE | ≥ 70% |

---

## Quick Reference: Tool Commands

### Graph MCP

| Tool | Mục đích |
|------|----------|
| `mcp_graph_mcp_activate_project(...)` | Kích hoạt database parser |
| `mcp_graph_mcp_search_functions(db, query, limit, content_mode)` | Tìm functions |
| `mcp_graph_mcp_find_paths(db, start_id, end_id, max_depth)` | Trace call path |
| `mcp_graph_mcp_find_path_between_module(source, target, max_depth)` | Inter-module paths |
| `mcp_graph_mcp_get_ipc_message(senders, receivers)` | IPC links |
| `mcp_graph_mcp_generetate_diagram_by_code(db, start_id, end_id, max_depth)` | Sequence diagram (.mmd) |

---

### Additional Tools

| Tool | Mục đích |
|------|----------|
| `semantic_search(query)` | Natural language fallback — tìm code trong workspace khi explore_graph không đủ |
| `get_node_details(function_id)` | Lấy metadata chi tiết của node (params, file_path) |
| `find_function_call_paths(start, end, max_depth)` | Tìm call path giữa 2 functions |
| `trace_flow(start, max_depth)` | Trace execution flow từ một entry point |

## Output Structure

```
<output>/
└── <module>/
    ├── phase1_functions.json        # Graph MCP function list
    ├── phase1_dependencies.json     # Inter-module paths + IPC
    ├── keywords.txt                 # Keyword taxonomy
    ├── phase2_keyword_hits.txt      # Multi-pass explore_graph + semantic_search results
    ├── phase2_symbols.json          # Function details from search_functions
    ├── phase3_diagrams/             # Sequence diagrams (.mmd)
    ├── uc_list.md                   # All use cases summary
    ├── uc_001_<name>.md             # Use case documents
    └── uc_002_<name>.md
```

---

## Sensitive Data Handling

Mọi output đều được redact tự động:

- API keys, passwords, secrets, tokens → `[REDACTED_*]`
- Connection strings, IP addresses → `[REDACTED_*]`
- Email, phone numbers → `[REDACTED_*]`
