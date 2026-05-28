---
name: hi:cook
description: "ALWAYS activate before implementing ANY feature, plan, or fix."
argument-hint: "[task] [--fast|--parallel|--auto|--no-test]"
metadata:
  author: baka3k
  version: "2.2.0"
---
# Cook - Feature Implementation

<HARD-GATE>
Do NOT write code until a plan exists and has been reviewed.
User override: "just code it" or "skip planning" - then respect.
</HARD-GATE>

## Intent Detection
| Input | Mode | Behavior |
|-------|------|----------|
| --fast, "quick", "asap" | fast | Skip research, scout->plan->code |
| --auto, "trust me", "yolo" | auto | Auto-approve all, no review stops |
| --parallel, 3+ features | parallel | Multi-agent |
| --no-test | no-test | Skip testing |
| Path to plan.md/phase-*.md | code | Execute existing plan |
| Default | interactive | Full workflow with review gates |

## Process Flow
`[Research?] -> [Plan?] -> [Implement] -> [Test] -> [Review] -> [Finalize]`

## Mode Matrix
| Mode | Research | Testing | Review Gates |
|------|----------|---------|--------------|
| interactive | Yes | Yes | Stops at each |
| auto | Yes | Yes | Skipped |
| fast | No | Yes | Stops at each |
| parallel | Optional | Yes | Stops at each |
| no-test | Yes | No | Stops at each |

## Steps

### Step 1: Research (skip fast/code)
Spawn researcher + hi:scout. Reports <=150 lines. Gate: user approves.

### Step 2: Plan (skip code)
Spawn planner. Fast: /hi:plan --fast. Gate: user validates.

### Step 3: Implement
Execute phase tasks. TaskUpdate in_progress on start.
Parallel: launch fullstack-developer per phase.

### Step 4: Test (skip no-test)
MUST spawn tester. 100% pass required. Failures -> spawn debugger -> fix -> repeat.

### Step 5: Review
MUST spawn code-reviewer. Score>=9.5 + 0 critical = auto-approve (auto mode only).
Interactive: max 3 fix cycles, user approves.

### Step 6: Finalize
1. project-manager -> sync-back all phases
2. docs-manager -> update ./docs
3. TaskUpdate all tasks complete
4. git-manager -> commit
5. /hi:journal

## Review Cycle
- Interactive: Run code-reviewer -> score, critical, warnings -> AskUserQuestion
- Auto: score>=9.5 & 0 critical = auto-approve
- Critical issues always block: Security, Performance (O(n^2) where O(n) possible), Architecture violations
