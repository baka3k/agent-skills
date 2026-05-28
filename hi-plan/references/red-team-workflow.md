# Red Team Review

Adversarial plan review. Spawn hostile reviewers to tear apart the plan.

## Step 1: Read Plan
Read plan.md + all phase-*.md files.

## Step 2: Scale Reviewers
| Phase Count | Reviewers | Lenses |
|-------------|-----------|--------|
| 1-2 | 2 | Security + Assumptions |
| 3-5 | 3 | + Failure Modes |
| 6+ | 4 | + Scope/Complexity |

## Step 3: Spawn Reviewers
Launch code-reviewer agents with hostile prompts:
- Security Adversary: find injection, auth bypass, data exposure
- Assumption Destroyer: challenge every stated assumption
- Failure Mode Analyst: what breaks in prod?
- Scope/Complexity Critic: is this over-engineered?

## Step 4: Collect & Adjudicate
1. Collect all findings
2. Deduplicate overlapping
3. Sort: Critical -> High -> Medium
4. Cap at 15 findings
5. Propose Accept/Reject per finding

## Step 5: User Review
Present findings. Options: "Apply all accepted" / "Review each" / "Reject all"

## Step 6: Apply
Edit phase files inline. Add ## Red Team Review section to plan.md.

## Output
- Findings by severity
- Accepted vs rejected count
- Files modified
