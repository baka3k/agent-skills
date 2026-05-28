# Review Cycle

## Autonomous Mode
1. Run code-reviewer -> score, critical_count, warnings
2. IF score>=9.5 AND critical=0 -> auto-approve, proceed
3. IF critical>0 AND cycle<3 -> auto-fix critical, re-test, loop
4. IF cycle>=3 -> escalate to user
5. IF no critical, score<9.5 -> approve with warnings logged

## Human-in-the-Loop Mode
1. Run code-reviewer -> score, critical_count, warnings, suggestions
2. Display findings with score, critical, warnings, suggestions
3. AskUserQuestion:
   IF critical>0: "Fix critical" / "Fix all" / "Approve anyway" / "Abort"
   ELSE: "Approve" / "Fix warnings/suggestions" / "Abort"
4. Fix -> re-test -> re-review (max 3 cycles)
   Approve -> proceed
   Abort -> stop

## Quick Mode
Lower threshold: score>=8.5 acceptable. Only 1 auto-fix cycle before escalate.
Focus: correctness, security, no regressions.

## Critical Issues (Always Block)
Security (XSS, SQLi, OWASP) | Performance (O(n^2) where O(n) possible) |
Architecture violations | Data loss risks | Breaking changes without migration
