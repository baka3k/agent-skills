# Dependency Tracing Patterns

Common patterns for tracing bug impact through code dependencies using graph_mcp.

## Pattern Categories

### 1. Call Graph Traversal

#### Forward Tracing (Downstream)
**Use case**: Understand what breaks when this function fails.

**Pattern**:
```
Start at bug location (function F)
For each outgoing call edge to function G:
  1. Record G as directly dependent
  2. Check if G is:
     - External API call (mark as integration point)
     - Database operation (mark as data impact)
     - State mutation (mark as side effect)
  3. Recursively trace G's outgoing calls
  4. Stop at module boundaries or max depth
```

**Implementation**:
```python
def trace_downstream(start_node, max_depth=5):
    impacted = set()
    integration_points = set()
    data_impacts = set()

    def trace(node, depth):
        if depth > max_depth:
            return
        for callee in get_outgoing_calls(node):
            impacted.add(callee)
            if is_external_call(callee):
                integration_points.add(callee)
            if is_database_operation(callee):
                data_impacts.add(callee)
            trace(callee, depth + 1)

    trace(start_node, 0)
    return impacted, integration_points, data_impacts
```

#### Backward Tracing (Upstream)
**Use case**: Understand who calls this buggy function.

**Pattern**:
```
Start at bug location (function F)
For each incoming call edge from function G:
  1. Record G as direct caller
  2. Check if G is:
     - API endpoint (mark as user-facing)
     - Scheduled job (mark as automated impact)
     - Public interface (mark as library impact)
  3. Recursively trace G's incoming calls
  4. Stop when centrality drops below threshold
```

**Implementation**:
```python
def trace_upstream(start_node, min_centrality=0.3):
    callers = set()
    user_facing = set()
    automated = set()

    def trace(node):
        for caller in get_incoming_calls(node):
            callers.add(caller)
            centrality = calculate_centrality(caller)
            if centrality < min_centrality:
                continue
            if is_api_endpoint(caller):
                user_facing.add(caller)
            if is_scheduled_job(caller):
                automated.add(caller)
            trace(caller)

    trace(start_node)
    return callers, user_facing, automated
```

### 2. Data Flow Tracing

#### Variable Flow Tracing
**Use case**: Track where corrupted/incorrect data propagates.

**Pattern**:
```
Start at bug location where variable V is corrupted
For each use of V:
  1. Record usage location
  2. If V is returned, track return value to caller
  3. If V is passed to function, track parameter
  4. If V is stored in struct/object, track object lifetime
  5. Stop at API boundaries or persistence
```

#### Object Lifetime Tracing
**Use case**: Understand resource management and lifecycle bugs.

**Pattern**:
```
Start at object creation site
Trace:
  - All method calls on the object
  - All assignments/references
  - Object destruction/cleanup
Check for:
  - Use-after-free patterns
  - Resource leaks
  - Double-free issues
```

### 3. Module Boundary Crossing

#### Integration Point Detection
**Use case**: Identify which external systems are affected.

**Pattern**:
```
During call graph traversal, flag:
  1. HTTP/HTTPS requests (check for external domains)
  2. RPC calls (check for external services)
  3. Queue operations (check for cross-system messaging)
  4. Database operations (check for shared data)
  5. File system operations (check for shared storage)
```

#### API Boundary Mapping
**Use case**: Map which API endpoints expose the bug.

**Pattern**:
```
For upstream caller analysis:
  1. Identify all HTTP route handlers
  2. Identify all GraphQL resolvers
  3. Identify all RPC service methods
  4. Trace from handler to bug location
  5. Record route/method + impact description
```

### 4. Centrality-Based Tracing

#### High-Centrality Focus
**Use case**: Prioritize impact on frequently used code.

**Pattern**:
```
During traversal, calculate centrality for each node:
  - PageRank centrality (importance in call graph)
  - Betweenness centrality (bridge between components)
  - Frequency centrality (how often called)

Prioritize:
  - High-centrality nodes (widely used functions)
  - High-betweenness nodes (integration points)
  - High-frequency nodes (hot paths)
```

