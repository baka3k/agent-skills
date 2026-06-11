# Skill Optimization Plan

> Mục tiêu: giảm token burn tối đa khi dùng bộ skill knows + cook + fix + plan

---

## 1. Phân tích token burn

| Skill | Mức độ | Nguyên nhân chính |
|-------|--------|-------------------|
| **cook** | 🔴 Extreme | Spawn 4-6 subagents (researcher, planner, tester, reviewer, docs, journal). Mỗi subagent = 10-15K tokens. Test loop spawn debugger. |
| **fix** | 🔴 Cao | Scout multi-agent + diagnose (gọi debug sub-skill) + verify (typecheck+lint+build+test) |
| **plan** | 🟡 TB | Research spawn + scope challenge + red team + validate |
| **debug** | 🟡 TB | 10 reference files + spawn sub-skills |
| **scout** | 🟢 Thấp | Chỉ spawn parallel agents đọc file |
| **knows** | 🟢 Thấp | Chỉ gọi MCP tool + git commands |
| **problem-solving** | 🟢 Thấp | Load reference on-demand, không spawn |
| **sequential-thinking** | 🟢 Rất thấp | Methodology thuần |
| **docs-seeker** | 🟢 Rất thấp | Script-first, zero-token |
| **journal** | 🟢 Rất thấp | Single subagent nhẹ |

---

## 2. Tối ưu `cook` — 🔴 Extreme → 🟢 Tiết kiệm

### Vấn đề
- Mặc định là `interactive` → full 6 bước
- Spawn researcher, planner, tester, reviewer, docs-manager
- Test loop spawn debugger mỗi lần fail

### Giải pháp

| Thay đổi | Trước | Sau |
|----------|-------|-----|
| Default mode | `interactive` | **`fast`** |
| Research | Spawn researcher + hi:scout | `sequential-thinking` + `docs-seeker` trực tiếp, không spawn |
| Plan | Spawn planner riêng | Gọi `hi:plan` inline, không spawn riêng |
| Test | MUST spawn tester, spawn debugger khi fail | Run test command, chỉ spawn debugger khi fail >2 lần |
| Review | MUST spawn code-reviewer | **Optional** — bỏ mặc định, chạy khi user yêu cầu (`--review`) |
| Finalize | project-manager + docs-manager + git-manager | Chỉ journal + git commit |

### Token savings
- Spawn researcher: ~12K → 0 (dùng inline)
- Spawn planner: ~12K → 0 (dùng inline)
- Spawn tester: ~12K → 0 (run command)
- Spawn debugger: ~12K → chỉ khi fail >2 lần
- Spawn reviewer: ~12K → 0 (bỏ mặc định)
- Spawn docs-manager: ~8K → 0 (bỏ)
- **Tổng: ~60-80K tokens → ~10-15K tokens**

---

## 3. Tối ưu `fix` — 🔴 Cao → 🟢 Tiết kiệm

### Vấn đề
- Mặc định là `Autonomous` → chạy Standard workflow
- Scout: spawn 2-3 parallel agents (20-30K tokens)
- Diagnose: gọi hi:debug (load references + spawn)
- Verify: typecheck + lint + build + test

### Giải pháp

| Thay đổi | Trước | Sau |
|----------|-------|-----|
| Default mode | Autonomous (Standard) | **Quick** |
| Scout | 2-3 parallel agents | Locate-only, 1 agent |
| Diagnose | Gọi hi:debug | Đọc error + trace inline |
| Verify | typecheck+lint+build+test | typecheck+lint |
| Review | Có | Bỏ (chỉ khi --review) |
| Finalize | Report + docs + git | Chỉ report |

### Token savings
- Scout: ~20-30K → ~5K
- Diagnose: ~15K → ~3K
- Verify: ~10K → ~3K
- Review + Finalize: ~15K → 0
- **Tổng: ~60-70K tokens → ~11K tokens**

---

## 4. Tối ưu `plan` — 🟡 TB → 🟢 Tiết kiệm

### Vấn đề
- Mặc định chạy full flow (research + scope challenge + red team + validate)
- Research spawn subagent (10-15K tokens)
- Cross-plan scan đọc nhiều file plan.md

### Giải pháp

| Thay đổi | Trước | Sau |
|----------|-------|-----|
| Default mode | (full flow) | **`--fast`** |
| Research | Spawn researchers | Skip (fast) |
| Red Team | Có (hard/parallel/two) | Skip (fast) |
| Validate | Có (hard/parallel/two) | Skip (fast) |
| Scope Challenge | Luôn chạy | Chỉ khi task >20 words |
| Cross-Plan Scan | Luôn quét | Chỉ khi có plan active |

---

## 5. Tổng token savings

| Skill | Trước | Sau | Tiết kiệm |
|-------|-------|-----|-----------|
| cook | ~80K tokens | ~15K tokens | **~80%** |
| fix | ~65K tokens | ~11K tokens | **~83%** |
| plan | ~40K tokens | ~10K tokens | **~75%** |
| **Tổng** | **~185K tokens** | **~36K tokens** | **~80%** |

---

## 6. Các thay đổi cụ thể

### File: `hi-cook/SKILL.md`
- [x] Default mode: `interactive` → `fast`
- [x] Step 1 Research: dùng inline skills thay vì spawn researcher + hi:scout
- [x] Step 2 Plan: gọi hi:plan inline, không spawn planner riêng
- [x] Step 4 Test: chạy command, spawn debugger chỉ khi fail >2 lần
- [x] Step 5 Review: MUST → optional (flag `--review`)
- [x] Step 6 Finalize: bỏ project-manager, docs-manager, git-manager

### File: `hi-fix/SKILL.md`
- [x] Default mode: Autonomous → Quick
- [x] scout: 2-3 parallel → locate-only
- [x] diagnose: gọi hi:debug → inline trace
- [x] verify: bỏ build+test mặc định
- [x] Bỏ review khỏi default flow

### File: `hi-plan/SKILL.md`
- [x] Default mode: full flow → `--fast`
- [x] Bỏ research, red team, validate mặc định
