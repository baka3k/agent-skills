---
name: bid-solution-designer
description: Design two software delivery solution options for bidding (baseline and optimized), including architecture direction, tradeoffs, and cost-quality-timeline impacts.
version: 1.1.0
last_updated: 2026-05-05
hooks:
  pre:
    - name: mcp-health-check
      timeout: 10s
    - name: input-validation
      scope: [bid_brief, requirements]
      enable_redaction: true
  phase:
    architecture_analysis:
      pre: [mcp-health-check]
      post: [progress-reporter]
    solution_design:
      post: [progress-reporter, solution-completeness-check]
    tradeoff_analysis:
      post: [progress-reporter]
  post:
    - name: output-redaction
      apply_to: [solution_options, tradeoff_analysis]
    - name: cleanup-handler
      paths: [solution-data/]
      keep: [*.json, *.md, *.pptx]
---

# Bid Solution Designer

Produce two explicit solution options from the same scope.

## Required Outputs

- Option A: Baseline delivery plan.
- Option B: Optimized plan (faster or higher quality or lower risk).
- Tradeoff matrix across cost, timeline, quality, and operational risk.

## Design Contract

- Keep the same in-scope boundary between options.
- Explain what changes in staffing, architecture, or sequencing.
- Attach assumptions and dependencies for each option.
