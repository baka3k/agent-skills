---
name: bid-evidence-hub
description: Aggregate and normalize evidence for software bidding from mind_mcp, graph_mcp, and trusted internet sources, then emit confidence-ready evidence logs with citations.
version: 1.0.0
last_updated: 2026-04-26
---

# Bid Evidence Hub

Collect evidence in a source-priority model and produce a traceable evidence log.

## Source Priority

1. `mind_mcp` for domain and project intent.
2. `graph_mcp` for code structure and dependency impact.
3. Trusted internet baselines for standards and benchmarks.

## Required Inputs

- `mind_source_ids[]`
- `graph_project_ids[]`
- `internet_domains_allowlist[]`

## Output

- Normalized evidence list with: `source_type`, `source_id`, `claim`, `citation`, `confidence_weight`, `timestamp`.

## Rules

- Downgrade confidence if one or more channels are unavailable.
- Do not emit uncited quantitative claims.
- Redact sensitive values from notes and snippets.
