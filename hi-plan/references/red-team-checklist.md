# Red Team Review Checklist

Adversarial review of plan weaknesses before execution.

## Core Questions

1. What assumption, if wrong, breaks this plan entirely?
2. What is the simplest alternative that was NOT considered?
3. What happens if every phase takes 3x the estimated time?
4. What external dependency is most likely to fail mid-plan?
5. How does this interact with other in-progress work?
6. What is the rollback strategy if this fails at phase N?
7. What knowledge gap does the team have that this plan depends on?
8. If this were a post-mortem of a failed project, what would the root cause be?

## Attack Vectors

| Vector | Challenge |
|--------|-----------|
| Scope Creep | What feature requests are likely to expand scope mid-plan? |
| Dependency Hell | What internal/external dependency is the weakest link? |
| Skill Gap | What skill does the plan assume that the team may lack? |
| Integration Risk | What integration point is least tested or documented? |
| Data Migration | What data migration could silently corrupt data? |
| Performance Cliff | At what scale does the design stop working? |

## Red Team Verdict

- **PASS** — No critical flaws found, risks have mitigations
- **CONDITIONAL PASS** — Minor concerns, specific mitigations added to plan
- **FAIL** — Critical flaw found, plan needs redesign before execution
