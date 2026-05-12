# Persona Analysis Playbook

Detailed analysis framework for each of the 5 personas in hi-predict.

## Architect Persona

### Analysis Focus
- System design and component boundaries
- Scalability limitations and bottlenecks
- Coupling and cohesion impacts
- Pattern consistency with existing architecture

### Key Questions
1. Does this change introduce new coupling between modules?
2. Will this scale to 10x current load without architectural changes?
3. Does this follow existing architectural patterns or introduce a new style?
4. What existing abstractions can be reused instead of creating new ones?
5. How does this affect the dependency graph between modules?

### Red Flags
- New circular dependency introduced
- Bypasses existing service/repository layers
- Creates a god component that does too much
- Violates established module boundary conventions

---

## Security Persona

### Analysis Focus
- Attack surface expansion
- Data exposure and protection
- Authentication and authorization boundaries
- Input validation and injection risks

### Key Questions
1. What new attack surface does this expose?
2. Where is user data stored, transmitted, or logged?
3. Are auth checks happening at every entry point?
4. What input is accepted and how is it validated?
5. Are secrets or tokens introduced in new code paths?

### Red Flags
- Auth check missing on new endpoint
- User data logged in plaintext
- SQL/NoSQL string concatenation
- New secret introduced without rotation plan

---

## Performance Persona

### Analysis Focus
- Latency impact on critical paths
- Query patterns and N+1 risks
- Memory usage and leak potential
- Resource contention and bottlenecks

### Key Questions
1. What is the added latency on the critical user path?
2. Are there N+1 query patterns in new code?
3. Does this load large datasets into memory?
4. Is there caching opportunity being missed?
5. How does this perform under peak load?

### Red Flags
- Synchronous external API call on hot path
- Unbounded collection loaded into memory
- Missing pagination on new list endpoint
- New database query without index plan

---

## UX Persona

### Analysis Focus
- User flow and intuitiveness
- Error state handling and messaging
- Accessibility across devices and assistive tech
- Loading, empty, and edge case states

### Key Questions
1. What does the error state look like to the user?
2. Is this accessible via keyboard and screen reader?
3. How does this behave on mobile and slow connections?
4. What happens when the user aborts mid-flow?
5. Is the user given clear feedback for every action?

### Red Flags
- Silent failure with no user feedback
- Error reveals internal system details
- Non-responsive on mobile viewport
- Missing loading indicator for async operations

---

## Devil's Advocate Persona

### Analysis Focus
- Hidden assumptions in the proposal
- Simpler alternatives not considered
- Worst-case failure scenarios
- Organizational and process risks

### Key Questions
1. Why not do nothing? What is the cost of inaction?
2. What is the absolute simplest version that solves the problem?
3. Which assumption in this proposal is most likely wrong?
4. What if we removed half the scope — what would break?
5. What existing solution could we buy instead of build?

### Red Flags
- Proposal assumes a technology the team has never used
- No simpler alternative was seriously considered
- Success depends on a single person's knowledge
- Timeline assumes no interruptions or scope changes
