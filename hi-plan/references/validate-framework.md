# Plan Validation Framework

Critical questions interview to stress-test plan assumptions before execution.

## Validation Questions

### Completeness
1. Is every phase's success criteria measurable and verifiable?
2. Are all dependencies explicitly identified with owners?
3. Does the plan cover error states and failure modes?

### Feasibility
4. Is the effort estimate calibrated against similar past work?
5. Does the team have the skills required for each phase?
6. Are external dependencies available when needed?

### Quality
7. Are architectural decisions documented with rationale?
8. Are security implications addressed for each component?
9. Is test strategy defined for each phase?

### Recovery
10. What is the rollback strategy if phase N fails?
11. Can the plan be paused and resumed mid-execution?
12. What is the minimum viable outcome if we must stop early?

## Validation Verdict

- **READY** — All questions adequately addressed
- **READY WITH NOTES** — Minor clarifications added, proceed
- **NOT READY** — Critical gaps, return to design phase
