# 【Mẫu】Tài liệu thiết kế xử lý API

## Thông tin cơ bản

| Mục                              | Nội dung                              |
| -------------------------------- | ------------------------------------- |
| **API ID**                       | `{APIID}`                             |
| **Tên xử lý**                    | `{Tên API}`                           |
| **Phiên bản**                    | v0.00                                 |
| **Ngày tạo**                     | `{YYYY-MM-DD}`                        |
| **Người tạo**                    | `{Tên người tạo}`                     |
| **Tài liệu thiết kế cơ bản gốc** | `{Tên file tài liệu thiết kế cơ bản}` |

---

## 1. Tổng quan API

### Thông tin cơ bản API

| Mục                      | Nội dung                                          |
| ------------------------ | ------------------------------------------------- |
| **HTTP Method**          | `{GET \| POST \| PUT \| DELETE \| PATCH}`         |
| **Endpoint**             | `/api/v1/{resource}/{action}`                     |
| **Content-Type**         | application/json                                  |
| **Phương thức xác thực** | `{OAuth 2.0 \| API Key \| Bearer Token \| Không}` |
| **Định dạng response**   | JSON                                              |

---

## 2. Tham số Request

### Request Header

| Tên header    | Bắt buộc | Kiểu   | Mô tả            |
| ------------- | -------- | ------ | ---------------- |
| Content-Type  | Yes      | string | application/json |
| Authorization | Yes      | string | Bearer {token}   |
| X-API-Key     | No       | string | API Key          |

### Request Body

```json
{
  "{param1}": "string",
  "{param2}": "string",
  "pagination": {
    "page": 1,
    "pageSize": 25
  },
  "sort": {
    "field": "{sortField}",
    "order": "asc"
  }
}
```

### Định nghĩa tham số

| No. | Tên tham số   | Tên logic               | Kiểu       | Lặp lại | Bắt buộc    | Giá trị mặc định | Ví dụ định dạng      | Mô tả     |
| --- | ------------- | ----------------------- | ---------- | ------- | ----------- | ---------------- | -------------------- | --------- |
| 1   | `{param1}`    | `{Tên logic 1}`         | `{Kiểu}`   | No      | `{Yes\|No}` | -                | `{Ví dụ}`            | `{Mô tả}` |
| 2   | `{param2}`    | `{Tên logic 2}`         | `{Kiểu}`   | No      | `{Yes\|No}` | -                | `{Ví dụ}`            | `{Mô tả}` |
| 3   | `{listParam}` | `{Tên logic danh sách}` | [JSON]Mảng | 1..\*   | No          | []               | `["code1", "code2"]` | `{Mô tả}` |

---

## 3. Tham số Response

### Response Header

| Tên header   | Kiểu   | Mô tả               |
| ------------ | ------ | ------------------- |
| Content-Type | string | application/json    |
| X-Request-ID | string | ID theo dõi request |

### Response Body

#### Response thành công (200 OK)

```json
{
  "status": "success",
  "data": {
    "{resultList}": [
      {
        "{field1}": "{value1}",
        "{field2}": "{value2}"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "pageSize": 25,
      "totalRecords": 0,
      "totalPages": 0
    }
  },
  "metadata": {
    "requestId": "req-{requestId}",
    "timestamp": "{ISO8601}",
    "processingTime": "{ms}ms"
  }
}
```

#### Response lỗi (400/500)

```json
{
  "status": "error",
  "error": {
    "code": "{ERR_CODE}",
    "message": "{Thông báo lỗi}",
    "details": [
      {
        "field": "{fieldName}",
        "message": "{Thông báo lỗi theo field}"
      }
    ]
  },
  "metadata": {
    "requestId": "req-{requestId}",
    "timestamp": "{ISO8601}"
  }
}
```

---

## 4. Danh sách ràng buộc kiểu dữ liệu

### Ràng buộc kiểu dữ liệu

| Kiểu    | Loại ràng buộc | Mô tả                                                       |
| ------- | -------------- | ----------------------------------------------------------- |
| string  | pattern        | Kiểm tra bằng biểu thức chính quy                           |
| string  | enum           | Chỉ cho phép một trong các chuỗi được định nghĩa trong enum |
| integer | minimum        | Giá trị tối thiểu                                           |
| integer | maximum        | Giá trị tối đa                                              |
| integer | int32          | Số nguyên 32-bit                                            |
| integer | int64          | Số nguyên 64-bit                                            |
| number  | float          | Số thực dấu phẩy động                                       |
| number  | double         | Số thực dấu phẩy động độ chính xác kép                      |
| array   | minItems       | Số phần tử tối thiểu của mảng                               |
| array   | maxItems       | Số phần tử tối đa của mảng                                  |
| object  | required       | Định nghĩa thuộc tính bắt buộc                              |
| object  | properties     | Định nghĩa cấu trúc object                                  |

### Định nghĩa ràng buộc theo tham số

| Tên tham số   | Kiểu   | Ràng buộc                               | Thông báo lỗi     |
| ------------- | ------ | --------------------------------------- | ----------------- |
| `{param1}`    | string | `{pattern\|maxLength\|enum}: {Giá trị}` | `{Thông báo lỗi}` |
| `{param2}`    | string | `{pattern\|maxLength\|enum}: {Giá trị}` | `{Thông báo lỗi}` |
| `{listParam}` | array  | `minItems: 1`                           | `{Thông báo lỗi}` |

---

