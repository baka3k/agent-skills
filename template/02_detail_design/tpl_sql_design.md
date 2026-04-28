# 【Mẫu】Tài liệu thiết kế SQL

> **Tên file**: 【Mẫu】SQL_Design_Template_SQLID_SQLName_v0.00.md
> **Ngày tạo**: `{YYYY-MM-DD}`

---

## 📋 Thông tin cơ bản

| Mục                              | Giá trị                               |
| -------------------------------- | ------------------------------------- |
| **SQL ID**                       | `{SQLID}`                             |
| **Tên SQL**                      | `{Tên SQL}`                           |
| **Phiên bản**                    | v0.00                                 |
| **Người tạo**                    | `{Tên người tạo}`                     |
| **Tài liệu thiết kế cơ bản gốc** | `{Tên file tài liệu thiết kế cơ bản}` |

---

## 📖 Tổng quan

`{Mô tả tổng quan về SQL này — tìm kiếm gì, từ bảng nào, theo điều kiện nào}`

---

## 📝 Ghi chú

`{Ghi chú đặc biệt, nếu không có thì ghi: (Không có)}`

---

## 1️⃣ Tham số SQL

### Vị trí sử dụng (mục đích)

| Tham số             | Mô tả                       |
| ------------------- | --------------------------- |
| WHERE (Điều kiện 1) | `{Tên tham số điều kiện 1}` |
| WHERE (Điều kiện 2) | `{Tên tham số điều kiện 2}` |
| WHERE (Điều kiện 3) | `{Tên tham số điều kiện 3}` |
| WHERE (Điều kiện 4) | `{Tên tham số điều kiện 4}` |
| WHERE (Điều kiện 5) | `{Tên tham số điều kiện 5}` |
| ORDER BY            | Chỉ định thứ tự sắp xếp     |
| LIMIT               | Giới hạn số bản ghi lấy ra  |
| OFFSET              | Vị trí bắt đầu lấy dữ liệu  |

---

## 2️⃣ SQL

```sql
-- Mô tả: {Mục đích của câu SQL}
SELECT
    {alias}.{column1},
    {alias}.{column2},
    {alias}.{column3}
FROM {TABLE_NAME} {alias}
    -- LEFT JOIN {TABLE2} {alias2} ON {alias}.{key} = {alias2}.{key}
WHERE
    -- {Điều kiện 1}
    -- {Điều kiện 2}
ORDER BY {alias}.{sortColumn} {ASC|DESC}
LIMIT :pageSize
OFFSET :offset;
```

---

## 3️⃣ Mệnh đề WHERE

```
-- Mô tả logic điều kiện WHERE
-- Ví dụ:
-- Nếu :param1 không null → AND column1 = :param1
-- Nếu :param2 không null → AND column2 LIKE :param2
-- Nếu :listParam không rỗng → AND column3 IN (:listParam)
```

---

## 4️⃣ Kết quả thực thi

### Danh sách phần tử (tên vật lý)

| No. | Tên phần tử (tên vật lý) | Mô tả           |
| --- | ------------------------ | --------------- |
| 1   | `{alias}.{column1}`      | `{Mô tả cột 1}` |
| 2   | `{alias}.{column2}`      | `{Mô tả cột 2}` |
| 3   | `{alias}.{column3}`      | `{Mô tả cột 3}` |
| 4   | `{alias}.{column4}`      | `{Mô tả cột 4}` |
| 5   | `{alias}.{column5}`      | `{Mô tả cột 5}` |

---

## 📊 Thông tin thống kê

| Field      | Non-empty     | Fill % |
| ---------- | ------------- | ------ |
| `{field1}` | `{X}/{Total}` | `{%}`  |
| `{field2}` | `{X}/{Total}` | `{%}`  |

---

## 🏷️ Metadata

- **Spec Type**: `{MESSAGE_FORMAT_SPEC \| QUERY_SPEC \| その他}`
- **Header Row**: `{N}`
- **Item Count**: `{N}`
- **Source File**: `{Tên file nguồn}`

---

## Tài liệu liên quan

- **Tài liệu thiết kế cơ bản**: `{Tài liệu tổng quan xử lý online_ID xử lý_Tên xử lý}`
- **Tài liệu thiết kế bảng**: `{Tài liệu thiết kế bảng_TABLE_Tên bảng}`
- **Tài liệu thiết kế màn hình**: `{Tài liệu thiết kế màn hình_ScreenID_Tên màn hình}`
- **Tài liệu thiết kế API**: `{Tài liệu thiết kế API_APIID_Tên API}`
