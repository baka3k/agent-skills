---
name: hi:plan
description: "Plan implementations, design architectures, create technical roadmaps with detailed phases."
argument-hint: "[task] OR [archive|red-team|validate]"
metadata:
  author: baka3k
  version: "1.0.0"
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
| (default) | Create implementation plan |
| `archive` | Archive plans + journal |
| `red-team` | Adversarial review |
| `validate` | Critical questions interview |

If invoked without arguments, use AskUserQuestion to present options.

## Workflow Modes
| Flag | Mode | Research | Red Team | Validation |
|------|------|----------|----------|------------|
| --auto | Auto-detect | Follows mode | Follows | Follows |
| --fast | Fast | Skip | Skip | Skip |
| --hard | Hard | 2 researchers | Yes | Optional |
| --parallel | Parallel | 2 researchers | Yes | Optional |
| --two | Two approaches | 2+ researchers | After select | After select |

Add `--no-tasks` to skip task hydration.

## Process Flow
1. **Pre-Creation Check** -> Check Plan Context
2. **Cross-Plan Scan** -> Detect blockedBy/blocks, update both
3. **Scope Challenge** -> Run 3 questions, select mode (EXPANSION/HOLD/REDUCTION)
   - Skip if --fast or trivial task (<20 words)
4. **Mode Detection** -> Auto or explicit flag
5. **Research** -> Spawn researchers (skip fast)
6. **Codebase Analysis** -> Read docs, scout if needed
7. **Plan Documentation** -> Write plan.md + phase-XX.md
8. **Red Team** -> `/hi:plan red-team {path}` (hard/parallel/two)
9. **Validate** -> `/hi:plan validate {path}` (hard/parallel/two)
10. **Hydrate Tasks** -> TaskCreate per phase (default, --no-tasks to skip)
11. **Output** -> Absolute path + cook command

## Scope Challenge (Step 0)
Answer 3 questions before research:
1. What already exists? (reuse, don't rebuild)
2. What's minimum change set? (defer non-blocking)
3. Complexity check (>8 files? >2 new classes? >3 phases?)

Then ask user: EXPANSION / HOLD / REDUCTION.

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
