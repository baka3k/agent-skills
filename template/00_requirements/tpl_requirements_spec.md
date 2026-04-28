# Tài liệu Đặc tả Yêu cầu — {Tên hệ thống / Tính năng}

## Thông tin cơ bản

| Muc                      | Noi dung       | Review   | Approved   | Comment    |
| ------------------------ | -------------- | -------- | ---------- | ---------- |
| **ID tai lieu**          | `REQ-{NNN}`    |          |            |            |
| **He thong / Tinh nang** | `{Ten}`        |          |            |            |
| **Phien ban**            | v0.00          |          |            |            |
| **Ngay tao**             | `{YYYY-MM-DD}` |          |            |            |
| **Nguoi tao**            | `{Ten}`        |          |            |            |
| **Nguoi duyet**          | `{Ten}`        |          |            |            |
| **Trang thai**           | `{Draft}       | {Review} | {Approved} | {Obsolete} |

---

## 1. Muc tieu & Pham vi

### Muc tieu

{Mo ta muc tieu nghiep vu cua he thong / tinh nang nay.
Vi du: Cho phep nhan vien tim kiem thong tin dong nghiep theo nhieu tieu chi.}

### Pham vi (Scope)

**In scope:**

- {Tinh nang / chuc nang duoc bao gom}
- {Tinh nang / chuc nang duoc bao gom}

**Out of scope:**

- {Tinh nang khong nam trong pham vi}
- {Tinh nang khong nam trong pham vi}

---

## 2. Stakeholders

| Stakeholder | Vai tro                                        | Muc do anh huong        | Lien he           |
| ----------- | ---------------------------------------------- | ----------------------- | ----------------- |
| `{Ten}`     | `{End User / Product Owner / Developer / ...}` | `{High / Medium / Low}` | `{email / slack}` |

---

## 3. Yeu cau chuc nang (Functional Requirements)

### FR-001: {Ten yeu cau}

| Muc              | Noi dung                                           |
| ---------------- | -------------------------------------------------- |
| **ID**           | `FR-001`                                           |
| **Mo ta**        | {Mo ta chi tiet yeu cau, nguoi dung co the lam gi} |
| **Actor**        | `{Ai su dung}`                                     |
| **Priority**     | `{Must Have / Should Have / Nice to Have}`         |
| **UC lien quan** | `{UCxxx}`                                          |

**Acceptance Criteria:**

- [ ] {Tieu chi chap nhan 1 — Given ... When ... Then ...}
- [ ] {Tieu chi chap nhan 2}
- [ ] {Tieu chi chap nhan 3}

---

### FR-002: {Ten yeu cau}

| Muc              | Noi dung                                   |
| ---------------- | ------------------------------------------ |
| **ID**           | `FR-002`                                   |
| **Mo ta**        | {Mo ta}                                    |
| **Actor**        | `{Ai su dung}`                             |
| **Priority**     | `{Must Have / Should Have / Nice to Have}` |
| **UC lien quan** | `{UCxxx}`                                  |

**Acceptance Criteria:**

- [ ] {Tieu chi 1}
- [ ] {Tieu chi 2}

---

## 4. Yeu cau phi chuc nang (Non-Functional Requirements)

### Hieu nang (Performance)

| Muc              | Yeu cau                        | Do uu tien  |
| ---------------- | ------------------------------ | ----------- |
| Response time    | `{< N ms cho 95th percentile}` | Must Have   |
| Throughput       | `{N request/giay}`             | Must Have   |
| Concurrent users | `{N nguoi dung dong thoi}`     | Should Have |

### Bao mat (Security)

| Muc                 | Yeu cau                                 |
| ------------------- | --------------------------------------- |
| Xac thuc            | `{OAuth 2.0 / JWT / Session}`           |
| Phan quyen          | `{RBAC — liet ke roles}`                |
| Ma hoa truyen thong | `{TLS 1.3}`                             |
| Ma hoa du lieu tinh | `{AES-256 / ...}`                       |
| Kiem tra xam nhap   | `{OWASP Top 10 / Phan tich tinh / ...}` |

### Do san sang (Availability)

| Muc                            | Yeu cau                         |
| ------------------------------ | ------------------------------- |
| Uptime                         | `{99.9% = downtime < 8.7h/nam}` |
| RTO (Recovery Time Objective)  | `{< N gio}`                     |
| RPO (Recovery Point Objective) | `{< N gio}`                     |
| Bao tri                        | `{Khung gio: ...}`              |

### Kha nang mo rong (Scalability)

- {Mo ta chien luoc mo rong: horizontal / vertical / auto-scaling}

### Kha nang bao tri (Maintainability)

- {Yeu cau ve code coverage, logging, documentation}

---

## 5. Rang buoc (Constraints)

| Loai rang buoc     | Mo ta                                        |
| ------------------ | -------------------------------------------- |
| Cong nghe          | `{Phai su dung Java 17, PostgreSQL 15, ...}` |
| Ngan sach          | `{...}`                                      |
| Thoi gian          | `{Deadline: YYYY-MM-DD}`                     |
| Phap ly / Tuan thu | `{GDPR / ISO 27001 / ...}`                   |
| Tuong thich        | `{Phai tuong thich voi he thong X hien co}`  |

---

## 6. Gia dinh (Assumptions)

- {Gia dinh 1: Vi du moi nguoi dung co mot tai khoan duy nhat}
- {Gia dinh 2}
- {Gia dinh 3}

---

## 7. Rui ro va phu thuoc

| Rui ro / Phu thuoc | Loai                  | Anh huong               | Xu ly              |
| ------------------ | --------------------- | ----------------------- | ------------------ |
| `{Mo ta}`          | `{Risk / Dependency}` | `{High / Medium / Low}` | `{Xu ly / Mitian}` |

---

## 8. Ma tran phu hop Yeu cau — UC

| Yeu cau | UC001 | UC002 | UC003 |
| ------- | ----- | ----- | ----- |
| FR-001  | X     |       |       |
| FR-002  | X     | X     |       |
| FR-003  |       | X     |       |

---

## Lich su thay doi

| Phien ban | Ngay           | Nguoi   | Noi dung         |
| --------- | -------------- | ------- | ---------------- |
| v0.00     | `{YYYY-MM-DD}` | `{Ten}` | Tao ban dau tien |
