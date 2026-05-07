---
name: bid-slide-factory
description: Build bidding presentation decks from proposal artifacts using the Presentations skill and Gemini image generation adapter with fallback behavior when API or model checks fail.
version: 1.1.0
last_updated: 2026-05-05
hooks:
  pre:
    - name: input-validation
      scope: [proposal_artifacts, slide_config]
      enable_redaction: true
  phase:
    slide_generation:
      pre: [timeout-handler]
      post: [progress-reporter]
    image_generation:
      post: [progress-reporter]
  post:
    - name: cleanup-handler
      paths: [slide-output/, temp-images/]
      keep: [*.pptx, *.pdf, final-deck.zip]
    - name: metrics-report
      include: [slide_count, generation_time, image_api_status]
---

# Bid Slide Factory

Create a proposal-ready deck with citations and fallback image handling.

## Core Behavior

- Build slide brief from proposal, estimate, staffing, quality gates, and evidence logs.
- Use `$presentations` for deck authoring when available.
- Use Gemini image generation adapter for visuals.
- If Gemini model check or generation fails, use placeholder/stock-safe fallback and continue.

## Model Availability Rule

Do not hardcode one Gemini model. Check model availability first using:

- Gemini models docs
- Gemini changelog
- Optional API model listing if API key is configured

## Script

```bash
python bid-slide-factory/scripts/resolve_gemini_model.py

python bid-slide-factory/scripts/build_slide_brief.py \
  --proposal outputs/proposal/proposal.md \
  --estimate outputs/estimate/estimate_summary.json \
  --staffing outputs/staffing/staffing_plan.md \
  --quality outputs/quality/quality_gates.md \
  --evidence outputs/evidence/evidence_log.json
```
