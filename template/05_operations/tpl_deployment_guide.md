# Hướng dẫn Deployment — {Tên hệ thống} v{X.XX}

## Thông tin cơ bản

| Mục               | Nội dung       |
| ----------------- | -------------- | ------- | ------------ |
| **Hệ thống**      | `{SystemName}` |
| **Phiên bản**     | v`{X.XX}`      |
| **Môi trường**    | `{Dev          | Staging | Production}` |
| **Ngày cập nhật** | `{YYYY-MM-DD}` |
| **Tác giả**       | `{Tên}`        |

---

## 1. Điều kiện tiên quyết

- [ ] Đã có quyền truy cập server / cloud console
- [ ] Đã cài đặt: `{tool1 vX.X}`, `{tool2 vX.X}` (ví dụ: Docker, kubectl, Ansible)
- [ ] Biến môi trường đã được cấu hình (xem Mục 4)
- [ ] Backup DB đã tạo xong
- [ ] Release Note đã được review

---

## 2. Tổng quan các thành phần deploy

| Component              | Phương thức                         | Server / Cluster |
| ---------------------- | ----------------------------------- | ---------------- |
| `{ComponentA}`         | `{Docker / JAR / ZIP / ...}`        | `{host:port}`    |
| `{ComponentB}`         | `{Docker / JAR / ZIP / ...}`        | `{host:port}`    |
| `{Database migration}` | `{Flyway / Liquibase / SQL script}` | `{DB host}`      |

---

## 3. Hướng dẫn Deploy từng bước

### Bước 1: {Chuẩn bị / Pull code / Build image}

```bash
# {Mô tả bước 1}
{command_1}
{command_2}
```

### Bước 2: {Database Migration}

```bash
# {Mô tả: chạy migration script}
{migration_command}
```

> ⚠️ **Chú ý**: {Cảnh báo nếu có, ví dụ: migration không rollback được}

### Bước 3: {Deploy Component A}

```bash
# {Mô tả}
{deploy_command_a}
```

### Bước 4: {Deploy Component B}

```bash
# {Mô tả}
{deploy_command_b}
```

### Bước 5: Xác minh Deploy

```bash
# Kiểm tra service đang chạy
{health_check_command}

# Kiểm tra log
{log_check_command}

# Smoke test
{smoke_test_command}
```

**Kết quả mong đợi**: {Mô tả output bình thường}

---

## 4. Cấu hình môi trường

| Biến           | Dev     | Staging | Production               | Mô tả              |
| -------------- | ------- | ------- | ------------------------ | ------------------ |
| `{ENV_VAR_1}`  | `{val}` | `{val}` | `{val}`                  | `{Mô tả}`          |
| `{ENV_VAR_2}`  | `{val}` | `{val}` | `{val}`                  | `{Mô tả}`          |
| `{SECRET_KEY}` | -       | -       | _(Vault/Secret Manager)_ | `{Không hardcode}` |

---

## 5. Rollback

> Thực hiện khi deploy thất bại hoặc có vấn đề nghiêm trọng sau deploy.

```bash
# Bước 1: Rollback service về phiên bản trước
{rollback_service_command}

# Bước 2: Rollback DB (nếu cần)
{rollback_db_command}

# Bước 3: Xác minh
{verify_command}
```

**Thời gian rollback ước tính**: `{N}` phút

---

## 6. Xử lý sự cố thường gặp

| Triệu chứng         | Nguyên nhân có thể             | Hành động                            |
| ------------------- | ------------------------------ | ------------------------------------ |
| Service không start | `{Config sai / Port conflict}` | `{Kiểm tra log tại {path}}`          |
| DB migration fail   | `{Script lỗi / Timeout}`       | `{Rollback migration: {command}}`    |
| Health check fail   | `{Service chưa sẵn sàng}`      | `{Đợi thêm Ns, kiểm tra {log path}}` |

---

## Tài liệu liên quan

- **Release Note**: `release_note_{system}_v{X.XX}.md`
- **Runbook**: `runbook_{system}.md`
- **System Architecture**: `tpl_system_architecture.md`
