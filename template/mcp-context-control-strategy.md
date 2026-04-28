# MCP Context Control Strategy for Large Codebases

## Mục tiêu

Phân tích source code theo project_id mà KHÔNG tràn context window.

## Quy tắc bắt buộc

1. **Không dump raw JSON lớn**
   - Chỉ in summary, không in toàn bộ JSON response
   - Nếu cần raw data: lưu vào file, chỉ in summary

2. **Mỗi lần gọi chỉ lấy dữ liệu tối thiểu**
   - Ưu tiên query metadata nhẹ (name/signature/path) trước
   - Chỉ mở rộng chi tiết cho nhóm node thật sự cần điều tra

3. **Ưu tiên node_id thay vì tên hàm**
   - Truy vết bằng node_id để tránh context bloat
   - Chỉ in tên khi cần thiết cho readability

4. **Tự động chia batch nếu > 50 items**
   - Batch size mặc định: 20-50 items
   - Tóm tắt mỗi batch, không in toàn bộ
   - Hỏi user xác nhận trước khi mở rộng

## Quy trình chuẩn

### 1) Khoanh vùng theo module

```python
# TÌCH: Chạy từng module, không chạy toàn project
for module in ["DAILY_MENU", "DLY_JOKYO", "MS_SYSTEM_MENU"]:
    list_up_entrypoint(modules=module)
```

**Output mỗi module:**
```markdown
## Module: DAILY_MENU
- Entry points: 5 found
- Top functions: node_001 (MainMenu), node_002 (ProcessOrder)
```

### 2) Lấy danh sách hàm nhẹ

```python
# TÌCH: Chỉ lấy tên, không lấy body
search_functions(
    query="process*",
    limit=50             # Max 50 kết quả
)
```

**Output:**
```markdown
## Top 20 functions matching "process*"
1. node_101: ProcessOrder
2. node_102: ProcessPayment
...
[Total: 50, showing top 20]
```

### 3) Mở rộng có kiểm soát

```python
# TÌCH: Batch theo 10-20 node
for batch in chunks(node_ids, size=20):
    get_node_details(
        node_ids=batch
    )
    # Tóm tắt batch, hỏi user trước khi tiếp tục
```

**Output mỗi batch:**
```markdown
## Batch 1/3 (20 nodes)
- High complexity: node_101 (cyclomatic=15), node_105 (cyclomatic=12)
- High coupling: node_103 (calls 15 others)
- Need detail? [node_101, node_105]
```

### 4) Quan hệ hàm có chọn lọc

```python
# TÌCH: Chỉ trace khi cần
query_subgraph(
    function_id="node_101",
    limit=30              # Giới hạn số node trả về
)

# CHỈ dùng find_paths cho 1 c_pair hàm/lần
find_paths(
    start_function_id="node_101",
    end_function_id="node_205",
    limit=3                # Giới hạn số paths
)
```

**Output:**
```markdown
## Call graph for node_101 (ProcessOrder)
- Direct callers: [node_001, node_050]
- Direct callees: [node_201, node_202, node_203]
- Critical path to DB: node_101 → node_201 → DB_CONNECTION
```

## Đầu ra mỗi vòng lặp

```markdown
## Summary (vòng X/Y)
- Entry points discovered: N
- Key functions: top 10 danh sách
- Next recommendations: 3-5 bước tiếp theo
- User confirmation needed: [yes/no] để mở rộng
```

## Ví dụ workflow hoàn chỉnh

```markdown
## Phase 1: Khoanh vùng
✓ Module DAILY_MENU: 5 entry points found
✓ Module DLY_JOKYO: 3 entry points found
→ Next: Analyze DAILY_MENU entry points? [Y/n]

## Phase 2: Deep dive DAILY_MENU (batch 1/2)
✓ Processed 20 nodes
  - High risk: node_101 (OrderProcess), node_105 (PaymentProcess)
  - Need detail: node_101 for error handling
→ Next: Expand node_101 or continue batch 2? [1/2]

## Phase 3: Expand node_101
✓ Subgraph (limit 30): 15 nodes
  - Main flow: node_101 → node_201 → node_301
  - Error flow: node_101 → node_401 → node_402
→ Next: Trace error flow? [Y/n]
```

## Meta-rules cho AI Agent

1. **Luôn hỏi user trước deep dive**
   - Batch processing: confirm mỗi batch
   - Deep expansion: confirm trước khi tăng `limit` hoặc mở rộng thêm module
   - Large result: confirm trước khi in > 20 items

2. **Luôn tóm tắt, không dump**
   - 50 items → in top 10 + summary stats
   - Call graph → in topology summary, không full list
   - Code body → in summary, không full source

3. **Luôn track state**
   - Batch number: "Processing batch 3/5"
   - Progress: "Analyzed 150/500 functions"
   - Context usage: estimate before each query

4. **Luôn ưu tiên node_id**
   - Trace bằng node_id: `node_101 → node_201 → DB_NODE`
   - Chỉ in tên khi cần cho readability
   - Link back bằng node_id cho expand sau

## Fallback rules

Nếu vẫn tràn context:
1. Reduce batch size: 20 → 10 → 5
2. Reduce query limit: 50 → 30 → 10
3. Reduce parallel queries: 5 → 3 → 1
4. Switch to filesystem scan with selective MCP queries