## 5. Luồng xử lý

### Sơ đồ luồng xử lý

```mermaid
flowchart TD
    START[Nhận API Request] --> AUTH{Kiểm tra xác thực/phân quyền}
    AUTH -->|NG| AUTH_ERR[401 Unauthorized]
    AUTH -->|OK| VALID{Validate đầu vào}
    VALID -->|NG| VALID_ERR[400 Bad Request]
    VALID -->|OK| PROC[{Xử lý chính}]
    PROC --> RESULT{Có kết quả?}
    RESULT -->|Có| FORMAT[Định dạng kết quả]
    RESULT -->|Không| EMPTY[Tạo kết quả rỗng]
    FORMAT --> RES_OK[200 OK Response]
    EMPTY --> RES_OK
    RES_OK --> END[Kết thúc xử lý]
    AUTH_ERR --> END
    VALID_ERR --> END
```

---

## 6. Liên kết dữ liệu

### Định nghĩa nguồn dữ liệu

| Mục                      | Nội dung                          |
| ------------------------ | --------------------------------- |
| **Loại định nghĩa file** | `{Loại tài liệu định nghĩa file}` |
| **Tên file logic**       | `{Tên file logic}`                |
| **Tên file vật lý**      | `{Tên file vật lý}`               |
| **Thư mục lưu trữ**      | `{Đường dẫn thư mục lưu trữ}`     |
| **Bộ ký tự**             | `{JIS X 0208 \| UTF-8 \| Khác}`   |
| **Encoding**             | `{UTF-8 \| Shift-JIS \| Khác}`    |

### Hỗ trợ định dạng

| Định dạng    | Hỗ trợ      | Ghi chú     |
| ------------ | ----------- | ----------- |
| XML          | `{○\|×\|△}` | `{Ghi chú}` |
| JSON         | `{○\|×\|△}` | `{Ghi chú}` |
| CSV          | `{○\|×\|△}` | `{Ghi chú}` |
| TSV          | `{○\|×\|△}` | `{Ghi chú}` |
| Excel        | `{○\|×\|△}` | `{Ghi chú}` |
| Fixed-length | `{○\|×\|△}` | `{Ghi chú}` |

### Hỗ trợ ký tự xuống dòng

| Ký tự xuống dòng | Hỗ trợ   |
| ---------------- | -------- |
| CR+LF            | `{○\|×}` |
| LF               | `{○\|×}` |
| CR               | `{○\|×}` |
| Không có         | `{○\|×}` |

---

## 7. Danh sách mã lỗi

| Mã lỗi     | HTTP Status     | Thông báo lỗi                   | Cách xử lý                              |
| ---------- | --------------- | ------------------------------- | --------------------------------------- |
| ERR001     | 400             | Điều kiện tìm kiếm không hợp lệ | Vui lòng kiểm tra tham số đầu vào       |
| ERR002     | 400             | Thiếu tham số bắt buộc          | Vui lòng nhập các trường bắt buộc       |
| ERR003     | 401             | Xác thực thất bại               | Vui lòng kiểm tra token xác thực        |
| ERR004     | 403             | Không có quyền truy cập         | Vui lòng kiểm tra cài đặt quyền         |
| ERR005     | 404             | Không tìm thấy resource         | Vui lòng kiểm tra URL                   |
| ERR006     | 500             | Lỗi nội bộ server               | Vui lòng liên hệ quản trị viên hệ thống |
| ERR007     | 503             | Dịch vụ không khả dụng          | Vui lòng thử lại sau                    |
| `{ERRXXX}` | `{HTTP Status}` | `{Thông báo lỗi đặc thù API}`   | `{Cách xử lý}`                          |

---

## 8. Bảo mật

### Xác thực / Phân quyền

| Mục                      | Nội dung                                 |
| ------------------------ | ---------------------------------------- |
| **Phương thức xác thực** | `{OAuth 2.0 \| API Key \| Bearer Token}` |
| **Phạm vi phân quyền**   | `{scope:action}`                         |
| **Thời hạn token**       | `{Số giây}` giây                         |
| **Giới hạn tốc độ**      | `{N}` request/giờ                        |

### Bảo vệ dữ liệu

| Mục                     | Nội dung                             |
| ----------------------- | ------------------------------------ |
| **Mã hoá truyền thông** | TLS 1.3                              |
| **Ghi log**             | Access log, Error log                |
| **Dữ liệu nhạy cảm**    | Mật khẩu, token xác thực được che ẩn |

---

## 9. Hiệu năng

### Mục tiêu hiệu năng

| Mục                               | Giá trị mục tiêu   |
| --------------------------------- | ------------------ |
| **Thời gian response trung bình** | Trong vòng `{N}`ms |
| **Thời gian response tối đa**     | Trong vòng `{N}`ms |
| **Số kết nối đồng thời**          | `{N}` kết nối      |
| **Thông lượng**                   | `{N}` request/giây |

---

## Tài liệu liên quan

- **Tài liệu thiết kế cơ bản**: `{Tài liệu tổng quan xử lý online_ID xử lý_Tên xử lý}`
- **Tài liệu thiết kế màn hình**: `{Tài liệu thiết kế màn hình_SCRID_Tên màn hình}`
- **Tài liệu thiết kế bảng**: `{Tài liệu thiết kế bảng_TABLE_Tên bảng}`
- **Tài liệu thiết kế SQL**: `{Tài liệu thiết kế SQL_SQLID_Tên SQL}`
