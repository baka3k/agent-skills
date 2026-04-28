# Ke hoach Kiem thu (Test Plan) — {Ten du an / He thong}

## Thong tin co ban

| Muc                             | Noi dung             |
| ------------------------------- | -------------------- | ------ | ---------- |
| **Du an / He thong**            | `{SystemName}`       |
| **Phien ban**                   | v0.00                |
| **Phien ban he thong kiem thu** | `{Release / Sprint}` |
| **Ngay tao**                    | `{YYYY-MM-DD}`       |
| **Nguoi tao**                   | `{Ten QA Lead}`      |
| **Nguoi duyet**                 | `{Ten}`              |
| **Trang thai**                  | `{Draft              | Review | Approved}` |

---

## 1. Muc tieu Kiem thu

{Mo ta muc tieu kiem thu cho phan mem nay. Vi du: Dam bao tinh nang tim kiem nhan vien hoat dong dung theo dac ta yeu cau, khong co loi nghiem trong, dat muc tieu coverage toi thieu 80%.}

---

## 2. Pham vi

### In scope (kiem thu)

- {Tinh nang / module duoc kiem thu}
- {Tinh nang / module duoc kiem thu}

### Out of scope (khong kiem thu)

- {Tinh nang / module khong kiem thu trong lan nay, ly do}
- {Vi du: He thong thanh toan — se kiem thu trong sprint tiep theo}

---

## 3. Chien luoc Kiem thu (Test Strategy)

| Loai kiem thu         | Cong cu                             | Dieu kien vao           | Tieu chi thoat                                 | Nguoi thuc hien |
| --------------------- | ----------------------------------- | ----------------------- | ---------------------------------------------- | --------------- |
| Unit Test             | `{JUnit / Jest / Pytest}`           | Code merge vao develop  | Coverage >= 80%                                | Developer       |
| Integration Test      | `{Spring Test / Supertest}`         | Unit test pass          | Tat ca endpoint API tra ve dung                | Developer / QA  |
| API Test              | `{Postman / Newman / RestAssured}`  | Deploy len Staging      | Tat ca TC pass                                 | QA              |
| UI / E2E Test         | `{Selenium / Playwright / Cypress}` | Deploy len Staging      | Happy path pass                                | QA              |
| Performance Test      | `{JMeter / Gatling / k6}`           | Staging tuong dong Prod | Response time < {N}ms tai {N} concurrent users | QA / DevOps     |
| Security Test         | `{OWASP ZAP / Semgrep}`             | Truoc release           | Khong co loi Critical / High mo                | Security        |
| UAT (User Acceptance) | Thu cong                            | Feature complete        | Stakeholder sign-off                           | PO / End User   |

---

## 4. Moi truong Kiem thu

| Moi truong  | Muc dich                 | URL / Access | Du lieu                 | Quan ly boi |
| ----------- | ------------------------ | ------------ | ----------------------- | ----------- |
| Development | Unit / Integration tests | `{URL}`      | Mock / Seed data        | Developer   |
| Staging     | QA / UAT / Performance   | `{URL}`      | Anonymized copy of prod | QA / DevOps |
| Production  | Smoke test sau deploy    | `{URL}`      | Real data               | DevOps      |

---

## 5. Dieu kien vao / ra (Entry & Exit Criteria)

### Dieu kien vao (Entry Criteria — bat dau kiem thu)

- [ ] Code da merge vao branch kiem thu tuong ung
- [ ] Deploy thanh cong len moi truong Staging
- [ ] Test data da duoc chuan bi
- [ ] Test case da duoc review va approved

### Dieu kien thoat (Exit Criteria — ket thuc kiem thu)

- [ ] Tat ca test case co priority `Critical` va `High` da pass
- [ ] Khong con bug mo co severity `Critical` va `High`
- [ ] Test coverage >= `{N}`%
- [ ] Performance test dat nguong yeu cau
- [ ] Stakeholder sign-off UAT

---

## 6. Lich kiem thu

| Giai doan               | Tu ngay        | Den ngay       | Ghi chu           |
| ----------------------- | -------------- | -------------- | ----------------- |
| Viet test case          | `{YYYY-MM-DD}` | `{YYYY-MM-DD}` |                   |
| Unit / Integration test | `{YYYY-MM-DD}` | `{YYYY-MM-DD}` | Song song voi dev |
| API test                | `{YYYY-MM-DD}` | `{YYYY-MM-DD}` |                   |
| UI / E2E test           | `{YYYY-MM-DD}` | `{YYYY-MM-DD}` |                   |
| Performance test        | `{YYYY-MM-DD}` | `{YYYY-MM-DD}` |                   |
| UAT                     | `{YYYY-MM-DD}` | `{YYYY-MM-DD}` |                   |
| Fix bug & retest        | `{YYYY-MM-DD}` | `{YYYY-MM-DD}` |                   |
| Sign-off                | `{YYYY-MM-DD}` |                |                   |

---

## 7. Vai tro & Trach nhiem

| Vai tro       | Nguoi   | Trach nhiem                              |
| ------------- | ------- | ---------------------------------------- |
| QA Lead       | `{Ten}` | Lap ke hoach, bao cao, quan ly quy trinh |
| QA Engineer   | `{Ten}` | Viet TC, thuc hien kiem thu, bao cao bug |
| Developer     | `{Ten}` | Unit test, sua bug, ho tro debug         |
| DevOps        | `{Ten}` | Chuan bi moi truong, deployment          |
| Product Owner | `{Ten}` | UAT sign-off                             |

---

## 8. Rui ro Kiem thu

| Rui ro                                    | Anh huong                         | Bien phap                            |
| ----------------------------------------- | --------------------------------- | ------------------------------------ |
| {Vi du: Moi truong staging khong on dinh} | Tre lich, ket qua khong chinh xac | {Co ke hoach rollback, bao cao ngay} |
| {Vi du: Thieu tai nguyen QA}              | {Anh huong}                       | {Bien phap}                          |

---

## Lich su thay doi

| Phien ban | Ngay           | Nguoi   | Noi dung         |
| --------- | -------------- | ------- | ---------------- |
| v0.00     | `{YYYY-MM-DD}` | `{Ten}` | Tao ban dau tien |
