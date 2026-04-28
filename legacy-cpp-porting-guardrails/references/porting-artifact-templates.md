# Porting Artifact Templates

Use these templates to keep large-function migration auditable and reversible.

## 1) Function Behavior Contract

```markdown
# Contract: <function-name>

## Signature
- Legacy: `<signature>`
- Target: `<signature>`

## Inputs
- Required params:
- Optional params:
- Accepted ranges/formats:

## Outputs
- Return/status code mapping:
- Output payload shape:

## Side Effects
- Files touched:
- Global/static state touched:
- External dependencies:

## Invariants
- Must always hold:

## Error and Edge Cases
- Empty/null handling:
- Boundary numeric values:
- Invalid state behavior:

## Open Risks
- Unknown legacy intent:
- Unverified branches:
```

## 2) Parity Case Matrix

```markdown
# Parity Cases: <function-name>

| Case ID | Input | Expected Legacy Output | Expected Side Effect | Port Output | Match |
| --- | --- | --- | --- | --- | --- |
| C01 | ... | ... | ... | ... | ✅/❌ |
| C02 | ... | ... | ... | ... | ✅/❌ |
```

## 3) Migration Ledger Entry

```markdown
# Ledger: <date> <slice-id>

- Function:
- Slice scope:
- Files changed:
- Legacy behavior touched:
- Parity result:
- Regression result:
- Known deviations:
- Decision:
  - [ ] Keep as-is (legacy compatibility)
  - [ ] Intentional change with approval
```

## 4) Slice Planning Rules

- Keep each slice small enough to review in one pass.
- Prefer semantic slices (validation branch, IO branch, calculation branch), not raw line ranges.
- Never merge two high-risk slices (e.g., IO + error protocol) into one change.
- Add one new targeted regression test per closed bug/parity mismatch.
