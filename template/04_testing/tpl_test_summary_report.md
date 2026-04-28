# Bao cao Tong ket Kiem thu (Test Summary Report) — {Ten du an / He thong}

## Thong tin co ban

| Muc                        | Noi dung                          |
| -------------------------- | --------------------------------- | ---- | ------------------ |
| **Du an / He thong**       | `{SystemName}`                    |
| **Phien ban**              | v`{X.XX}`                         |
| **Chu ky kiem thu**        | `{Sprint N / Release YYYY-MM}`    |
| **Khoang thoi gian**       | `{YYYY-MM-DD}` den `{YYYY-MM-DD}` |
| **Nguoi tao bao cao**      | `{Ten QA Lead}`                   |
| **Ngay phat hanh bao cao** | `{YYYY-MM-DD}`                    |
| **Ket qua tong the**       | `{PASS                            | FAIL | CONDITIONAL PASS}` |

---

## 1. Tom tat (Executive Summary)

{Mo ta ngan gon: He thong/tinh nang nao da duoc kiem thu, trong khoang thoi gian bao lau, ket qua tong quan la gi, co de nghi deploy hay chua.

Vi du: "Sprint 3 — Da kiem thu 45 test case cho module Quan ly Nhan vien. Ket qua: 42/45 pass (93%). 3 bug con mo o muc Medium. De nghi deploy len Production sau khi fix 3 bug con lai."}

---

## 2. Pham vi kiem thu

### Tinh nang da kiem thu

| Module / Tinh nang | Loai kiem thu   | Trang thai             |
| ------------------ | --------------- | ---------------------- |
| `{Module 1}`       | Functional, API | Pass                   |
| `{Module 2}`       | Functional, UI  | Pass voi ghi chu       |
| `{Module 3}`       | Performance     | Fail — chua dat nguong |

### Tinh nang khong kiem thu (Out of Scope)

| Module / Tinh nang | Ly do                                 |
| ------------------ | ------------------------------------- |
| `{Module}`         | {Ly do — vi du: chua phat trien xong} |

---

## 3. Ket qua Test Case

### Tong hop

| Loai kiem thu | Tong TC | Pass  | Fail  | Blocked | Skip  | Pass Rate |
| ------------- | ------- | ----- | ----- | ------- | ----- | --------- |
| Functional    | `{N}`   | `{N}` | `{N}` | `{N}`   | `{N}` | `{N}%`    |
| API Test      | `{N}`   | `{N}` | `{N}` | `{N}`   | `{N}` | `{N}%`    |
| UI / E2E      | `{N}`   | `{N}` | `{N}` | `{N}`   | `{N}` | `{N}%`    |
| Performance   | `{N}`   | `{N}` | `{N}` | -       | -     | `{N}%`    |
| **TONG**      | `{N}`   | `{N}` | `{N}` | `{N}`   | `{N}` | `{N}%`    |

### Theo priority

| Priority | Tong TC | Pass  | Fail  | Pass Rate |
| -------- | ------- | ----- | ----- | --------- |
| Critical | `{N}`   | `{N}` | `{N}` | `{N}%`    |
| High     | `{N}`   | `{N}` | `{N}` | `{N}%`    |
| Medium   | `{N}`   | `{N}` | `{N}` | `{N}%`    |
| Low      | `{N}`   | `{N}` | `{N}` | `{N}%`    |

---

## 4. Tong hop Bug

### Tong hop theo Severity

| Severity | Phat hien | Da fix | Con mo | Reject / Defer |
| -------- | --------- | ------ | ------ | -------------- |
| Critical | `{N}`     | `{N}`  | `{N}`  | `{N}`          |
| High     | `{N}`     | `{N}`  | `{N}`  | `{N}`          |
| Medium   | `{N}`     | `{N}`  | `{N}`  | `{N}`          |
| Low      | `{N}`     | `{N}`  | `{N}`  | `{N}`          |
| **Tong** | `{N}`     | `{N}`  | `{N}`  | `{N}`          |

### Bug con mo (Open Bugs)

| Bug ID  | Tom tat   | Severity | Priority | Module     | Nguoi xu ly | Ghi chu             |
| ------- | --------- | -------- | -------- | ---------- | ----------- | ------------------- |
| BUG-001 | {Tom tat} | High     | P2       | `{Module}` | `{Dev}`     | {Ghi chu / ETA fix} |
| BUG-002 | {Tom tat} | Medium   | P3       | `{Module}` | `{Dev}`     |                     |

---

## 5. Do phu lot Code (Code Coverage)

| Module       | Line Coverage | Branch Coverage | Goal   | Trang thai      |
| ------------ | ------------- | --------------- | ------ | --------------- |
| `{Module 1}` | `{N}%`        | `{N}%`          | >= 80% | `{Pass / Fail}` |
| `{Module 2}` | `{N}%`        | `{N}%`          | >= 80% | `{Pass / Fail}` |
| **Tong the** | `{N}%`        | `{N}%`          | >= 80% | `{Pass / Fail}` |

---

## 6. Ket qua Performance Test

| Kich ban           | Users | Avg Response Time | P95 Response Time | Error Rate | Tieu chi | Trang thai      |
| ------------------ | ----- | ----------------- | ----------------- | ---------- | -------- | --------------- |
| Tim kiem nhan vien | `{N}` | `{N}ms`           | `{N}ms`           | `{N}%`     | < 500ms  | `{Pass / Fail}` |
| Upload file        | `{N}` | `{N}ms`           | `{N}ms`           | `{N}%`     | < 2000ms | `{Pass / Fail}` |

---

## 7. Nhung van de ton dong (Issues & Notes)

| Van de           | Anh huong   | De xuat xu ly |
| ---------------- | ----------- | ------------- |
| {Mo ta van de 1} | {Anh huong} | {De xuat}     |
| {Mo ta van de 2} | {Anh huong} | {De xuat}     |

---

## 8. Khuyen nghi va Ket luan

**Khuyen nghi:** `{Deploy ngay | Deploy sau khi fix N bug | Can kiem thu lai | Khong deploy}`

**Dieu kien de deploy (neu CONDITIONAL PASS):**

- [ ] {Bug ID}: {Ten bug} phai duoc fix va verify
- [ ] {Dieu kien khac}

**Ghi chu them:**
{Bat ky ghi chu nao them ve rui ro, viec can theo doi sau deploy, v.v.}

---

## 9. Sign-off

| Vai tro       | Ten     | Chu ky / Xac nhan | Ngay           |
| ------------- | ------- | ----------------- | -------------- |
| QA Lead       | `{Ten}` | Approved          | `{YYYY-MM-DD}` |
| Tech Lead     | `{Ten}` | Approved          | `{YYYY-MM-DD}` |
| Product Owner | `{Ten}` | Approved          | `{YYYY-MM-DD}` |
