# Generic Use Case Metrics — {Module or Scope}

## 1. Document Info

| Field | Value |
| --- | --- |
| Document ID | `UC-MET-{NNN}` |
| Scope | `{Module / Feature / Service}` |
| Version | `v0.1` |
| Created | `{YYYY-MM-DD}` |
| Owner | `{Name}` |
| Status | `{Draft / Review / Approved}` |

---

## 2. Coverage Summary

| Metric | Value | Target | Notes |
| --- | --- | --- | --- |
| Use cases discovered | `{n}` | `{n}` | `{summary}` |
| Entry points covered | `{n}` | `{n}` | `{summary}` |
| High-risk flows covered | `{n}` | `{n}` | `{summary}` |
| Error paths covered | `{n}` | `{n}` | `{summary}` |
| IPC / integration paths covered | `{n}` | `{n}` | `{summary}` |

---

## 3. Risk Distribution

| Risk level | Count | Notes |
| --- | --- | --- |
| HIGH | `{n}` | `{money / auth / integration / data loss}` |
| MEDIUM | `{n}` | `{shared logic / cross-module flows}` |
| LOW | `{n}` | `{local / internal only}` |

---

## 4. Annotation Taxonomy

| Category | Values |
| --- | --- |
| ROLE | ENTRYPOINT, CONTROLLER, SERVICE, REPOSITORY, ADAPTER, UTILITY |
| FLOW | MAIN, ALT, ERROR, TIMEOUT, RETRY |
| LAYER | UI, DOMAIN, INFRA, INTEGRATION |
| STATE | MUTATES, PURE, CACHE, I/O |
| SYNC | SYNC, ASYNC, CALLBACK, INTERRUPT |

---

## 5. Dependency Overview

| Target | Direct calls | Indirect paths | IPC | Notes |
| --- | --- | --- | --- | --- |
| `{ModuleA}` | `{n}` | `{n}` | `{n}` | `{summary}` |

---

## 6. Quality Gates

- [ ] All primary entry points mapped
- [ ] High-risk flows documented
- [ ] Error paths identified
- [ ] Duplicate UCs merged
- [ ] Unclear flows flagged for manual review
- [ ] Metrics values are traceable to artifacts

---

## 7. Next Priorities

1. `{Top priority use case or flow}`
2. `{Second priority use case or flow}`
3. `{Third priority use case or flow}`
