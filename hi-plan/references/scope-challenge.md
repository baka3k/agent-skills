# Scope Challenge Framework

Before starting any plan, challenge whether the work should be done at all.

## Challenge Questions

1. **Why not do nothing?** What is the cost of inaction vs the cost of change?
2. **What is the simplest version that works?** Remove all non-essential aspects.
3. **What problem are we actually solving?** Reframe the feature in problem terms.
4. **Who is this for?** Is the audience clearly defined and measurable?
5. **What is the success criteria?** Must be verifiable, not "it works."
6. **What happens if we get it wrong?** Define rollback and recovery.

## Complexity Classification

After scope challenge, classify complexity:

- **Trivial**: Single file, <50 LOC, no API change, known pattern → `fast` mode
- **Moderate**: 2-5 files, new function, minor refactor → `hard` mode
- **Complex**: 5+ files, new module, API contract change → `hard` mode
- **Architectural**: Cross-module, new service, DB schema migration → `hard`/`parallel`

## Scope Reduction Rules

If scope can be reduced, do so before mode selection:
- Can this be split into smaller independent plans?
- Can we defer non-critical aspects to a follow-up?
- Can we reuse existing infrastructure instead of building new?
