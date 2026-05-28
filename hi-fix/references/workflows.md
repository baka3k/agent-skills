# Workflow Variants

## Quick (Simple: 1 file, type/lint, clear error)
1. Scout: locate file + direct deps only
2. Diagnose: read error, identify root cause
3. Fix: apply fix
4. Verify: typecheck + lint
5. Done. Ask to commit if auto mode.

## Standard (Moderate: 2-5 files)
1. Scout: hi:scout or 2-3 parallel Explore
2. Diagnose: capture pre-fix -> debug -> trace root cause
3. Fix: minimal changes
4. Verify: typecheck + lint + build + test
5. Review: code-reviewer
6. Finalize: report -> docs -> git -> journal

## Deep (Complex: 5+ files, architecture impact)
1. Parallel: Scout + Diagnose + Research
2. Fix: root cause
3. Verify: comprehensive (edge cases, security, perf)
4. Review: code-reviewer
5. Finalize

## Parallel (2+ independent issues)
Separate task tree per issue. Spawn fullstack-developer per tree.
Final integration verify task blocked by all issue verify tasks.

## Specialized (merge into standard workflow)
- **CI**: Fetch logs (gh run view --log-failed), analyze, fix, test locally
- **Logs**: Read last N lines, focus on stack traces, patterns
- **Test**: Compile failures, group by module, fix shared root causes first
- **Type Errors**: tsc --noEmit, fix ALL errors, never use any
- **UI**: Analyze screenshot, implement, verify visually
