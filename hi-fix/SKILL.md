---
name: hi:fix
description: "ALWAYS activate before fixing ANY bug, error, test failure, CI/CD issue, type error, lint, log error, UI issue, code problem."
argument-hint: "[issue] --auto|--review|--quick|--parallel"
metadata:
  author: baka3k
  version: "1.0.0"
---
# Fix - Issue Resolution

## Mode Selection
| Flag | When |
|------|------|
| --quick | Type errors, lint, trivial (auto-triggered) |
| --parallel | 2+ independent issues |
| --review | Human-in-the-loop at each step |
| default | Autonomous, auto-approve if score>=9.5 |

## Process Flow
`[Scout] -> [Diagnose] -> [Fix] -> [Verify+Prevent] -> [Finalize]`

<HARD-GATE>
Do NOT fix before Scout + Diagnose. Find ROOT CAUSE first. If 3+ fix attempts fail, STOP and question architecture with user.
</HARD-GATE>

### Step 1: Scout
Activate hi:scout or 2-3 parallel Explore agents. Map: affected files, deps, tests, git log.

### Step 2: Diagnose (MANDATORY)
Capture pre-fix state: exact error, stack traces, logs.
Trace backward: symptom -> immediate cause -> contributing factor -> ROOT CAUSE.
If 2+ hypotheses fail -> activate hi:problem-solving.

### Step 3: Fix
Fix ROOT CAUSE. Minimal changes. Follow existing patterns.

### Step 4: Verify + Prevent
1. Re-run EXACT commands from pre-fix state. Compare before/after.
2. Add regression test (fails without fix, passes with fix).
3. Add guards where applicable.

### Step 5: Finalize
1. Report: root cause, changes, prevention
2. Update docs if needed
3. Ask to commit

## Workflows

### Quick (1 file, type/lint, clear error)
Scout (locate only) -> Diagnose (read error) -> Fix -> Verify (typecheck+lint) -> Done

### Standard (2-5 files)
Full Scout -> Full Diagnose -> Fix -> Verify (typecheck+lint+build+test) -> Review -> Finalize

### Deep (5+ files, architecture impact)
Parallel Scout + Diagnose + Research -> Fix -> Comprehensive Verify -> Review -> Finalize

### Parallel (2+ independent)
Separate task tree per issue. Spawn fullstack-developer per issue.
