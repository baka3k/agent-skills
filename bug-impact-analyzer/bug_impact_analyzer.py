#!/usr/bin/env python3
"""
Bug Impact Analyzer

Automated bug impact analysis script that combines filesystem analysis
with MCP evidence (mind_mcp and graph_mcp) when available.

Usage:
    python bug_impact_analyzer.py /path/to/repo --bug "file:line or description" --output /tmp/bug-analysis
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class BugImpactAnalyzer:
    def __init__(self, repo_path: str, bug_info: str):
        self.repo_path = Path(repo_path)
        self.bug_info = bug_info
        self.analysis = {
            "bug_info": bug_info,
            "repository": str(self.repo_path),
            "analysis_date": datetime.now().isoformat(),
            "evidence": {
                "filesystem": {},
                "mind_mcp": {},
                "graph_mcp": {}
            },
            "impact": {
                "severity": "unknown",
                "reach_score": 0,
                "affected_modules": [],
                "upstream_callers": [],
                "downstream_dependencies": [],
                "integration_points": [],
                "data_flows": []
            },
            "risk_assessment": {
                "regression_risk": "unknown",
                "fix_complexity": "unknown",
                "confidence_level": "low"
            },
            "recommendations": {
                "priority": "unknown",
                "approach": "unknown",
                "test_strategy": []
            }
        }

    def analyze_filesystem(self) -> Dict[str, Any]:
        """
        Perform filesystem-based analysis.
        This works without MCP and provides baseline information.
        """
        print("Analyzing filesystem...")

        results = {
            "bug_location": None,
            "file_structure": [],
            "import_candidates": [],
            "similar_patterns": []
        }

        # Try to parse bug location if provided as "file:line" format
        if ":" in self.bug_info:
            file_part, line_part = self.bug_info.split(":", 1)
            potential_file = self.repo_path / file_part
            if potential_file.exists():
                results["bug_location"] = {
                    "file": str(potential_file.relative_to(self.repo_path)),
                    "line": line_part,
                    "confidence": "high"
                }
                print(f"  Found bug location: {potential_file}")

        # Scan for project structure
        try:
            for root, dirs, files in os.walk(self.repo_path):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in {
                    '.git', '.venv', 'venv', 'node_modules',
                    '__pycache__', '.next', 'dist', 'build'
                }]

                for file in files:
                    ext = Path(file).suffix
                    if ext in {'.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c'}:
                        rel_path = Path(root) / file
                        results["file_structure"].append(str(rel_path.relative_to(self.repo_path)))
        except Exception as e:
            print(f"  Warning: Could not scan repository: {e}")

        print(f"  Found {len(results['file_structure'])} source files")
        self.analysis["evidence"]["filesystem"] = results
        return results

    def suggest_mcp_queries(self) -> Dict[str, List[str]]:
        """
        Suggest MCP queries for manual execution.
        These would be run by the analyst using mind_mcp and graph_mcp.
        """
        print("\nGenerating MCP query suggestions...")

        queries = {
            "mind_mcp": [
                # Context queries
                f"Search knowledge base for documentation about the affected area: {self.bug_info}",
                "Find architectural decisions (ADRs) related to this module",
                "Look for historical bugs or fixes in similar areas",
                "Retrieve business requirements or domain models for affected features",
            ],
            "graph_mcp": [
                # Location queries
                f"Semantic search for code related to: {self.bug_info}",
                "Find error handling patterns in the affected module",
                "Locate exception throwing sites",
                # Impact tracing queries
                "Trace upstream callers from the bug location (2-3 levels)",
                "Trace downstream dependencies and data flows",
                "Identify API boundary crossings",
                "Find integration points with external services",
                # Test coverage queries
                "Find test files covering the affected functions",
                "Assess test coverage for impacted areas",
            ]
        }

        self.analysis["mcp_query_suggestions"] = queries
        return queries

    def calculate_preliminary_severity(self) -> str:
        """
        Calculate preliminary severity based on available evidence.
        This is a rough estimate without full MCP data.
        """
        print("\nCalculating preliminary severity...")

        # Default to medium if we don't have much info
        severity = "medium"

        # Check if we have location info
        if self.analysis["evidence"]["filesystem"].get("bug_location"):
            file_path = self.analysis["evidence"]["filesystem"]["bug_location"]["file"]

            # Heuristics based on file location
            if any(keyword in file_path.lower() for keyword in
                   ['auth', 'security', 'payment', 'database', 'data']):
                severity = "high"
            elif any(keyword in file_path.lower() for keyword in
                     ['util', 'helper', 'common', 'shared']):
                # Could be high impact if widely used
                severity = "medium-high"
            elif any(keyword in file_path.lower() for keyword in
                     ['test', 'spec', 'mock']):
                severity = "low"

        self.analysis["impact"]["severity"] = severity
        print(f"  Preliminary severity: {severity}")
        return severity

    def generate_recommendations(self) -> Dict[str, Any]:
        """
        Generate initial recommendations based on analysis.
        """
        print("\nGenerating recommendations...")

        severity = self.analysis["impact"]["severity"]
        priority_map = {
            "critical": "P0",
            "high": "P1",
            "medium-high": "P1",
            "medium": "P2",
            "low": "P3",
            "unknown": "P2"
        }

        recommendations = {
            "priority": priority_map.get(severity, "P2"),
            "next_steps": [
                "Execute suggested MCP queries to gather evidence",
                "Analyze impact using graph_mcp call graph tracing",
                "Cross-reference with mind_mcp documentation",
                "Update severity based on findings",
                "Generate detailed impact report"
            ],
            "data_collection": {
                "required": [
                    "Exact bug location from graph_mcp",
                    "Upstream caller count and types",
                    "Downstream dependency analysis",
                    "Test coverage assessment",
                    "Historical context from mind_mcp"
                ],
                "optional": [
                    "Performance impact data",
                    "Security implications",
                    "Business impact assessment"
                ]
            }
        }

        self.analysis["recommendations"].update(recommendations)
        return recommendations

    def save_results(self, output_base: str):
        """
        Save analysis results to JSON and Markdown formats.
        """
        output_path = Path(output_base)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(self.analysis, f, indent=2)
        print(f"\nSaved JSON analysis to: {json_path}")

        # Save Markdown
        md_path = output_path.with_suffix('.md')
        self._save_markdown(md_path)
        print(f"Saved Markdown report to: {md_path}")

        # Save MCP query suggestions separately
        queries_path = output_path.parent / (output_path.stem + "_mcp_queries.md")
        self._save_mcp_queries(queries_path)
        print(f"Saved MCP query suggestions to: {queries_path}")

    def _save_markdown(self, path: Path):
        """
        Generate a human-readable Markdown report.
        """
        with open(path, 'w') as f:
            f.write(f"# Bug Impact Analysis Report\n\n")
            f.write(f"**Bug**: {self.bug_info}\n")
            f.write(f"**Repository**: {self.repo_path}\n")
            f.write(f"**Analysis Date**: {self.analysis['analysis_date']}\n\n")

            f.write(f"## Executive Summary\n\n")
            f.write(f"**Preliminary Severity**: {self.analysis['impact']['severity'].upper()}\n")
            f.write(f"**Recommended Priority**: {self.analysis['recommendations']['priority']}\n\n")

            f.write(f"**Note**: This is a preliminary analysis without full MCP evidence.\n")
            f.write(f"Execute the suggested MCP queries to complete the analysis.\n\n")

            f.write(f"## Current Evidence\n\n")
            f.write(f"### Filesystem Analysis\n\n")
            if self.analysis["evidence"]["filesystem"].get("bug_location"):
                loc = self.analysis["evidence"]["filesystem"]["bug_location"]
                f.write(f"- **Bug Location**: {loc['file']}:{loc['line']} (confidence: {loc['confidence']})\n")
            else:
                f.write(f"- Bug location not yet identified from filesystem alone\n")
            f.write(f"- **Source Files Found**: {len(self.analysis['evidence']['filesystem'].get('file_structure', []))}\n\n")

            f.write(f"## Impact Assessment\n\n")
            f.write(f"**Severity**: {self.analysis['impact']['severity']}\n")
            f.write(f"**Reach Score**: TBD (requires graph_mcp analysis)\n\n")
            f.write(f"**Affected Areas**: TBD (requires graph_mcp call tracing)\n\n")

            f.write(f"## Recommendations\n\n")
            f.write(f"### Priority: {self.analysis['recommendations']['priority']}\n\n")
            f.write(f"### Next Steps\n\n")
            for step in self.analysis["recommendations"]["next_steps"]:
                f.write(f"1. {step}\n")
            f.write(f"\n")

            f.write(f"### Data Collection Required\n\n")
            f.write(f"**Required**:\n")
            for item in self.analysis["recommendations"]["data_collection"]["required"]:
                f.write(f"- {item}\n")
            f.write(f"\n**Optional**:\n")
            for item in self.analysis["recommendations"]["data_collection"]["optional"]:
                f.write(f"- {item}\n")

            f.write(f"\n## MCP Evidence Needed\n\n")
            f.write(f"See `*_mcp_queries.md` for detailed query suggestions.\n\n")

    def _save_mcp_queries(self, path: Path):
        """
        Save MCP query suggestions to a separate file.
        """
        with open(path, 'w') as f:
            f.write(f"# MCP Query Suggestions for Bug Analysis\n\n")
            f.write(f"**Bug**: {self.bug_info}\n")
            f.write(f"**Repository**: {self.repo_path}\n\n")

            f.write(f"## mind_mcp Queries\n\n")
            f.write(f"Use these queries to gather context from the project knowledge base:\n\n")
            for i, query in enumerate(self.analysis.get("mcp_query_suggestions", {}).get("mind_mcp", []), 1):
                f.write(f"{i}. {query}\n")

            f.write(f"\n## graph_mcp Queries\n\n")
            f.write(f"Use these queries to analyze code structure and dependencies:\n\n")
            for i, query in enumerate(self.analysis.get("mcp_query_suggestions", {}).get("graph_mcp", []), 1):
                f.write(f"{i}. {query}\n")

            f.write(f"\n## Query Execution Sequence\n\n")
            f.write(f"1. Run mind_mcp queries to understand context\n")
            f.write(f"2. Run graph_mcp location queries to find exact bug position\n")
            f.write(f"3. Run graph_mcp impact tracing queries (upstream + downstream)\n")
            f.write(f"4. Run graph_mcp test coverage queries\n")
            f.write(f"5. Synthesize evidence and update analysis\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze bug impact using filesystem and MCP evidence"
    )
    parser.add_argument(
        "repo_path",
        help="Path to the repository root"
    )
    parser.add_argument(
        "--bug",
        required=True,
        help="Bug identifier: file:line, function name, or description"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="/tmp/bug-impact-analysis",
        help="Output base path for results (default: /tmp/bug-impact-analysis)"
    )
    parser.add_argument(
        "--scope",
        choices=["local", "module", "system", "full"],
        default="module",
        help="Analysis scope (default: module)"
    )

    args = parser.parse_args()

    # Validate repository path
    if not os.path.exists(args.repo_path):
        print(f"Error: Repository path does not exist: {args.repo_path}")
        sys.exit(1)

    # Run analysis
    print(f"Bug Impact Analyzer")
    print(f"=" * 60)
    print(f"Repository: {args.repo_path}")
    print(f"Bug: {args.bug}")
    print(f"Scope: {args.scope}")
    print(f"Output: {args.output}")
    print()

    analyzer = BugImpactAnalyzer(args.repo_path, args.bug)

    # Perform analysis stages
    analyzer.analyze_filesystem()
    analyzer.suggest_mcp_queries()
    analyzer.calculate_preliminary_severity()
    analyzer.generate_recommendations()

    # Save results
    analyzer.save_results(args.output)

    print(f"\n" + "=" * 60)
    print(f"Analysis complete!")
    print(f"\nNext steps:")
    print(f"1. Review the generated reports")
    print(f"2. Execute suggested MCP queries")
    print(f"3. Update analysis with MCP findings")
    print(f"4. Generate final impact report")


if __name__ == "__main__":
    main()
