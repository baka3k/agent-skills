# Runbook — {Tên hệ thống}

## Thông tin cơ bản

| Mục                 | Nội dung                |
| ------------------- | ----------------------- |
| **Hệ thống**        | `{SystemName}`          |
| **Ngày cập nhật**   | `{YYYY-MM-DD}`          |
| **Tác giả**         | `{Tên}`                 |
| **Liên hệ on-call** | `{Tên / Slack / Phone}` |

---

## Danh sách thao tác vận hành

| ID     | Tên thao tác               | Trigger          | Mức độ                           |
| ------ | -------------------------- | ---------------- | -------------------------------- |
| OP-001 | {Restart service}          | {Manual / Alert} | `{Routine / Urgent / Emergency}` |
| OP-002 | {Xử lý disk đầy}           | {Alert}          | `{Urgent}`                       |
| OP-003 | {Chạy batch thủ công}      | {Manual}         | `{Routine}`                      |
| OP-004 | {Xử lý kết nối DB timeout} | {Alert}          | `{Urgent}`                       |

---

## OP-001: {Restart Service}

**Trigger**: `{Service health check fail / Manual request}`  
**Thời gian xử lý dự kiến**: `{N}` phút  
**Ảnh hưởng**: `{Service downtime khoảng N giây}`

### Các bước

```bash
# 1. Xác nhận service đang lỗi
{status_check_command}

# 2. Kiểm tra log lỗi
{log_check_command}

# 3. Restart service
{restart_command}

# 4. Xác minh service đã lên
{health_check_command}
```

**Kết quả mong đợi**: {Mô tả}  
**Nếu vẫn lỗi**: → Escalate đến `{Team / Person}` hoặc xem OP-{NNN}

---

## OP-002: {Xử lý Disk Đầy}

**Trigger**: `{Disk usage > 85%}`  
**Thời gian xử lý dự kiến**: `{N}` phút  
**Ảnh hưởng**: `{Service có thể fail nếu không xử lý kịp}`

### Các bước

```bash
# 1. Xác định thư mục chiếm nhiều dung lượng
df -h
du -sh {monitored_path}/*

# 2. Xoá log cũ (giữ N ngày gần nhất)
{log_cleanup_command}

# 3. Xoá file tạm
{tmp_cleanup_command}

# 4. Kiểm tra lại dung lượng
df -h
```

**Kết quả mong đợi**: `Disk usage < 70%`  
**Nếu vẫn không đủ**: → Tăng dung lượng disk hoặc liên hệ `{Team Infra}`

---

## OP-003: {Chạy Batch Thủ Công}

**Trigger**: `{Batch auto bị lỗi / Cần chạy lại}`  
**Thời gian xử lý dự kiến**: `{N}` phút  
**Ảnh hưởng**: `{Không ảnh hưởng service online}`

### Các bước

```bash
# 1. Kiểm tra trạng thái lần chạy trước
{batch_status_check}

# 2. Chuẩn bị input (nếu cần)
{prepare_input_command}

# 3. Chạy batch
{batch_run_command}

# 4. Kiểm tra kết quả
{batch_result_check}
```

**Kết quả mong đợi**: `{Summary log: success=N, fail=0}`  
**Nếu fail**: → Xem error log tại `{path/error.log}`

---

## OP-004: {Xử lý Kết nối DB Timeout}

**Trigger**: `{Alert: DB connection pool exhausted / Slow query alert}`  
**Thời gian xử lý dự kiến**: `{N}` phút  
**Ảnh hưởng**: `{API trả lỗi 500}`

### Các bước

```bash
# 1. Xem số kết nối hiện tại
{db_connection_check}

# 2. Xác định query chậm
{slow_query_check}

# 3. Kill connection chết
{kill_connection_command}

# 4. Restart connection pool nếu cần
{restart_pool_command}
```

**Kết quả mong đợi**: `Connection count về bình thường`  
**Nếu vẫn lỗi**: → Escalate đến `{DBA / Team Backend}`

---

## Quy trình Escalation

| Cấp độ | Điều kiện                               | Liên hệ                | Kênh          |
| ------ | --------------------------------------- | ---------------------- | ------------- |
| L1     | Không tự xử lý được sau `{N}` phút      | `{Team on-call}`       | Slack / Phone |
| L2     | L1 không giải quyết được sau `{N}` phút | `{Tech Lead / Senior}` | Phone         |
| L3     | Production down > `{N}` phút            | `{Manager / CTO}`      | Phone         |

---

## Tài liệu liên quan

- **Deployment Guide**: `deployment_guide_{system}.md`
- **Monitoring / Alert Spec**: `monitoring_alert_spec_{system}.md`
- **Release Note**: `release_note_{system}_v{X.XX}.md`
