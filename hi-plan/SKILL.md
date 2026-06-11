---
name: hi:plan
description: "Plan implementations, design architectures, create technical roadmaps with detailed phases."
argument-hint: "[task] [--full|--hard|--parallel|--two|--no-tasks]  — default: fast mode. Sub: archive|red-team|validate"
metadata:
  author: baka3k
  version: "2.0.0"
---
# Plan - Implementation Planning

**Scan `./plans/` first.** If relevant unfinished plans exist, update them. If unclear, ask user.

## Cross-Plan Dependency Detection
1. Scan `plans/*/plan.md` (status != completed/cancelled)
2. Detect overlapping files, shared deps, same feature area
3. Classify: new needs existing output -> `blockedBy: [dir]`, new changes existing deps -> update both
4. Bidirectional: update BOTH plan.md files

## Default (No Arguments)
| Operation | Description |
|-----------|-------------|
| (default) | Create implementation plan (fast mode) |
| `--full` | Full flow: research + scope challenge + red team + validate |
| `archive` | Archive plans + journal |
| `red-team` | Adversarial review |
| `validate` | Critical questions interview |

If invoked without arguments, run fast mode trực tiếp (không AskUserQuestion).

## Workflow Modes
| Flag | Mode | Research | Red Team | Validation |
|------|------|----------|----------|------------|
| default / --fast | Fast | Skip | Skip | Skip |
| --full | Full | 1 researcher | Optional | Optional |
| --hard | Hard | 2 researchers | Yes | Optional |
| --parallel | Parallel | 2 researchers | Yes | Optional |
| --two | Two approaches | 2+ researchers | After select | After select |

Add `--no-tasks` to skip task hydration.

## Process Flow (default fast)
1. **Cross-Plan Scan** -> Chỉ quét nếu có plan active (scan nhanh)
2. **Scope Challenge** -> Skip (fast)
3. **Codebase Analysis** -> Đọc docs, scout nếu cần (không spawn researcher)
4. **Plan Documentation** -> Write plan.md + phase-XX.md
5. **Hydrate Tasks** -> TaskCreate per phase (--no-tasks để skip)
6. **Output** -> Absolute path

## Full Flow (--full)
1. **Pre-Creation Check** -> Check Plan Context
2. **Cross-Plan Scan** -> Detect blockedBy/blocks, update both
3. **Scope Challenge** -> Run 3 questions, select mode
4. **Research** -> Spawn 1 researcher
5. **Codebase Analysis** -> Read docs, scout if needed
6. **Plan Documentation** -> Write plan.md + phase-XX.md
7. **Red Team** -> `/hi:plan red-team {path}`
8. **Validate** -> `/hi:plan validate {path}`
9. **Hydrate Tasks** -> TaskCreate per phase
10. **Output** -> Absolute path + cook command

## Output Requirements
- Plans in CURRENT WORKING PROJECT DIRECTORY (not user home)
- Plan files = persistent. Tasks = session-scoped
- Invoke /hi:project-organization after output
- Respect `./docs/development-rules.md`

## Task Management
- Auto-hydrate tasks after plan write (skip --no-tasks)
- <3 phases -> skip task creation (overhead > benefit)
- Task tools CLI-only (VSCode: use TodoWrite)

## Subcommands
| Subcommand | Purpose |
|------------|---------|
| `/hi:plan archive` | Archive plans + journal |
| `/hi:plan red-team {path}` | Adversarial review |
| `/hi:plan validate {path}` | Critical questions interview |
