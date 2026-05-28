# Scope Challenge

Run BEFORE research. Forces intent clarification.

## Skip If
- --fast mode
- Task is trivial (single file fix, <20 words)

## The 3 Questions
1. **What already exists?** (reuse, don't rebuild)
2. **What's minimum change set?** (defer non-blocking)
3. **Complexity check** (>8 files? >2 new classes? >3 phases? justify each)

## Mode Selection
Ask user: EXPANSION / HOLD / REDUCTION

| Mode | Behavior |
|------|----------|
| EXPANSION | --hard or --two mode, explore alternatives, stretch goals ok |
| HOLD | auto-detected mode, focus edge cases, test coverage |
| REDUCTION | --fast mode, minimal version, defer non-critical |

**Once selected, RESPECT IT.** No silent scope changes.
