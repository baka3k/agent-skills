# API Warning Rules

Use these rules to generate architecture warnings around API dependency boundaries.

## Rule W1: API Direct Driver Access

Condition:
- API/controller/handler code imports low-level DB driver, and
- same file (or immediate call path) performs direct query/execute/connect operations.

Severity:
- `high` when both import and operation are observed.
- `medium` when only driver import is observed.

Why it matters:
- Bypasses service/repository abstraction.
- Makes transport layer tightly coupled to persistence details.

## Rule W2: Service Layer Framework Coupling

Condition:
- Service/domain/usecase layer imports web framework symbols.

Severity:
- `medium`.

Why it matters:
- Business logic becomes framework-dependent.
- Harder to test and migrate frameworks.

## Rule W3: Controller-to-Driver Call Path (graph_mcp)

Condition:
- A call path exists from API entry function to driver symbol,
- and no intermediate service/repository abstraction node is observed.

Severity:
- `high`.

Why it matters:
- Indicates architectural boundary violation in runtime flow.

## Required Warning Payload

Each warning should include:
- `warning_id`
- `severity`
- `path` or node/function id
- short `title`
- `evidence` (matched patterns or graph path refs)
- `recommendation`