#### Critical Path Identification
**Use case**: Find if bug is on critical execution path.

**Pattern**:
```
1. Identify main entry points (APIs, jobs, main functions)
2. For each entry point, trace to common operations
3. Check if bug location is on:
   - Happy path (normal execution flow)
   - Error path (exception handling)
   - Cleanup path (resource cleanup)
4. Prioritize happy path bugs highest
```

### 5. Test Coverage Intersection

#### Coverage Gap Analysis
**Use case**: Find impacted areas with poor test coverage.

**Pattern**:
```
1. Build impact set (all affected functions)
2. Query test coverage for each function
3. Calculate coverage score per function
4. Flag functions with:
   - High impact + Low coverage = HIGH RISK
   - High impact + Medium coverage = MEDIUM RISK
   - High impact + High coverage = LOWER RISK
```

#### Regression Risk Mapping
**Use case**: Estimate regression risk for fix.

**Pattern**:
```
For each impacted function:
  1. Check test coverage (unit, integration, e2e)
  2. Check code complexity (cyclomatic complexity)
  3. Check coupling (number of dependencies)
  4. Calculate regression risk:
     risk = complexity × coupling / coverage

Prioritize testing for high-risk functions.
```

### 6. Special Bug Patterns

#### Memory Leak Tracing
**Use case**: Find if bug causes resource leaks.

**Pattern**:
```
1. Locate allocation site (bug location)
2. Trace all possible execution paths
3. Check each path for:
   - Explicit cleanup/free
   - Scope-based cleanup
   - GC eligibility
4. Flag paths without cleanup
```

#### Race Condition Tracing
**Use case**: Find concurrency-related bug impact.

**Pattern**:
```
1. Identify shared state access at bug location
2. Find all concurrent access points:
   - Other functions accessing same state
   - Async/callback chains
   - Thread/task spawns
3. Map execution sequences that could race
4. Identify critical sections without locks
```

#### Error Propagation Tracing
**Use case**: Find where errors bubble up.

**Pattern**:
```
1. Start at error throw site
2. Trace exception propagation:
   - Which functions catch/rethrow?
   - Which functions let it pass through?
   - Where is it finally handled?
3. Identify:
   - Silent failures (caught but not logged)
   - Incorrect handling (catching too broadly)
   - Missing handling (uncaught exceptions)
```

## Heuristics

### When to Stop Tracing
- **Depth limit**: Reached max traversal depth (3-5 levels typical)
- **Module boundary**: Crossed into different bounded context
- **Centrality threshold**: Node importance below threshold
- **API boundary**: Reached external system boundary
- ** diminishing returns**: Additional impact < 5% of current total

### Confidence Levels
- **High confidence**: Direct call graph evidence, clear data flow
- **Medium confidence**: Indirect evidence, inferred relationships
- **Low confidence**: Speculative, needs verification

### Priority Weighting
When ranking impacted areas:
1. User-facing APIs highest priority
2. Data integrity impacts next
3. Performance impacts next
4. Internal utilities lowest

## Tool Integration

### graph_mcp Queries
```cypher
# Direct callers
MATCH (caller)-[:CALLS]->(bug_func)
RETURN caller, count(*) as call_count

# Downstream impact
MATCH path = (bug_func)-[:CALLS*1..3]->(impacted)
RETURN nodes(path), length(path)

# Integration points
MATCH (bug_func)-[:CALLS]->(external)
WHERE external:ExternalAPI OR external:DatabaseOp
RETURN external

# Centrality calculation
CALL algo.pageRank.stream('CALLS')
YIELD nodeId, score
MATCH (f) WHERE id(f) = nodeId
RETURN f.name, score
ORDER BY score DESC
```

### mind_mcp Integration
- Cross-reference impact findings with architecture docs
- Validate assumptions about module boundaries
- Check for documented invariants that might be violated
