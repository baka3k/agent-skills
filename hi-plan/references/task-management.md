# Task Management

## Reality
Tasks are **session-scoped** (die with session). Plan files are **persistent**.

**CLI-only:** TaskCreate/TaskUpdate. If error (VSCode), use TodoWrite.

## Hydration Pattern
```
Plan Files (persistent)  <->  Tasks (session-scoped)
     [ ] Phase 1         ->   TaskCreate(phase1)
     [x] Phase 2         <-   TaskUpdate(completed)
```

## When to Create
- Default: auto-hydrate after plan write
- Skip: --no-tasks flag
- <3 phases: skip (overhead > benefit)

## Patterns
```
TaskCreate(
  subject: "Setup database migrations",
  activeForm: "Setting up database",
  description: "See phase-01-setup.md",
  metadata: { phase: 1, priority: "P1", effort: "2h", planDir: "...", phaseFile: "..." }
)
```

## Dependencies
Phase 1 (no blockers) -> Phase 2 (blockedBy: [P1-id]) -> Phase 3 (blockedBy: [P2-id])

## Cook Handoff
- Same session: TaskList -> finds existing tasks -> picks up
- New session: TaskList -> empty -> re-hydrate from unchecked [ ] items
- Sync-back: project-manager updates [ ] -> [x] in phase files
