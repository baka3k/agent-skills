# Tài liệu Test Case — {Tên tính năng / Use Case}

## Thông tin cơ bản

| Mục                | Nội dung                     | Review | Approved | Executing | Done |
| ------------------ | ---------------------------- | ------ | -------- | --------- | ---- |
| **ID tài liệu**    | `TC-{ModuleID}-{NNN}`        |
| **Tính năng / UC** | `{Tên tính năng hoặc UCxxx}` |
| **Phiên bản**      | v0.00                        |
| **Ngày tạo**       | `{YYYY-MM-DD}`               |
| **Người tạo**      | `{Tên}`                      |
| **Trạng thái**     | `{Draft                      |        |          |           |      |

---

## 1. Phạm vi kiểm thử

- **In scope**: {Liệt kê chức năng được test}
- **Out of scope**: {Liệt kê chức năng không test}
- **Môi trường**: `{Dev | Staging | UAT | Production}`

---

## 2. Điều kiện tiên quyết chung

- {Điều kiện 1: ví dụ DB đã có seed data}
- {Điều kiện 2: ví dụ user test đã được tạo}
- {Điều kiện 3}

---

## 3. Danh sách Test Case

### TC-001: {Tên test case — Happy Path}

| Mục                      | Nội dung                                |
| ------------------------ | --------------------------------------- |
| **Test Case ID**         | `TC-{NNN}-001`                          |
| **Loại**                 | `{Unit / Integration / E2E / API / UI}` |
| **Ưu tiên**              | `{High / Medium / Low}`                 |
| **Điều kiện tiên quyết** | {Điều kiện đặc thù cho test case này}   |

**Bước thực hiện:**

| Step | Hành động     | Dữ liệu đầu vào | Kết quả mong đợi     |
| ---- | ------------- | --------------- | -------------------- |
| 1    | {Hành động 1} | `{input data}`  | {Kết quả mong đợi 1} |
| 2    | {Hành động 2} | `{input data}`  | {Kết quả mong đợi 2} |
| 3    | {Hành động 3} | `{input data}`  | {Kết quả mong đợi 3} |

**Kết quả thực tế:** {Điền khi thực hiện test}  
**Trạng thái:** `{Pass | Fail | Blocked | Skip}`  
**Ghi chú:** {Ghi chú thêm nếu có}

---

### TC-002: {Tên test case — Validation Error}

| Mục                      | Nội dung                                |
| ------------------------ | --------------------------------------- |
| **Test Case ID**         | `TC-{NNN}-002`                          |
| **Loại**                 | `{Unit / Integration / E2E / API / UI}` |
| **Ưu tiên**              | `{High / Medium / Low}`                 |
| **Điều kiện tiên quyết** | {Điều kiện}                             |

**Bước thực hiện:**

| Step | Hành động     | Dữ liệu đầu vào   | Kết quả mong đợi     |
| ---- | ------------- | ----------------- | -------------------- |
| 1    | {Hành động 1} | `{invalid input}` | {Thông báo lỗi: ...} |
| 2    | {Hành động 2} | `{input data}`    | {Kết quả mong đợi}   |

**Kết quả thực tế:** {Điền khi thực hiện test}  
**Trạng thái:** `{Pass | Fail | Blocked | Skip}`  
**Ghi chú:** {Ghi chú}

---

### TC-003: {Tên test case — Alt / Error Flow}

_(Tiếp tục theo cùng cấu trúc)_

---

## 4. Test Data

| Biến           | Giá trị           | Mô tả             |
| -------------- | ----------------- | ----------------- |
| `{varName1}`   | `{value}`         | {Mô tả}           |
| `{varName2}`   | `{value}`         | {Mô tả}           |
| `{invalidVar}` | `{invalid value}` | Dùng cho test lỗi |

---

## 5. Tóm tắt kết quả

| Tổng  | Pass  | Fail  | Blocked | Skip  |
| ----- | ----- | ----- | ------- | ----- |
| `{N}` | `{N}` | `{N}` | `{N}`   | `{N}` |

---

## Tài liệu liên quan

- **Use Case**: `uc{NNN}_{usecase_name}.md`
- **API Spec**: `API_Process_Design_{APIID}_{Name}_v{X.XX}.md`
- **Bug Report**: `bug_report_{ID}.md`
