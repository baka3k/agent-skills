# Release Note — {Tên hệ thống} v{X.XX}

## Thông tin Release

| Mục               | Nội dung       |
| ----------------- | -------------- | ------------ | ------------- |
| **Hệ thống**      | `{SystemName}` |
| **Phiên bản**     | v`{X.XX}`      |
| **Ngày release**  | `{YYYY-MM-DD}` |
| **Môi trường**    | `{Staging      | Production}` |
| **Người release** | `{Tên}`        |
| **Trạng thái**    | `{Planned      | Released     | Rolled Back}` |

---

## Tóm tắt

{Mô tả 2-3 dòng tổng quan về release này — thay đổi chính là gì, tại sao release.}

---

## Tính năng mới (New Features)

| ID    | Tính năng         | Mô tả        | UC / Ticket            |
| ----- | ----------------- | ------------ | ---------------------- |
| F-001 | `{Tên tính năng}` | {Mô tả ngắn} | `{UCxxx / TICKET-NNN}` |
| F-002 | `{Tên tính năng}` | {Mô tả ngắn} | `{UCxxx / TICKET-NNN}` |

---

## Bug Fixes

| ID    | Mô tả lỗi     | Tác động                | Ticket         |
| ----- | ------------- | ----------------------- | -------------- |
| B-001 | `{Mô tả bug}` | `{High / Medium / Low}` | `{TICKET-NNN}` |
| B-002 | `{Mô tả bug}` | `{High / Medium / Low}` | `{TICKET-NNN}` |

---

## Breaking Changes

> Nếu không có: ghi **None**

| Thay đổi         | Tác động         | Cách migrate        |
| ---------------- | ---------------- | ------------------- |
| `{Tên thay đổi}` | {Mô tả tác động} | {Hướng dẫn migrate} |

---

## Migration Guide

{Nếu có breaking change hoặc cần migration DB/config:}

```bash
# Bước 1: {Mô tả bước}
{command}

# Bước 2: {Mô tả bước}
{command}
```

---

## Known Issues (Lỗi đã biết chưa fix)

| ID     | Mô tả     | Workaround        | Dự kiến fix       |
| ------ | --------- | ----------------- | ----------------- |
| KI-001 | `{Mô tả}` | `{Cách tạm thời}` | `{v{X.XX} / TBD}` |

---

## Thành phần được deploy

| Component      | Phiên bản cũ | Phiên bản mới | Ghi chú     |
| -------------- | ------------ | ------------- | ----------- |
| `{ComponentA}` | `{vOld}`     | `{vNew}`      | `{Ghi chú}` |
| `{ComponentB}` | `{vOld}`     | `{vNew}`      | `{Ghi chú}` |

---

## Quy trình Rollback

> Thực hiện khi release thất bại hoặc phát sinh vấn đề nghiêm trọng.

```bash
# Bước 1: Dừng service
{stop_command}

# Bước 2: Rollback phiên bản
{rollback_command}

# Bước 3: Rollback DB (nếu có)
{db_rollback_command}

# Bước 4: Khởi động lại
{start_command}

# Bước 5: Xác minh
{verify_command}
```

**Thời gian rollback ước tính**: `{N}` phút  
**Người có thẩm quyền rollback**: `{Tên / Role}`

---

## Checklist Trước Release

- [ ] Test case toàn bộ đã Pass
- [ ] Test_summary_report đã được approve
- [ ] Breaking changes đã thông báo cho team
- [ ] Migration script đã test trên Staging
- [ ] Rollback plan đã kiểm tra
- [ ] Monitoring/alert đã cấu hình
- [ ] Stakeholders đã được thông báo

---

## Tài liệu liên quan

- **Deployment Guide**: `deployment_guide_{env}_v{X.XX}.md`
- **Test Summary Report**: `test_summary_{version}.md`
- **Runbook**: `runbook_{system}.md`
