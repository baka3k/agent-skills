---
name: hi:cook
description: "ALWAYS activate before implementing ANY feature, plan, or fix."
argument-hint: "[task] [--full|--review|--auto|--no-test]  — default: fast mode"
metadata:
  author: baka3k
  version: "3.0.0"
---
# Cook - Feature Implementation

<HARD-GATE>
Do NOT write code until a plan exists and has been reviewed.
User override: "just code it" or "skip planning" - then respect.
</HARD-GATE>

## Intent Detection
| Input | Mode | Behavior |
|-------|------|----------|
| --full, "full" | full | Full workflow với research + review |
| --review | review | Có review gate ở cuối |
| --auto, "trust me", "yolo" | auto | Auto-approve all |
| --no-test | no-test | Skip testing |
| Path to plan.md/phase-*.md | code | Execute existing plan |
| Default | fast | Skip research, skip review, test nhanh |

## Process Flow
`[Plan] -> [Implement] -> [Test] -> [Finalize]`

## Mode Matrix
| Mode | Research | Review | Testing |
|------|----------|--------|---------|
| fast (default) | Skip | Skip | Run command |
| full | Yes | MUST | Run command |
| review | Skip | MUST | Run command |
| auto | Skip | Auto-pass | Run command |
| no-test | Skip | Skip | Skip |

## Steps

### Step 1: Plan (skip if plan.md provided)
- Dùng `sequential-thinking` để phân tích task ngắn gọn
- Dùng `docs-seeker` nếu cần tra cứu tài liệu
- Không spawn planner riêng. Gọi `hi:plan --fast` inline nếu cần.

### Step 2: Implement
Execute tasks trực tiếp. TaskUpdate in_progress trên mỗi task.
Parallel mode: launch fullstack-developer per phase.

### Step 3: Test (skip no-test)
Run test command. Xem output. Nếu fail:
  - Lần 1-2: tự phân tích và fix
  - Lần 3+: spawn `hi:fix` để debug chuyên sâu
Không spawn tester riêng.

### Step 4: Finalize
1. TaskUpdate all tasks complete
2. git commit
3. /hi:journal

## Review (optional, flag --review hoặc full mode)
Run code-reviewer. Score>=9.5 + 0 critical = auto-approve (auto mode only).
Max 3 fix cycles. Critical issues always block: Security, Performance, Architecture violations.
