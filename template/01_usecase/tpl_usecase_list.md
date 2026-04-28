# Kết quả Khám phá Use Case — {Tên Module}

## Tóm tắt

- **Tổng số hàm đã phân tích**: `{N}` (từ Graph MCP / code search)
- **Số Entry Point chính**: `{N}` (liệt kê tên hàm)
- **Tổng số UC**: `{N}` (Primary: `{N}`, Secondary: `{N}`)
- **Chế độ khám phá**: `{Basic | Extended}`
- **IPC Messages**: `{N}` outgoing messages to `{Module1}`, `{Module2}`

---

## Danh sách UC

### UC001: {Tên UC} [PRIMARY | SECONDARY]

**Mục tiêu nghiệp vụ**: {Mô tả ngắn mục tiêu}
**Ưu tiên**: `{HIGH | MEDIUM | LOW}` ({Lý do})
**Mức độ rủi ro**: `{HIGH | MEDIUM | LOW}` ({Lý do})

**Actors**:

- {Actor chính} (primary): {Vai trò}
- {Actor phụ} (secondary): {Vai trò}

**Entry Points**:

- `{ClassName::FunctionName}` ({mô tả})

**Flows**:

- Main Flow: `{N}` bước ({Mô tả ngắn các bước chính})
- Alt Flows: `{N}` ({Liệt kê tên các alt flow})
- Error Flows: `{N}` ({Liệt kê tên các error flow})

**Dependencies**: {Phụ thuộc IPC, module, không có thì ghi: None}

**Related Classes**: `{Class1}`, `{Class2}`

**Overlap Analysis**:

- Với {UCxxx}: `{N}`% → {Separate | Merged into UCooo}

---

### UC002: {Tên UC} [PRIMARY | SECONDARY]

_(Tiếp tục theo cùng cấu trúc như UC001)_

---

## Phân tích Khoảng trống & Xác minh

**IPC Messages được bao phủ**: `{N}`/`{N}` (`{%}`)

- {Nhóm operation 1}: `{mã IPC}` → {UCxxx}
- {Nhóm operation 2}: `{mã IPC}` → {UCxxx}

**Bao phủ hàm**: ~`{%}` (`{N}` hàm phân tích, `{N}` UC xác định)

**Checkpoint xác minh**:

- [ ] Tất cả Entry Point chính đã được gán vào UC
- [ ] Không còn flow mồ côi (orphan flows)
- [ ] Số lượng UC hợp lý
- [ ] Tất cả UC có actors và flows
- [ ] Mức độ rủi ro đã được gán
- [ ] IPC messages đã được ánh xạ

**Ngày khám phá**: `{YYYY-MM-DD}`
**Phiên bản**: v`{X.X}`
