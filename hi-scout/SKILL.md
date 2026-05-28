---
name: hi:scout
description: "Fast codebase scouting using parallel agents. Use for file discovery, task context gathering, searching across directories."
argument-hint: "[search-target] [ext]"
metadata:
  author: baka3k
  version: "2.0.0"
---
# Scout

Fast, token-efficient codebase scouting using parallel agents.

## Arguments
- Default: Explore subagents in parallel
- ext: External Gemini/OpenCode CLI tools

## Workflow

### 1. Analyze
Parse user prompt for targets, key directories, patterns, file types. Determine SCALE (subagent count).

### 2. Divide
Split codebase logically. Each agent gets distinct scope, no overlap.

### 3. Register Tasks
Skip if <=2 agents or Task tools unavailable.
TaskList -> use existing. Else TaskCreate per agent with scope metadata.
Metadata: agentType, scope, scale, agentIndex, totalAgents, toolMode, priority:P2, effort:3m.
See references/task-management.md for patterns.

### 4. Spawn
Load internal (references/internal-scouting.md) or external (references/external-scouting.md).
TaskUpdate each to in_progress before spawning. Max 3m per agent. Skip timed-out.

### 5. Collect
Aggregate: deduplicate paths, merge descriptions, note gaps/timeouts, list unresolved.

## Report Format
```markdown
# Scout Report
## Relevant Files
- path/to/file.ts - description
## Unresolved Questions
- any gaps
```

## Configuration
Read .claude/.ck.json: gemini.model (default: gemini-3-flash-preview).

Invoke /hi:project-organization to organize outputs.
