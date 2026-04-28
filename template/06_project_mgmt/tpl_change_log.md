# So theo doi Thay doi — {Ten du an / He thong}

## Thong tin co ban

| Muc                        | Noi dung       |
| -------------------------- | -------------- |
| **Du an / He thong**       | `{Ten}`        |
| **Ngay cap nhat**          | `{YYYY-MM-DD}` |
| **Nguoi quan ly thay doi** | `{Ten}`        |

---

## Tong hop

| Trang thai     | So luong |
| -------------- | -------- |
| Pending Review | `{N}`    |
| Approved       | `{N}`    |
| Implemented    | `{N}`    |
| Rejected       | `{N}`    |

---

## Danh sach Thay doi

| Change ID | Ngay de xuat   | Loai                                     | Tom tat          | Anh huong               | Nguoi de xuat | Trang thai   | Phien ban |
| --------- | -------------- | ---------------------------------------- | ---------------- | ----------------------- | ------------- | ------------ | --------- |
| CR-001    | `{YYYY-MM-DD}` | `{Requirement / Design / Code / Config}` | {Tom tat 1 dong} | `{High / Medium / Low}` | `{Ten}`       | `{Approved}` | v`{X.XX}` |
| CR-002    | `{YYYY-MM-DD}` | `{Loai}`                                 | {Tom tat}        | `{Medium}`              | `{Ten}`       | `{Pending}`  | -         |
| CR-003    | `{YYYY-MM-DD}` | `{Loai}`                                 | {Tom tat}        | `{Low}`                 | `{Ten}`       | `{Rejected}` | -         |

---

## Chi tiet Thay doi

### CR-001: {Ten thay doi}

| Muc                   | Noi dung                                           |
| --------------------- | -------------------------------------------------- | -------- | ----------- | ---------- |
| **Ngay de xuat**      | `{YYYY-MM-DD}`                                     |
| **Nguoi de xuat**     | `{Ten}`                                            |
| **Loai thay doi**     | `{Requirement / Design / Code / Config / Process}` |
| **Trang thai**        | `{Pending Review                                   | Approved | Implemented | Rejected}` |
| **Phien ban ap dung** | v`{X.XX}`                                          |

**Hien trang (As-Is):**
{Mo ta tinh trang hien tai truoc thay doi}

**De xuat (To-Be):**
{Mo ta tinh trang mong muon sau thay doi}

**Ly do thay doi:**
{Tai sao can thay doi — yeu cau tu stakeholder, bug, cai tien, kiem tra ...}

**Anh huong den:**

- [ ] Yeu cau (Requirements): {Mo ta neu co}
- [ ] Thiet ke (Design): {Tai lieu nao can cap nhat}
- [ ] Code: {Module / Component nao bi anh huong}
- [ ] Test case: {Test case nao can cap nhat / bo sung}
- [ ] Tai lieu khac: {Tai lieu nao khac}

**Uoc tinh effort:** `{N}` gio / ngay

**Quyet dinh:**
{Approved / Rejected boi: {Ten}, ngay {YYYY-MM-DD}}
{Ly do neu Rejected:}

**Lich su khi thuc hien:**
| Ngay | Hanh dong | Nguoi |
|---|---|---|
| `{YYYY-MM-DD}` | {Mo ta: implemented vao PR #NNN} | `{Ten}` |

---

### CR-002: {Ten thay doi}

_(Tiep tuc theo cung cau truc)_
