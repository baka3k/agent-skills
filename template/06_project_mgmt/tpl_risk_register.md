# So theo doi Rui ro — {Ten du an / He thong}

## Thong tin co ban

| Muc                  | Noi dung       |
| -------------------- | -------------- |
| **Du an / He thong** | `{Ten}`        |
| **Ngay cap nhat**    | `{YYYY-MM-DD}` |
| **Nguoi quan ly**    | `{Ten}`        |

---

## Thang danh gia

### Muc do kha nang xay ra (Likelihood)

| Muc    | Mo ta                         | Diem |
| ------ | ----------------------------- | ---- |
| Low    | It co kha nang xay ra (< 20%) | 1    |
| Medium | Co the xay ra (20-60%)        | 2    |
| High   | Co kha nang cao (> 60%)       | 3    |

### Muc do anh huong (Impact)

| Muc    | Mo ta                                             | Diem |
| ------ | ------------------------------------------------- | ---- |
| Low    | Anh huong nho, du an van di dung tien do          | 1    |
| Medium | Anh huong dang ke, can dieu chinh ke hoach        | 2    |
| High   | Anh huong nghiem trong, co the lam du an that bai | 3    |

**Risk Score = Likelihood x Impact**

- 1-2: Green (Chap nhan)
- 3-4: Yellow (Theo doi)
- 6-9: Red (Can xu ly khan cap)

---

## Danh sach Rui ro

| ID    | Mo ta Rui ro       | Loai                                      | Likelihood | Impact | Score | Muc do | Bien phap giam thieu     | Ke hoach du phong     | Nguoi chiu trach nhiem | Trang thai                      |
| ----- | ------------------ | ----------------------------------------- | ---------- | ------ | ----- | ------ | ------------------------ | --------------------- | ---------------------- | ------------------------------- |
| R-001 | `{Mo ta rui ro 1}` | `{Tech / Business / Resource / External}` | Medium     | High   | 6     | Red    | `{Bien phap giam thieu}` | `{Ke hoach du phong}` | `{Ten}`                | `{Active / Mitigated / Closed}` |
| R-002 | `{Mo ta rui ro 2}` | `{Loai}`                                  | Low        | Medium | 2     | Green  | `{Bien phap}`            | `{Ke hoach}`          | `{Ten}`                | `{Active}`                      |
| R-003 | `{Mo ta rui ro 3}` | `{Loai}`                                  | High       | High   | 9     | Red    | `{Bien phap}`            | `{Ke hoach}`          | `{Ten}`                | `{Active}`                      |

---

## Chi tiet Rui ro

### R-001: {Ten rui ro}

**Mo ta:** {Mo ta day du tinh huong rui ro}

**Nguyen nhan co the:** {Nguyen nhan}

**Anh huong neu xay ra:** {Anh huong cu the den du an / san pham / team}

**Bien phap giam thieu (Mitigation):**

- {Hanh dong giam thieu 1}
- {Hanh dong giam thieu 2}

**Ke hoach du phong (Contingency):**

- {Neu rui ro xay ra, lam gi}

**Lich su cap nhat:**
| Ngay | Cap nhat | Nguoi |
|---|---|---|
| `{YYYY-MM-DD}` | {Mo ta} | `{Ten}` |

---

### R-002: {Ten rui ro}

**Mo ta:** {Mo ta}

**Bien phap giam thieu:**

- {Hanh dong}

**Ke hoach du phong:**

- {Ke hoach}

---

## Tong quan Dashboard

| Muc do             | So luong | Danh sach ID |
| ------------------ | -------- | ------------ |
| Red (can xu ly)    | `{N}`    | R-001, R-003 |
| Yellow (theo doi)  | `{N}`    | R-00x        |
| Green (chap nhan)  | `{N}`    | R-002        |
| Mitigated / Closed | `{N}`    | -            |
