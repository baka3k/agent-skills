---
name: bid-staffing-planner
description: Generate phase-based staffing plans for software bidding using default effort ratios across Discovery, Foundation, Build, Stabilize/UAT, and Go-live/Hypercare.
version: 1.1.0
last_updated: 2026-05-05
hooks:
  pre:
    - name: input-validation
      scope: [effort_estimate, rate_card]
      validate:
        - file_exists
        - file_readable
        - json_valid
      enable_redaction: true
  phase:
    staffing_calculation:
      post: [progress-reporter]
    ratio_validation:
      post: [staffing-ratio-check]
  post:
    - name: output-redaction
      apply_to: [staffing_plan, role_rates]
    - name: cleanup-handler
      paths: [staffing-data/]
      keep: [*.json, *.md]
---

# Bid Staffing Planner

Generate role allocation and phase allocation from total effort.

## Phase Framework

- Discovery: 10-15%
- Foundation/Architecture: 15-20%
- Build: 45-55%
- Stabilize/UAT: 15-20%
- Go-live/Hypercare: 5-10%

## Output

- PM allocation by phase.
- Role-level PM allocation.
- Staffing narrative for delivery waves.

## Script

```bash
python bid-staffing-planner/scripts/build_staffing_plan.py --base-pm 30 --timeline "6 months"
```
