# Quality Gates

Use these gates before marking the package as complete.

## 1. Baseline Gate

- [ ] Module inventory exists.
- [ ] Function baseline captured.
- [ ] Entry-point baseline captured.
- [ ] IPC baseline captured (send + receive view).

## 2. Use Case Gate

- [ ] `usecase_list_<module>.md` completed.
- [ ] Every primary UC has:
  - [ ] entry point
  - [ ] main flow
  - [ ] alt/error flow or explicit N/A reason
  - [ ] sequence diagram
  - [ ] class diagram (if class domain is relevant)
- [ ] High-risk nodes tagged.

## 3. Coverage Thresholds

Default target thresholds:

- `ENTRY_COVERAGE >= 0.90`
- `FUNCTION_COVERAGE >= 0.60`
- `ERROR_PATH_COVERAGE >= 0.70`
- `IPC_COVERAGE >= 0.90`

If thresholds are not met, add explicit gap items and recovery actions.

## 4. Detail Design Gate

- [ ] Screen design linked to actors/triggers.
- [ ] API process design linked to main + alt/error flows.
- [ ] OpenAPI aligns with API process design.
- [ ] Table and SQL design align with entity and state transitions.
- [ ] Batch design included when batch flows exist.

## 5. Review and Release Gate

- [ ] UC status moved to `Reviewed` or `Approved`.
- [ ] Version and date metadata updated.
- [ ] Trace evidence file updated with unresolved points.
- [ ] No undocumented `RISK=HIGH` behavior remains.
