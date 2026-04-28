# Bug Severity Classification Matrix

Framework for classifying bug severity based on impact, reach, and risk factors.

## Severity Levels

### Critical (P0)
**Definition**: System-breaking or security-critical issue requiring immediate fix.

**Criteria** (ANY of these):
- Data corruption or data loss
- Security vulnerability exploitable in production
- Complete service or system outage
- Critical business impact (revenue, compliance, legal)
- No workaround available

**Examples**:
- Database connection pool exhausted causing total outage
- Authentication bypass allowing unauthorized access
- Payment processing failure preventing transactions
- Data deletion bug causing permanent loss

**SLA**: Fix within [24] hours, hotfix if needed

---

### High (P1)
**Definition**: Major feature broken or significant user impact.

**Criteria** (ANY of these):
- Major feature completely non-functional
- Significant performance degradation (>50% slowdown)
- User data at risk (but not corrupted yet)
- High-visibility UI/UX issue
- Workaround available but difficult or time-consuming

**Examples**:
- Search function returns no results
- Checkout process fails for 30% of users
- Page load times increased by 3x
- Critical button not working on mobile devices

**SLA**: Fix within [1 week], plan next release if needed

---

### Medium (P2)
**Definition**: Partial feature degradation or moderate user impact.

**Criteria** (ANY of these):
- Feature works but with bugs in edge cases
- Minor performance impact (<50% slowdown)
- UI/UX issue affecting specific scenarios
- Easy workaround available

**Examples**:
- Filter works but crashes on special characters
- Report generation fails for large datasets
- Button alignment issue on tablet resolution
- Feature works on Chrome but not Firefox

**SLA**: Fix within [1-2 sprints], backlog as needed

---

### Low (P3)
**Definition**: Cosmetic issue or minor inconvenience.

**Criteria** (ANY of these):
- Typos or text issues
- Visual styling problems
- Nice-to-have improvements
- No impact on functionality

**Examples**:
- Misspelled word in error message
- Color slightly off from design spec
- Missing hover effect on button
- Inconsistent spacing in layout

**SLA**: Fix when convenient, backlog for future

---

## Reach Assessment

### Reach Score Calculation

**Factors**:
1. **User Reach**: What % of users are affected?
   - All users: 3 points
   - Most users (50-90%): 2 points
   - Some users (10-50%): 1 point
   - Few users (<10%): 0 points

2. **Feature Visibility**: How visible is the affected feature?
   - Core/critical feature: 3 points
   - Frequently used feature: 2 points
   - Occasional feature: 1 point
   - Rare/edge case feature: 0 points

3. **Impact Breadth**: How many functions/flows are affected?
   - System-wide: 3 points
   - Multiple modules: 2 points
   - Single module: 1 point
   - Single function: 0 points

**Reach Score** = Sum of factors (0-9)

**Reach Categories**:
- 7-9: Critical reach
- 4-6: High reach
- 2-3: Medium reach
- 0-1: Low reach

---

## Risk Factors

### Risk Multipliers

Apply these to adjust severity based on context:

| Risk Factor | Multiplier | When to Apply |
|-------------|-----------|---------------|
| Production-only bug | ×2 | Bug exists in prod but not dev/staging |
| Security-related | ×2 | Any security implication |
| Compliance/legal | ×2 | Regulatory impact |
- High-traffic period | ×1.5 | During peak usage or events |
- No monitoring | ×1.5 | No alerts would fire if this worsens |
- Poor test coverage | ×1.5 | High regression risk |
- Complex fix | ×1.5 | Fix requires significant changes |
- Distributed system | ×1.5 | Impact could cascade |

### Risk Reducers

Apply these to potentially reduce severity:

| Risk Reducer | Multiplier | When to Apply |
|--------------|-----------|---------------|
| Easy workaround | ×0.5 | Simple alternative for users |
| Behind feature flag | ×0.5 | Can be disabled instantly |
| Excellent monitoring | ×0.7 | Would be detected immediately |
| Comprehensive tests | ×0.7 | Low regression risk |
- Simple fix | ×0.7 | One-line change, well-understood |

---

## Severity Determination Algorithm

```
BASE_SEVERITY = Determine from bug characteristics
REACH_SCORE = Calculate from user/feature/breadth factors
RISK_MULTIPLIER = Apply multipliers and reducers

ADJUSTED_SEVERITY = BASE_SEVERITY × RISK_MULTIPLIER

If REACH_SCORE >= 7:
    Consider bumping severity one level
If REACH_SCORE <= 1:
    Consider dropping severity one level

Final severity = ADJUSTED_SEVERITY with reach adjustment
```

---

## Special Cases

### Security Bugs
Always start at High severity, then:
- Elevate to Critical if exploitable in production
- Keep at High if exploitable but requires specific conditions
- Downgrade to Medium if theoretical only

### Performance Bugs
Assess severity based on degradation:
- >90% slowdown: Critical
- 50-90% slowdown: High
- 20-50% slowdown: Medium
- <20% slowdown: Low

Then apply reach multiplier.

### Data-Related Bugs
Assess severity based on data impact:
- Data loss/corruption: Critical
- Data inconsistency: High
- Data display issues: Medium
- Data formatting issues: Low

### Regression Bugs
New bugs introduced by recent changes:
- Severity based on impact as usual
- Add note: "Regression from [commit/PR]"
- Consider prioritizing higher due to freshness

---

## Severity Escalation/De-escalation

### When to Escalate
- New information reveals wider impact
- User complaints increase significantly
- Workaround proves ineffective
- Related issues discovered

### When to De-escalate
- Impact is smaller than initially assessed
- Easy workaround discovered
- Bug is hard to reproduce
- Affects deprecated/unused code

Always document the reason for severity changes.
