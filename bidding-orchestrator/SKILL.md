---
name: bidding-orchestrator
description: Orchestrate end-to-end software project bidding packages in hybrid mode (fixed-price + T&M) by coordinating evidence retrieval, solution design, quality gates, estimation, staffing plans, and slide deck generation.
version: 1.0.0
last_updated: 2026-04-26
---

# Bidding Orchestrator

Run a complete bidding pipeline from intake contracts to final proposal package.

## When To Use

- You need a complete bid package with effort range, cost range, staffing, and slides.
- You need both fixed-price and T&M scenarios from one source of truth.
- You need confidence and citations tied to MCP evidence and trusted web sources.

## Required Inputs

- `contracts/bid_brief.yaml`
- `contracts/evidence_config.yaml`
- Optional `contracts/rate_card.yaml`

## Output Contract

- `outputs/proposal/proposal.md`
- `outputs/estimate/estimate_summary.json`
- `outputs/staffing/staffing_plan.md`
- `outputs/quality/quality_gates.md`
- `outputs/evidence/evidence_log.json`
- `outputs/slides/bid_deck.pptx` (or markdown fallback when PPTX tooling is unavailable)

## Orchestration Workflow

1. Validate contract files and required fields.
2. Collect evidence through `$bid-evidence-hub` using `mind_mcp`, `graph_mcp`, and trusted internet sources.
3. Build two solution options using `$bid-solution-designer`.
4. Compute estimation ranges using `$bid-estimator`.
5. Build staffing plan by phase using `$bid-staffing-planner`.
6. Apply lifecycle quality gates using `$bid-quality-gates`.
7. Generate proposal artifacts and slides with `$bid-slide-factory`.
8. Emit confidence tier and assumption log.

## Execution

Run:

```bash
python bidding-orchestrator/scripts/generate_bid_package.py \
  --bid-brief bidding-orchestrator/examples/bid_brief.sample.yaml \
  --evidence-config bidding-orchestrator/examples/evidence_config.sample.yaml \
  --rate-card bidding-orchestrator/examples/rate_card.sample.yaml \
  --output-dir outputs
```

## Guardrails

- Prefer MCP evidence over assumptions.
- If `rate_card.yaml` is missing, still produce effort and timeline, and mark cost as `pending`.
- Do not make quantitative claims without either citation or explicit `assumption` flag.
- Keep default language as English unless the brief explicitly overrides it.
