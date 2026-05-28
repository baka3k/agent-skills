# Plan Organization

## Directory Structure
Create under CURRENT WORKING PROJECT DIRECTORY.
```
{plan-dir}/
├── plan.md
├── phase-01-name.md
└── phase-02-name.md
```

## plan.md Structure
```markdown
---
title: "Brief title"
status: pending
priority: P2
effort: 4h
tags: [feature, frontend]
blockedBy: []
blocks: []
created: YYYY-MM-DD
---

# Plan

## Overview
Brief description.

## Phases
| Phase | Name | Status |
|-------|------|--------|
| 1 | [Setup](./phase-01-name.md) | Pending |
```

Keep plan.md under 80 lines.

## Phase File Structure
- Context links (related files, docs)
- Overview: priority, status, description
- Key insights from research
- Requirements: functional + non-functional
- Architecture: design, components, data flow
- Related code: create/modify/delete
- Implementation steps: numbered, specific
- Success criteria: definition of done
- Risk assessment: potential issues, mitigation
