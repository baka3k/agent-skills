# AGENT WORKING CONTRACT

[One-sentence project purpose]

## Startup Workflow

Before writing code:

1. **Confirm working directory** with `pwd`
2. **Read this file** completely
3. **Check `.harness/` exists** — if not, run `dev harness init` to bootstrap
4. **Run `.harness/scripts/init.sh`** to verify MCP endpoints are reachable
5. **Read `.harness/state/feature_list.json`** to see the task backlog
6. **Pick one `todo` task** — work on the highest-priority item only
7. **Review recent commits** with `git log --oneline -5`

If MCP endpoints are unreachable, run `dev mcp start` first.
If baseline verification is failing, repair that before adding new scope.

## Working Rules

- **One task at a time**: Pick exactly one `todo` task from `feature_list.json`
- **Graph-first scope**: Use `graph_entry_node` to anchor context before editing
- **Verify before done**: Don't mark task `done` without running `.harness/scripts/verify.sh`
- **Log scope violations**: If you edit a file outside `related_files`, note it in the session log
- **Leave clean state**: Next session must run `.harness/scripts/init.sh` without errors

## Task Lifecycle

```
todo → in_progress → done
                  ↘ blocked  (if verify fails after max_rounds)
```

Update `status` in `.harness/state/feature_list.json` as you work.
The orchestrator manages `session_id` automatically — do not set it manually.

## Required Artifacts

- `.harness/config.yaml` — MCP endpoints, budget limits, verify commands
- `.harness/state/feature_list.json` — Task backlog (source of truth)
- `.harness/state/progress.md` — Session continuity log
- `.harness/scripts/init.sh` — MCP health check + env validation
- `.harness/scripts/verify.sh` — Critical test / lint / type gate
- `.harness/scripts/context_selector.py` — Graph + vector context builder
- `.harness/scripts/orchestrator.py` — Session lifecycle manager

## Definition of Done

A task is done only when ALL of the following are true:

- [ ] Implementation complete and scoped to `related_files` / `related_modules`
- [ ] `.harness/scripts/verify.sh` exits 0 (critical checks pass)
- [ ] Task status set to `done` in `feature_list.json`
- [ ] Session log written to `.harness/state/session_log/`
- [ ] Repository restartable from `.harness/scripts/init.sh`

## End of Session

Before ending a session:

1. Update `.harness/state/progress.md` with current state
2. Update task `status` in `feature_list.json`
3. Record unresolved risks or blockers in `notes` field
4. Commit with descriptive message
5. Leave repo clean enough for `dev harness run` to restart immediately

## Verification Commands

```bash
# Run via CortexHarness CLI
dev harness verify

# Or directly
bash .harness/scripts/verify.sh

# Full orchestrated session (picks next todo task automatically)
dev harness run
```

## Context Commands

```bash
# Show backlog
dev harness task list

# Check MCP health + backlog summary
dev harness status

# Build context for a specific task (queries graph_mcp + mind_mcp)
dev harness context task-001
```

## Escalation

If you encounter:
- **MCP unreachable**: Run `dev mcp start`, then re-run `init.sh`
- **Architecture decisions**: Consult project docs or ask user
- **Unclear requirements**: Re-read task `notes` in `feature_list.json` or ask user
- **Repeated verify failures**: Set task to `blocked`, update `notes`, stop session
- **Scope ambiguity**: Use `graph_entry_node` + `related_modules` as the boundary
