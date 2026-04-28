---
name: bid-estimator
description: Compute hybrid software bid estimates with best/base/worst person-month ranges and fixed-price/T&M cost ranges using WBS complexity multipliers and capped risk buffers.
version: 1.0.0
last_updated: 2026-04-26
---

# Bid Estimator

Estimate effort and cost ranges using deterministic formulas.

## Formula Contract

- Complexity multiplier: `low=0.85`, `medium=1.0`, `high=1.25`
- Risk buffer from unknowns (integration, data migration, NFR), capped at `30%`
- Effort range: `best=0.85*base`, `worst=1.30*base`
- Fixed-price: `base_pm * blended_monthly_rate * 1.15`
- T&M: `sum(role_pm * role_monthly_rate)`

## Script

```bash
python bid-estimator/scripts/calc_estimate.py \
  --wbs-json bid-estimator/references/wbs.sample.json \
  --rate-card bidding-orchestrator/examples/rate_card.sample.yaml
```
