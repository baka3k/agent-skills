# Bug Impact Analysis Report

**Bug ID/Reference**: [issue link or identifier]
**Analysis Date**: [YYYY-MM-DD]
**Repository**: [repo name/path]
**Analysis Scope**: [local/module/system/full]

---

## Executive Summary

**Severity**: [Critical/High/Medium/Low]
**Reach Score**: [0-10 scale]
**Overall Risk**: [Critical/High/Medium/Low]
**Recommended Priority**: [P0/P1/P2/P3]

**One-paragraph summary** of the bug, its impact, and recommended action.

---

## Bug Description

### Location
- **File**: `path/to/file.ext`
- **Function/Class**: `function_name` or `ClassName`
- **Lines**: [start-end]

### Bug Type
- [ ] Logic Error
- [ ] Null/Undefined Reference
- [ ] Race Condition
- [ ] Resource Leak
- [ ] Security Vulnerability
- [ ] Performance Issue
- [ ] Data Corruption
- [ ] Integration Failure
- [ ] Other: _______________

### Reproduction Steps
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**: What should happen
**Actual Behavior**: What actually happens

---

## Impact Analysis

### Direct Impact
**Modules Affected**:
| Module | Impact Type | Severity | Evidence |
|--------|-------------|----------|----------|
| module_a | Data corruption | High | graph_mcp trace #1 |
| module_b | Feature broken | Medium | mind_mcp doc #2 |

### Upstream Callers
**Direct Callers** (count: N):
- `caller_function_1` in `module/path1.ext` - [usage context]
- `caller_function_2` in `module/path2.ext` - [usage context]

**Indirect Callers** (count: N):
- Total reach: X functions across Y modules

### Downstream Dependencies
**Direct Dependencies**:
- `dependency_1` - [impact description]
- `dependency_2` - [impact description]

**Cascading Effects**:
- [Effect 1]
- [Effect 2]

### Data Flow Impact
**Data Streams Affected**:
- Stream 1: [source] → [bug location] → [destination]
- Stream 2: [source] → [bug location] → [destination]

**Data Types**: [list affected data structures/types]

### Integration Boundaries
**External APIs Affected**:
- API endpoint: [impact description]

**Service Boundaries**:
- Service X → Service Y: [impact description]

**User-Facing Impact**:
- Features broken: [list]
- Features degraded: [list]
- UX issues: [describe]

---

## Risk Assessment

### Severity Justification
**Score**: [Critical/High/Medium/Low]

**Justification**:
- Data integrity impact: [describe]
- User experience impact: [describe]
- Business impact: [describe]
- Security implications: [describe]

### Reach Metrics
| Metric | Value | Risk Level |
|--------|-------|------------|
| Direct callers affected | N | High/Med/Low |
| Indirect callers affected | N | High/Med/Low |
| Modules impacted | N | High/Med/Low |
| Data flows disrupted | N | High/Med/Low |
| External integrations | N | High/Med/Low |
| User-facing features | N | High/Med/Low |

**Reach Score**: [X/10]

### Regression Risk
**Probability of Regression**: [High/Medium/Low]

**Factors**:
- Code coupling in impact zone: [assess]
- Test coverage quality: [assess]
- Dependency complexity: [assess]
- Required coordination: [assess]

---

## Fix Recommendations

### Proposed Fix
**Approach**: [describe the fix approach]

**Implementation Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Code Changes Required**:
- `file/path1.ext`: [description of changes]
- `file/path2.ext`: [description of changes]

### Alternative Approaches
**Option 2**: [describe alternative]
**Pros**: [advantages]
**Cons**: [disadvantages]
**When to use**: [criteria]

### Test Strategy
**Unit Tests Required**:
- [ ] Test case 1: [description]
- [ ] Test case 2: [description]

**Integration Tests Required**:
- [ ] Test scenario 1: [description]
- [ ] Test scenario 2: [description]

**Regression Tests Required**:
- [ ] Test area 1: [description]
- [ ] Test area 2: [description]

**Test Coverage Target**: [X%]

### Rollback Plan
**Rollback Strategy**: [describe rollback approach]
**Rollback Risk**: [High/Medium/Low]
**Rollback Steps**:
1. [Step 1]
2. [Step 2]

---

## Evidence and Confidence

### mind_mcp Evidence
| Query | Result | Confidence | Impact |
|-------|--------|------------|--------|
| [query 1] | [finding] | High/Med/Low | [how used] |
| [query 2] | [finding] | High/Med/Low | [how used] |

### graph_mcp Evidence
| Trace | Path | Depth | Centrality | Impact |
|-------|------|-------|------------|--------|
| [trace 1] | [path description] | N | score | [how used] |
| [trace 2] | [path description] | N | score | [how used] |

### Confidence Levels
- **Bug location confidence**: [High/Medium/Low]
- **Impact scope confidence**: [High/Medium/Low]
- **Severity confidence**: [High/Medium/Low]
- **Fix complexity confidence**: [High/Medium/Low]

---

## Open Questions and Assumptions

### Open Questions
- [Question 1]
- [Question 2]

### Assumptions Made
- [Assumption 1]
- [Assumption 2]

### Recommended Follow-up
- [Action 1]
- [Action 2]

---

## Appendix

### Related Issues
- Issue #X: [related problem]
- PR #Y: [related fix]

### Historical Context
- [Historical notes from mind_mcp]

### Documentation References
- [Doc link 1]
- [Doc link 2]
