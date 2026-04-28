# Use Case to Detail Design Map

Use this mapping after UC files are reviewed.

## 1. Input Set

Mandatory UC sources:

- `usecase_list_<module>.md`
- `ucXXX_<module>.md`
- `usecase_metrics_<module>.md`
- related sequence/class diagrams

## 2. Mapping Matrix

| UC evidence | Target document | Required transfer |
| --- | --- | --- |
| Actors + entry points | `screen_design_<module>.md` | screen triggers, event handlers, role-specific flows |
| Main flow steps | `api_process_design_<module>.md` | processing flow, request/response stages, success flow |
| Alt/error flows | `api_process_design_<module>.md` | error code matrix, timeout/retry strategy |
| Critical checkpoints | `api_process_design_<module>.md` | auth, validation, security, performance sections |
| Domain entities + data fields | `table_design_<module>.md` | table columns, constraints, index candidates |
| Query and state transitions | `sql_design_<module>.md` | SQL operations and where-clause logic |
| API request/response shape | `openapi_spec_<module>.yaml` | schema properties, required fields, response models |
| Batch-oriented UC branches | `batch_process_design_<module>.md` | triggers, schedules, retry/rollback behavior |

## 3. Transformation Sequence

1. Lock UC versions (`Reviewed` minimum).
2. Extract stable field inventory:
   - inputs, outputs, identifiers, status transitions.
3. Build table design first.
4. Build SQL design from table design plus UC flow predicates.
5. Build API process design from main + alt/error flow.
6. Derive OpenAPI spec from API process design.
7. Build screen and batch designs from actors and trigger models.
8. Reconcile naming across all files.

## 4. Consistency Checks

Run these checks before publishing:

- Every API field exists in either UC field list or derived business rule.
- Every SQL filter condition maps to a documented input.
- Every high-risk UC checkpoint appears in design docs.
- Every diagram participant maps to a defined component/module.

## 5. Anti-Patterns

- Do not create APIs that are not backed by UC flows.
- Do not introduce tables without traceable entity evidence.
- Do not mark success paths without documenting rollback or error behavior for high-risk operations.
