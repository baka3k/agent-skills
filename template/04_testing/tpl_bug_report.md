# Bao cao Bug — {Ten he thong / Du an}

## Thong tin co ban

| Muc                       | Noi dung                       |
| ------------------------- | ------------------------------ | -------- | ----------- | ----- | -------- | ------ | -------- | ---------- |
| **Bug ID**                | `BUG-{NNN}`                    |
| **He thong / Module**     | `{Module}`                     |
| **Phien ban phat hien**   | v`{X.XX}`                      |
| **Moi truong phat hien**  | `{Dev / Staging / Production}` |
| **Ngay phat hien**        | `{YYYY-MM-DD}`                 |
| **Nguoi phat hien**       | `{Ten}`                        |
| **Nguoi phu trach xu ly** | `{Ten Developer}`              |
| **Trang thai**            | `{New                          | Assigned | In Progress | Fixed | Verified | Closed | Rejected | Deferred}` |

---

## Phan loai

| Loai         | Gia tri      |
| ------------ | ------------ | ------ | ----------- | --------- | ---- | ------ | ------------ |
| **Severity** | `{Critical   | High   | Medium      | Low}`     |
| **Priority** | `{P1-Khan    | P2-Cao | P3-Normal   | P4-Thap}` |
| **Loai bug** | `{Functional | UI/UX  | Performance | Security  | Data | Config | Regression}` |

### Mo ta muc do Severity

- **Critical**: He thong crash, mat du lieu, khong the su dung chuc nang chinh
- **High**: Chuc nang quan trong bi loi, chua co workaround
- **Medium**: Chuc nang bi loi nhung co workaround
- **Low**: Loi phu, chi anh huong nho den trai nghiem

---

## Mo ta Bug

### Tom tat (Summary)

> {1 dong mo ta ngan gon, ro rang ve loi. Vi du: API tim kiem nhan vien tra ve loi 500 khi search voi ky tu dac biet}

### Muc tieu kiem tra (Objective)

{Dang thu kiem tra tinh nang / use case gi thi gap loi nay}

---

## Cac buoc tai hien (Steps to Reproduce)

1. {Buoc 1: Mo trinh duyet, truy cap URL ...}
2. {Buoc 2: Dang nhap bang tai khoan ...}
3. {Buoc 3: Vao menu ... > chon ...}
4. {Buoc 4: Nhap gia tri ... vao truong ...}
5. {Buoc 5: Nhan nut ...}

**Du lieu thu:**

| Truong         | Gia tri             |
| -------------- | ------------------- |
| `{Ten truong}` | `{Gia tri dau vao}` |
| `{Ten truong}` | `{Gia tri dau vao}` |

---

## Ket qua

### Ket qua mong doi (Expected Result)

{Mo ta he thong nen xu ly nhu the nao theo dac ta}

### Ket qua thuc te (Actual Result)

{Mo ta nhung gi thuc te xay ra — kem error message, response body neu co}

```
{Error message / Stack trace / Response body (neu co)}
```

---

## Bang chung (Evidence)

| Loai               | Mo ta / Duong dan           |
| ------------------ | --------------------------- |
| Screenshot         | `{duong dan den anh}`       |
| Video              | `{duong dan / link video}`  |
| Log file           | `{duong dan / snippet log}` |
| HAR / Request dump | `{duong dan}`               |

---

## Thong tin ky thuat

| Muc                       | Noi dung                          |
| ------------------------- | --------------------------------- |
| **Trinh duyet / Client**  | `{Chrome 120 / iOS 17 / ...}`     |
| **OS**                    | `{macOS 14 / Windows 11 / ...}`   |
| **API Endpoint**          | `{POST /api/v1/employees/search}` |
| **Request ID / Trace ID** | `{ID de tra cuu log}`             |
| **URL chinh sac**         | `{URL}`                           |
| **User ID / Account**     | `{ID tai khoan dung de test}`     |

---

## Xu ly Bug

### Nguyen nhan goc re (Root Cause)

{Developer dien sau khi phan tich. Vi du: Ham sanitize dau vao khong xu ly ky tu `%` truoc khi truyen vao LIKE query trong SQL}

### Giai phap (Fix Description)

{Mo ta cach sua. Vi du: Escape ky tu dac biet truoc khi truyen vao PreparedStatement}

**PR / Commit:** `{link PR hoac commit hash}`

### Lich su xu ly

| Ngay           | Trang thai | Nguoi        | Ghi chu             |
| -------------- | ---------- | ------------ | ------------------- |
| `{YYYY-MM-DD}` | New        | `{QA}`       | Bao cao lan dau     |
| `{YYYY-MM-DD}` | Assigned   | `{Dev Lead}` | Giao cho {Dev}      |
| `{YYYY-MM-DD}` | Fixed      | `{Dev}`      | Fix xong, PR #NNN   |
| `{YYYY-MM-DD}` | Verified   | `{QA}`       | Kiem tra lai — Pass |
| `{YYYY-MM-DD}` | Closed     | `{QA Lead}`  | Dong bug            |
