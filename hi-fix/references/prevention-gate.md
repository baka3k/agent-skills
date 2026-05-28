# Prevention Gate

A fix without prevention is incomplete. The same bug WILL recur.

## Requirements

### 1. Regression Test (ALWAYS)
Every fix MUST have a test that fails without the fix, passes with it.

### 2. Defense-in-Depth (consider each)
- Entry point: reject invalid at API boundary
- Business logic: assert data makes sense
- Environment: guard dangerous operations
- Debug: add logging for hard-to-diagnose

### 3. Type Safety
Null/undefined -> strict null checks, ?? or ?.
Wrong type -> type guard or runtime validation.
Missing property -> required field in interface.

### 4. Error Handling
Unhandled promise -> .catch() or try/catch.
Silent failure -> explicit error logging.
No fallback -> timeout + fallback.

## Verification Checklist
- [ ] Pre-fix state captured?
- [ ] Fix at ROOT CAUSE (not symptom)?
- [ ] Same commands before/after comparison?
- [ ] Regression test added?
- [ ] Defense-in-depth considered?
- [ ] No new warnings?
