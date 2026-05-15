# Generic Use Case Discovery Guide — {Module or Scope}

## 1. Document Info

| Field | Value |
| --- | --- |
| Document ID | `UC-DISC-{NNN}` |
| Scope | `{Module / Feature / Service}` |
| Version | `v0.1` |
| Created | `{YYYY-MM-DD}` |
| Owner | `{Name}` |
| Status | `{Draft / Review / Approved}` |

---

## 2. Purpose

- Discover candidate use cases from source code, flows, and runtime interactions.
- Keep the output small, reviewable, and traceable.
- Avoid dumping raw data; summarize first, expand later only when needed.

---

## 3. Inputs

| Input | Description |
| --- | --- |
| Scope hint | `{module / feature / folder / service}` |
| Source signals | Entry points, handlers, lifecycle functions, IPC, config, keywords |
| Constraints | `{batch size, max depth, output path, validation rules}` |

---

## 4. Discovery Strategy

### 4.1 Breadth scan
- Find entry points, handlers, and high-degree nodes.
- Record only short summaries for each candidate.

### 4.2 Keyword scan
- Search for business/domain terms, feature names, and data objects.
- Merge duplicates by intent, not by literal name.

### 4.3 Path validation
- Trace from entry points to key downstream nodes.
- If no direct call path exists, inspect IPC or message-based communication.

### 4.4 Controlled expansion
- Use node IDs for follow-up reads.
- Split large result sets into batches.
- Ask for confirmation before deepening scope.

---

## 5. Output Structure

### 5.1 Summary
- Total functions analyzed
- Entry points found
- UC candidates discovered
- High-risk candidates

### 5.2 UC list
For each candidate use case, capture:
- UC ID and name
- Trigger / actor
- Entry point(s)
- Main flow summary
- Alternate / error flow summary
- Risk level
- Dependencies and related modules
- Notes and follow-up questions

### 5.3 IPC and dependency map
- Module-to-module paths
- IPC message groups
- Shared state or external integration points

### 5.4 Coverage checklist
- Entry points mapped
- High-risk flows covered
- Error paths identified
- Duplicate candidates merged
- Gaps needing manual review

---

## 6. Guardrails

- Do not print raw JSON or large code bodies unless explicitly needed.
- Prefer summaries over full detail.
- Keep per-batch processing bounded.
- Use node IDs for follow-up expansion.
- Stop and ask before broadening scope beyond the agreed boundary.

---

## 7. Report Template

```markdown
## Discovery Summary
- Scope: {scope}
- Entry points: {n}
- UC candidates: {n}
- High risk: {n}

## Candidates
### UC-001: {name}
- Trigger: {actor/action}
- Entry point: {symbol}
- Risk: {HIGH/MEDIUM/LOW}
- Dependencies: {modules or IPC}
- Notes: {summary}
```
