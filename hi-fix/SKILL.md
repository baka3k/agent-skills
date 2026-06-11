---
name: hi:fix
description: "ALWAYS activate before fixing ANY bug, error, test failure, CI/CD issue, type error, lint, log error, UI issue, code problem."
argument-hint: "[issue] [--standard|--deep|--parallel|--review]  — default: Quick mode"
metadata:
  author: baka3k
  version: "2.0.0"
---
# Fix - Issue Resolution

## Mode Selection
| Flag | When |
|------|------|
| default | Quick: 1 file, type/lint, lỗi rõ ràng |
| --standard | Standard: 2-5 files, cần debug đầy đủ |
| --deep | Deep: 5+ files, architecture impact |
| --parallel | 2+ independent issues |
| --review | Human-in-the-loop at each step |

## Process Flow
`[Scout] -> [Diagnose] -> [Fix] -> [Verify+Prevent] -> [Finalize]`

<HARD-GATE>
Do NOT fix before Scout + Diagnose. Find ROOT CAUSE first. If 3+ fix attempts fail, STOP and question architecture with user.
</HARD-GATE>

### Step 1: Scout (locate-only, default)
Locate affected files và đọc lỗi. 1 agent là đủ.
Standard/Deep: activate hi:scout hoặc 2-3 parallel agents.

### Step 2: Diagnose (MANDATORY)
Capture pre-fix state: exact error, stack traces, logs.
Trace backward: symptom -> immediate cause -> contributing factor -> ROOT CAUSE.
Nếu khó: activate hi:debug. Nếu 2+ hypotheses fail -> activate hi:problem-solving.

### Step 3: Fix
Fix ROOT CAUSE. Minimal changes. Follow existing patterns.

### Step 4: Verify + Prevent
Quick: typecheck + lint (mặc định)
Standard: + build + test
Deep: comprehensive (edge cases, security, perf)

### Step 5: Finalize
Quick: report ngắn -> ask commit (skip docs, skip review)
Standard/Deep: report -> review (nếu --review) -> docs -> commit

## Workflows

### Quick (default, 1 file, type/lint, clear error)
Scout (locate only) -> Diagnose (read error) -> Fix -> Verify (typecheck+lint) -> Done

### Standard (--standard, 2-5 files)
Full Scout -> Full Diagnose (gọi hi:debug nếu cần) -> Fix -> Verify (typecheck+lint+build+test) -> Review (nếu --review) -> Finalize

### Deep (--deep, 5+ files, architecture impact)
Parallel Scout + Diagnose + Research -> Fix -> Comprehensive Verify -> Review -> Finalize

### Parallel (2+ independent)
Separate task tree per issue. Spawn fullstack-developer per issue.
