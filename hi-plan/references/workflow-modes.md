# Workflow Modes — Auto-Detection Logic

## Mode Selection

| Complexity | Characteristics | Recommended Mode |
|------------|----------------|-------------------|
| Trivial | Single file, <50 lines, no API change | `fast` |
| Moderate | 2-5 files, new function, minor refactor | `auto` (defaults to `hard`) |
| Complex | 5+ files, new module, API change | `hard` |
| Architectural | Cross-module, new service, DB migration | `hard` or `parallel` |

## Per-Mode Detail

### Fast Mode
- Scope challenge: Skip
- Research: Skip
- Codebase analysis: Minimal (affected files only)
- Solution design: One approach only
- Red team: Skip
- Validation: Skip

### Hard Mode
- Scope challenge: Full
- Research: 2 rounds (mind_mcp + graph_mcp)
- Codebase analysis: Full MCP analysis
- Solution design: Single approach with tradeoff documentation
- Red team: Yes
- Validation: Yes

### Parallel Mode
- Same as Hard, but spawns 2 parallel research tracks
- Research tracks compare findings before solution design
- Useful for complex domains with multiple valid approaches

### Two-Approaches Mode
- Same as Hard, but designs 2 competing solutions
- Red team evaluates both, recommends one
- Validation confirms selection
- Best for high-risk architectural decisions
