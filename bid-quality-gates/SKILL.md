---
name: bid-quality-gates
description: Apply proposal lifecycle quality gates for software bidding, covering scope clarity, architecture readiness, estimation confidence, delivery readiness, and production readiness.
version: 1.0.0
last_updated: 2026-04-26
---

# Bid Quality Gates

Run deterministic quality gates before bid submission.

## Gate Set

- Scope clarity
- Architecture readiness
- Estimation confidence
- Delivery readiness
- Production readiness

## Output

For each gate emit:

- `status`: pass/warn/fail
- `evidence`
- `risk_if_failed`
- `mitigation_action`

## Rule

Any `fail` gate requires explicit mitigation in proposal assumptions.
