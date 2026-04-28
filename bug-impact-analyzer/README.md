# Bug Impact Analyzer Skill

A specialized skill for analyzing bugs and evaluating their impact across codebases using mind_mcp and graph_mcp.

## Overview

This skill helps you:
- Understand the scope and impact of bugs
- Trace upstream callers and downstream dependencies
- Assess severity and regression risk
- Generate fix recommendations with test strategies
- Prioritize bugs based on evidence-based analysis

## When to Use This Skill

Use this skill when:
- Triaging new bug reports
- Assessing risk before deploying fixes
- Planning bug fixes and estimating effort
- Conducting post-mortem analyses
- Prioritizing backlog items
- Onboarding to a legacy codebase with documented issues

## Required Tools

- **mind_mcp**: For retrieving project context, historical information, and documentation
- **graph_mcp**: For tracing call graphs, dependencies, and code relationships

## Workflow

### 1. Initialize Analysis
Provide:
- Bug identifier (issue URL, error message, stack trace, or location)
- Repository path
- Analysis scope (optional)

### 2. Gather Evidence
Run the analysis script:
```bash
python bug-impact-analyzer/bug_impact_analyzer.py \
  /path/to/repo \
  --bug "file:line or description" \
  --output /tmp/bug-analysis
```

This generates:
- Preliminary filesystem analysis
- MCP query suggestions
- Initial severity assessment
- Recommended next steps

### 3. Execute MCP Queries
Use the suggested queries from the analysis:
- Run mind_mcp queries for context
- Run graph_mcp queries for impact tracing
- Collect evidence systematically

### 4. Generate Final Report
Synthesize evidence into:
- Impact analysis report
- Risk assessment
- Fix recommendations
- Test strategy

## File Structure

```
bug-impact-analyzer/
├── SKILL.md                           # Main skill documentation
├── README.md                          # This file
├── bug_impact_analyzer.py            # Automation script
└── references/                        # Supporting documentation
    ├── bug-impact-template.md         # Report template
    ├── mcp-bug-playbook.md           # MCP query recipes
    ├── severity-matrix.md            # Severity classification
    └── dependency-tracing-patterns.md # Tracing patterns
```

## Output Artifacts

### bug_impact_analysis.md
Human-readable impact report including:
- Executive summary
- Bug description and location
- Impact analysis (modules, callers, dependencies, data flows)
- Risk assessment (severity, reach, regression risk)
- Fix recommendations with test strategy
- Evidence references with confidence levels

### bug_impact_graph.json
Machine-readable impact graph for:
- Automated processing
- Tool integration
- Historical tracking

### bug_evidence_trace.md (optional)
Detailed MCP query logs and raw evidence for:
- Reproducibility
- Audit trail
- Further analysis

## Integration with Other Skills

This skill works well with:
- **repo-recon**: For unfamiliar codebases
- **tech-build-audit**: For infrastructure-related bugs
- **module-summary-report**: For architectural context
- **reverse-doc-reconstruction**: For updating documentation based on findings

## Quality Gates

Ensure every analysis:
- References MCP evidence for each claim
- Includes confidence levels
- Identifies unknown areas explicitly
- Provides actionable recommendations
- Documents assumptions and open questions

## Example Usage

### Quick Analysis
```bash
python bug-impact_analyzer.py ~/project \
  --bug "src/auth/login.py:45" \
  --output /tmp/login-bug-analysis
```

### Full Workflow
1. Run the script for initial assessment
2. Execute suggested MCP queries manually
3. Update analysis with findings
4. Generate final report using the template

## Contributing

When extending this skill:
- Follow the existing documentation structure
- Update the MCP playbook with new query patterns
- Add severity criteria to the matrix
- Document new tracing patterns

## Resources

- See [SKILL.md](SKILL.md) for detailed workflow
- See [references/](references/) for templates and patterns
- See [bug_impact_analyzer.py](bug_impact_analyzer.py) for automation
