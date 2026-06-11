# Usage Guide — Skill Toolkit

> Cách dùng nhanh các skill: `knows`, `cook`, `fix`, `plan`

---

## 1. `hi:cook` — Feature Implementation

**Default:** fast mode (skip research, skip review)

### Flags

| Flag | Tác dụng |
|------|----------|
| _(none)_ | Fast: `plan → code → test → finalize` |
| `--full` | Full: thêm research + review gate |
| `--review` | Fast + có review gate ở cuối |
| `--auto` | Auto-approve, không dừng hỏi |
| `--no-test` | Skip test |

### Ví dụ

```
cook "thêm REST API cho users"        → fast, không research
cook --full "thêm REST API"            → có research + review
cook --review "sửa giao diện"          → fast + review cuối
cook --auto "thêm tính năng X"         → chạy hết, ko hỏi
cook --no-test "refactor module Y"     → code xong, skip test
cook path/to/plan.md                   → chạy theo plan có sẵn
```

---

## 2. `hi:fix` — Bug Fixing

**Default:** Quick mode (locate-only scout, typecheck+lint verify)

### Flags

| Flag | Tác dụng |
|------|----------|
| _(none)_ | Quick: 1 file, lỗi rõ, verify nhẹ |
| `--standard` | Standard: 2-5 files, debug + build+test |
| `--deep` | Deep: 5+ files, parallel research |
| `--parallel` | Nhiều issue độc lập |
| `--review` | Thêm review gate |

### Ví dụ

```
fix "type error ở login.ts"            → Quick: locate→diagnose→fix→typecheck
fix --standard "API không trả data"    → Standard: scout multi + debug + test
fix --deep "hiệu năng kém"             → Deep: parallel scout + research
fix --parallel "lỗi 1" "lỗi 2"        → Xử lý đồng thời
fix --standard --review "bug payment"  → Standard + review
```

### Chọn workflow

| Mức độ | Dùng |
|--------|------|
| Lỗi type/lint đơn giản | default |
| Bug logic 2-5 files | `--standard` |
| Architecture / performance | `--deep` |
| Nhiều bug rời rạc | `--parallel` |

---

## 3. `hi:plan` — Implementation Planning

**Default:** fast mode (skip research, red team, validate)

### Flags

| Flag | Tác dụng |
|------|----------|
| _(none)_ | Fast: codebase analysis → viết plan → tasks |
| `--full` | Full: research + scope challenge + red team + validate |
| `--hard` | Hard: 2 researchers + red team |
| `--parallel` | Parallel: 2 researchers + red team |
| `--two` | Two approaches: 2 researchers, chọn sau |
| `--no-tasks` | Skip hydrate tasks (chỉ viết plan) |

### Subcommands

| Lệnh | Tác dụng |
|------|----------|
| `plan red-team {path}` | Adversarial review cho plan |
| `plan validate {path}` | Critical questions interview |
| `plan archive` | Archive plans + journal |

### Ví dụ

```
plan "thêm module notification"          → fast: analysis→plan→tasks
plan --full "module notification"        → full: research + red team
plan --hard "module notification"        → hard: 2 researchers
plan --no-tasks "module notification"    → chỉ viết plan, ko tạo tasks
plan red-team plans/notif/plan.md        → review plan đã có
plan validate plans/notif/plan.md        → validate plan đã có
plan archive                             → dọn plan cũ
```

---

## 4. `knows` — Knowledge Retrieval

**Default:** tra cứu evidence, không có flag đặc biệt.

### Cách dùng

```
knows "tại sao function X thay đổi?"        → git blame + history
knows "ảnh hưởng của function Y?"           → graph_mcp traversal
knows "architecture decision về Z?"         → mind_mcp + memory
```

### Khi nào dùng

| Mục đích | Dùng |
|----------|------|
| Tra history thay đổi | ✓ |
| Impact analysis | ✓ |
| Architecture context | ✓ |
| Fix lỗi đơn giản | ❌ — dùng `fix` |
| Implement feature | ❌ — dùng `cook` |

---

## 5. Skill hỗ trợ (leaf skills)

Các skill này được gọi tự động bởi skill chính, ít khi dùng trực tiếp.

| Skill | Ai gọi? | Mục đích |
|-------|---------|----------|
| `hi:scout` | cook, fix, debug | Quét codebase tìm file |
| `hi:journal` | cook, plan | Ghi journal cuối session |
| `sequential-thinking` | plan | Step-by-step analysis |
| `docs-seeker` | plan, debug | Tra cứu tài liệu |
| `hi:debug` | fix | Debug chuyên sâu |
| `hi:problem-solving` | fix, debug | Kỹ thuật gỡ rối khi stuck |

---

## 6. So sánh nhanh các mode

### `cook`

```
             Research  Plan  Code  Test  Review  Finalize
default         ✘      ✓     ✓     ✓      ✘        ✓
--full          ✓      ✓     ✓     ✓      ✓        ✓
--review        ✘      ✓     ✓     ✓      ✓        ✓
--auto          ✘      ✓     ✓     ✓    auto       ✓
--no-test       ✘      ✓     ✓     ✘      ✘        ✓
```

### `fix`

```
            Scout     Diagnose  Fix   Verify            Review
default     locate    inline    ✓    typecheck+lint       ✘
--standard  multi     +debug    ✓    +build+test        optional
--deep      parallel  +research ✓    comprehensive       optional
```

### `plan`

```
            Research  Scope    Red     Validate  Tasks
                      Challenge  Team
default       ✘        ✘       ✘        ✘        ✓
--full        ✓        ✓       ✓        ✓        ✓
--hard        ✓(2)     ✓       ✓        optional  ✓
--parallel    ✓(2)     ✓       ✓        optional  ✓
--two         ✓(2+)    ✓     after     after      ✓
                           select    select
```

---

## 7. Mẹo tiết kiệm token

| Tình huống | Làm | Tiết kiệm |
|------------|-----|-----------|
| Code tính năng đơn giản | `cook` (default) | ~80% so với --full |
| Fix lỗi type | `fix` (default) | ~83% so với --deep |
| Plan nhanh | `plan` (default) | ~75% so với --full |
| Research riêng | `plan --full` 1 lần, rồi `cook` | Không research lại |
| Test riêng | `cook --no-test` + test tay sau | Tiết kiệm test loop |
| Review riêng | `cook --review` | Chỉ review khi cần |
