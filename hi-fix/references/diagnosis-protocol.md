# Diagnosis Protocol

NEVER guess. Form hypotheses through structured reasoning, test against evidence.

## Capture State (MANDATORY)
Record: exact error, stack trace, log snippets, git log --oneline -10.

## Diagnosis Chain

### Phase 1: Observe
What is the exact error? Where (file, line)? When did it start?
Activate hi:debug (systematic-debugging).

### Phase 2: Hypothesize
For each hypothesis: What CONFIRMS it? REFUTES it? How to test?
Common: recent regression, data/state mismatch, env difference, missing validation.

### Phase 3: Test (parallel)
2-3 Explore agents simultaneously to test hypotheses.
Result: CONFIRMED / REFUTED / INCONCLUSIVE.

### Phase 4: Trace Root Cause
Trace backward: Symptom -> Immediate cause -> Contributing factor -> ROOT CAUSE.
NEVER fix where the error appears. Fix the source.

### Phase 5: Escalate
2+ hypotheses refuted -> activate hi:problem-solving.
3+ fix attempts fail -> STOP, question architecture with user.

## Diagnosis Report
**Issue:** [one-line]
**Root Cause:** [clear, traced to origin]
**Evidence Chain:** observation -> hypothesis -> test result
**Recommended Fix:** address root cause, not symptom
**Prevention:** guards/tests to prevent recurrence

## Quick Mode
Read error -> locate file -> identify root cause. Skip parallel hypothesis testing.
