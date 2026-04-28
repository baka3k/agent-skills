# Use Case Trace Metrics Dashboard — {Tên Module}

## Overview

- **Module**: `{ModuleID}` ({Tên module})
- **Lần cập nhật cuối**: `{YYYY-MM-DD}`
- **Tổng số UC xác định**: `{N}`
- **UC có Sequence Diagram**: `{N}` ({Liệt kê UCxxx})
- **UC có Class Diagram**: `{N}` ({Liệt kê UCxxx})
- **UC có file .mmd**: `{N}` ({Liệt kê UCxxx})

---

## Coverage Metrics

### UC Coverage — `{N}`/`{N}` = `{%}`

| UC    | Tên         | Trạng thái                 |
| ----- | ----------- | -------------------------- |
| UC001 | {Tên UC001} | ✅ Sequence + Class + .mmd |
| UC002 | {Tên UC002} | ✅ Sequence + .mmd         |
| UC003 | {Tên UC003} | ❌ Chưa trace              |
| UCxxx | {Tên UCxxx} | ❌ Chưa trace              |

### Entry Point Coverage — `{N}`/`{N}` = `{%}`

| Entry Point          | UC liên quan | Trạng thái    |
| -------------------- | ------------ | ------------- |
| `{Class::Function1}` | UC001, UC002 | ✅ Traced     |
| `{Class::Function2}` | UC003        | ❌ Not traced |

### High Risk Trace Coverage — `{N}`/`{N}` = `{%}`

| Chức năng rủi ro cao | UC    | Trạng thái    |
| -------------------- | ----- | ------------- |
| {Tên chức năng 1}    | UC001 | ✅ Traced     |
| {Tên chức năng 2}    | UC002 | ✅ Traced     |
| {Tên chức năng 3}    | UC007 | ❌ Not traced |

### Error Path Coverage — `{N}`/`{N}` = `{%}`

| Loại lỗi | UC    | Trạng thái    |
| -------- | ----- | ------------- |
| {Lỗi 1}  | UC001 | ✅ Traced     |
| {Lỗi 2}  | UC002 | ✅ Traced     |
| {Lỗi 3}  | UCxxx | ❌ Not traced |

---

## Module Relationships

- **Direct Calls**: `{Module}` ↔ `{Module2}`, `{Module}` ↔ `{Module3}`
- **IPC Messages**: {Mô tả kênh IPC chính}
- **Shared Memory**: {Mô tả vùng nhớ dùng chung nếu có}

---

## Annotations Applied

- **ROLE**: `ENTRYPOINT` ({Hàm}), `CONTROLLER` ({Hàm}), `SERVICE` ({Hàm})
- **FLOW**: `MAIN` ({flows chính}), `ALT` ({nhánh điều kiện}), `ERROR` ({đường lỗi})
- **RISK**: `HIGH` ({fund / auth / host comm}), `MEDIUM` ({card reading}), `LOW` ({UI updates})
- **STATE**: `MUTATES` ({cập nhật dữ liệu}), `PURE` ({validation}), `I/O` ({printer, cash})

---

## Timeline

| Ngày           | Sự kiện                |
| -------------- | ---------------------- |
| `{YYYY-MM-DD}` | Khởi tạo, tạo template |
| `{YYYY-MM-DD}` | {Mô tả sự kiện}        |
| `{YYYY-MM-DD}` | {Mô tả sự kiện}        |

---

## Next Priorities

1. **Tăng UC_COVERAGE**: Hoàn thành sequence diagram cho {UCxxx–UCyyy} (hiện tại `{N}`/`{N}` = `{%}`)
2. **Hoàn thiện ENTRY_COVERAGE**: Trace các entry point còn lại (hiện tại `{N}`/`{N}` = `{%}`)
3. **Tăng HIGH_RISK_TRACE**: Hoàn thành trace error handling và system lifecycle (hiện tại `{N}`/`{N}` = `{%}`)
4. **Thêm IPC Integration**: Ánh xạ tất cả `{N}` IPC messages vào UC flows
5. **Tạo Diagram**: Tạo sequence và class diagram cho tất cả `{N}` UC

---

## Quality Gates

- [ ] Template chuẩn hóa
- [ ] UC001 và UC002 đã được phân biệt rõ ràng
- [ ] File .mmd đã tạo
- [ ] Khám phá UC đầy đủ (`{N}` UC xác định)
- [ ] Entry points đã được ánh xạ (`{N}`/`{N}` traced)
- [ ] IPC messages đã phân tích (`{N}` messages)
- [ ] Tất cả UC có sequence diagram
- [ ] Tất cả entry points đã traced
- [ ] Tất cả đường rủi ro cao đã covered
- [ ] Tất cả error paths đã documented
