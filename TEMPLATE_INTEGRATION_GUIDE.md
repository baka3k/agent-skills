# Template Integration Guide

**Version**: 1.0.0
**Date**: 2025-04-16
**Status**: ✅ Active

---

## Overview

This guide documents how Agent Skill Kit skills use standard templates from the `template/` directory to generate consistent, professional documentation artifacts.

### Template Directory Structure

```
template/
├── 00_requirements/
│   ├── tpl_requirements_spec.md
│   └── tpl_feature_list.md
├── 01_usecase/
│   ├── tpl_usecase_list.md
│   ├── tpl_usecase_detail.md
│   └── tpl_usecase_metrics.md
├── 02_detail_design/
│   ├── tpl_screen_design.md
│   ├── tpl_api_process_design.md
│   ├── tpl_openapi_spec.yaml
│   ├── tpl_table_design.md
│   ├── tpl_sql_design.md
│   └── tpl_batch_process_design.md
├── 03_system_design/
│   ├── tpl_system_architecture.md
│   ├── tpl_infra_design.md
│   ├── tpl_security_design.md
│   └── tpl_adr.md
├── 04_testing/
│   ├── tpl_test_plan.md
│   ├── tpl_test_case.md
│   ├── tpl_bug_report.md
│   └── tpl_test_summary_report.md
├── 05_operations/
│   ├── tpl_release_note.md
│   ├── tpl_deployment.md
│   ├── tpl_runbook.md
│   └── tpl_monitoring.md
└── 06_project_mgmt/
    ├── tpl_meeting_minutes.md
    ├── tpl_risk_register.md
    └── tpl_change_log.md
```

---

## Skills Using Standard Templates

### 1. reverse-doc-reconstruction

**Status**: ✅ Fully Integrated

**Templates Used**:
- `template/00_requirements/tpl_requirements_spec.md`
- `template/00_requirements/tpl_feature_list.md`
- `template/01_usecase/tpl_usecase_list.md`
- `template/01_usecase/tpl_usecase_metrics.md`
- `template/01_usecase/tpl_usecase_detail.md`
- `template/02_detail_design/tpl_screen_design.md`
- `template/02_detail_design/tpl_api_process_design.md`
- `template/02_detail_design/tpl_openapi_spec.yaml`
- `template/02_detail_design/tpl_table_design.md`
- `template/02_detail_design/tpl_sql_design.md`
- `template/02_detail_design/tpl_batch_process_design.md`

**Implementation**:
```python
# File: reverse-doc-reconstruction/scripts/bootstrap_reverse_doc_workspace.py

TEMPLATE_MAP = [
    ("00_requirements/tpl_requirements_spec.md", "00_requirements/requirements_spec_{module}.md"),
    ("00_requirements/tpl_feature_list.md", "00_requirements/feature_list_{module}.md"),
    ("01_usecase/tpl_usecase_list.md", "01_usecase/usecase_list_{module}.md"),
    ("01_usecase/tpl_usecase_metrics.md", "01_usecase/usecase_metrics_{module}.md"),
    ("01_usecase/tpl_usecase_detail.md", "01_usecase/uc001_{module}_template.md"),
    ("02_detail_design/tpl_screen_design.md", "02_detail_design/screen_design_{module}.md"),
    ("02_detail_design/tpl_api_process_design.md", "02_detail_design/api_process_design_{module}.md"),
    ("02_detail_design/tpl_openapi_spec.yaml", "02_detail_design/openapi_spec_{module}.yaml"),
    ("02_detail_design/tpl_table_design.md", "02_detail_design/table_design_{module}.md"),
    ("02_detail_design/tpl_sql_design.md", "02_detail_design/sql_design_{module}.md"),
    ("02_detail_design/tpl_batch_process_design.md", "02_detail_design/batch_process_design_{module}.md"),
]

def copy_templates(template_dir: Path, output_dir: Path, replacements: Dict[str, str]) -> None:
    """Copy templates from template/ directory and replace placeholders."""
    for template_path, output_path in TEMPLATE_MAP:
        src = template_dir / template_path
        dst = output_dir / output_path.format(**replacements)

        # Read template
        content = src.read_text(encoding="utf-8")

        # Replace placeholders
        for placeholder, value in replacements.items():
            content = content.replace(f"{{{placeholder}}}", value)

        # Write output
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
```

**Usage**:
```bash
# Bootstrap workspace with templates
python scripts/bootstrap_reverse_doc_workspace.py \
    --target-root /path/to/repo \
    --module auth-service \
    --owner "Team A" \
    --date 2025-04-16
```

**SKILL.md References**:
- Explicitly lists all templates from `template/` directory
- Documents placeholder replacements: `{ModuleID}`, `{owner}`, `{date}`
- Links to template usage in Phase 2 workflow

---

### 2. repo-recon

**Status**: ✅ Fully Integrated

**Template Used**:
- `repo-recon/references/module-inventory-template.md` (skill-specific)

**Implementation**:
```python
# File: repo-recon/scripts/repo_recon.py

def load_template(template_path: str) -> str:
    """Load template from file."""
    script_dir = Path(__file__).parent
    template_abs_path = script_dir.parent / "references" / template_path
    with open(template_abs_path, "r", encoding="utf-8") as f:
        return f.read()

def populate_template(template: str, data: Dict) -> str:
    """Populate module inventory template with discovered data."""
    lines = template.split("\n")
    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Context section
        if line.strip().startswith("- Repository:"):
            output_lines.append(f"- Repository: `{data.get('root', 'N/A')}`")
        elif line.strip().startswith("- Commit/branch:"):
            output_lines.append(f"- Commit/branch: `{data.get('commit', 'N/A')}`")

        # Top-Level Modules table
        elif line.strip() == "| Module | Purpose | Key Files | Dominant Languages | Notes |":
            output_lines.append(line)
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|---|")

            modules = data.get("module_candidates", [])
            if modules:
                for mod in modules:
                    name = mod.get("module", "")
                    purpose = _infer_module_purpose(mod)
                    key_files = mod.get("key_files", [])
                    langs = mod.get("dominant_languages", [])
                    notes = f"{mod.get('source_file_count', 0)} source files"
                    output_lines.append(f"| {name} | {purpose} | {key_files} | {langs} | {notes} |")

        # ... more sections

        i += 1

    return "\n".join(output_lines)

def to_markdown(data: Dict) -> str:
    """Generate markdown output using module inventory template."""
    template = load_template("module-inventory-template.md")
    return populate_template(template, data)
```

**Usage**:
```bash
# Generate module inventory using template
python scripts/repo_recon.py /path/to/repo --md module_inventory.md
```

**Key Features**:
- Template-based output generation
- Intelligent data mapping (module purpose inference, runtime classification)
- Preserves template structure while populating with discovered data

---

### 3. tech-build-audit

**Status**: ✅ Fully Integrated

**Template Used**:
- `tech-build-audit/references/audit-template.md` (skill-specific)

**Implementation**:
```python
# File: tech-build-audit/scripts/tech_build_audit.py

def load_template(template_path: str) -> str:
    """Load template from file."""
    script_dir = Path(__file__).parent
    template_abs_path = script_dir.parent / "references" / template_path
    with open(template_abs_path, "r", encoding="utf-8") as f:
        return f.read()

def populate_template(template: str, data: Dict) -> str:
    """Populate audit template with scan data."""
    # Build technology matrix
    areas = _build_technology_matrix(data)

    # Build command table
    commands = _build_command_table(data)

    # Generate risks
    risks = _generate_risks(data)

    # ... populate template sections

def to_markdown(data: Dict) -> str:
    """Generate markdown output using audit template."""
    template = load_template("audit-template.md")
    return populate_template(template, data)
```

**Usage**:
```bash
# Generate tech audit using template
python scripts/tech_build_audit.py /path/to/repo --md tech_audit.md
```

**Key Features**:
- Technology matrix mapping (languages, frameworks, build systems, CI/CD, deployment)
- Command table generation by ecosystem (Node, Python, Go, Rust)
- Risk assessment based on scan gaps (build reproducibility, release pipeline)

---

### 4. bug-impact-analyzer

**Status**: ✅ Template References Updated

**Templates Referenced**:
- `references/bug-impact-template.md` (skill-specific, for impact analysis)
- `template/04_testing/tpl_bug_report.md` (standard, for initial bug documentation)
- `template/04_testing/tpl_test_case.md` (standard, for regression tests)
- `template/04_testing/tpl_test_plan.md` (standard, for test strategy)

**Usage**:
```yaml
# For bug documentation
- Use tpl_bug_report.md for initial bug report
- Document reproduction steps, evidence, technical info

# For impact analysis
- Use bug-impact-template.md for reach metrics and risk assessment
- Analyze upstream/downstream dependencies
- Generate fix recommendations

# For testing
- Use tpl_test_case.md to document regression tests
- Use tpl_test_plan.md for comprehensive test strategy
```

**SKILL.md Integration**:
```markdown
## Resources

### Standard Templates

**Skill-Specific Template**:
- `references/bug-impact-template.md`: Specialized template for bug impact analysis

**Standard Testing Templates** (template/04_testing/):
- `tpl_bug_report.md`: Standard bug report format for initial bug documentation
- `tpl_test_case.md`: Test case template for creating regression tests
- `tpl_test_plan.md`: Test plan template for comprehensive testing strategy

**Template Usage Guide**:
- Use `tpl_bug_report.md` for initial bug documentation and reproduction
- Use `bug-impact-template.md` for impact analysis and risk assessment
- Use `tpl_test_case.md` to document regression tests from fix recommendations
- Use `tpl_test_plan.md` to create comprehensive test strategy for high-impact bugs
```

---

## Template Integration Best Practices

### 1. Template Loading

**Standard Pattern**:
```python
def load_template(template_path: str) -> str:
    """Load template from template/ directory."""
    script_dir = Path(__file__).parent
    template_abs_path = script_dir.parent.parent / "template" / template_path
    with open(template_abs_path, "r", encoding="utf-8") as f:
        return f.read()
```

**For Skill-Specific Templates**:
```python
def load_template(template_path: str) -> str:
    """Load template from skill's references/ directory."""
    script_dir = Path(__file__).parent
    template_abs_path = script_dir.parent / "references" / template_path
    with open(template_abs_path, "r", encoding="utf-8") as f:
        return f.read()
```

### 2. Placeholder Replacement

**Simple Replacement**:
```python
def replace_placeholders(template: str, data: Dict[str, str]) -> str:
    """Replace placeholders in template."""
    content = template
    for key, value in data.items():
        content = content.replace(f"{{{key}}}", value)
    return content
```

**Usage**:
```python
replacements = {
    "ModuleID": "auth-service",
    "owner": "Team A",
    "date": "2025-04-16",
}
populated = replace_placeholders(template, replacements)
```

### 3. Table Population

**Standard Pattern**:
```python
def populate_table(template_lines: List[str], data: List[Dict]) -> List[str]:
    """Populate template table with data."""
    output = []
    for line in template_lines:
        if "| Header1 | Header2 |" in line:
            output.append(line)
            # Add separator if not present
            if not template_lines[template_lines.index(line) + 1].strip().startswith("|---"):
                output.append("|---|---|")
            # Add data rows
            for row in data:
                output.append(f"| {row['col1']} | {row['col2']} |")
            # Skip template placeholder rows
            while template_lines.index(line) + 1 < len(template_lines):
                if template_lines[template_lines.index(line) + 1].strip().startswith("|"):
                    break
                template_lines.pop(template_lines.index(line) + 1)
        else:
            output.append(line)
    return output
```

### 4. Documentation Updates

**SKILL.md Template Section**:
```markdown
## Standard Templates

**Templates Used**:
- `template/XX_category/tpl_template_name.md` - Description

**Implementation**:
- Script: `scripts/script_name.py`
- Function: `load_template()`, `populate_template()`
- Placeholders: `{placeholder1}`, `{placeholder2}`

**Usage**:
```bash
python scripts/script_name.py --input data.json --output output.md
```
```

---

## Template Mapping by Skill

### Documentation Generation Skills

| Skill | Template Category | Templates Used |
|-------|------------------|----------------|
| reverse-doc-reconstruction | 00_requirements, 01_usecase, 02_detail_design | 11 templates |
| repo-recon | Custom (module inventory) | 1 template |
| tech-build-audit | Custom (tech audit) | 1 template |
| bug-impact-analyzer | 04_testing | Referenced (not used directly) |
| module-summary-report | 03_system_design, 06_project_mgmt | To be integrated |
| deep-codebase-discovery | Multiple | To be integrated |
| legacy-cpp-porting-guardrails | 02_detail_design, 04_testing | To be verified |

---

## Future Work

### Skills Requiring Template Integration

1. **module-summary-report**
   - Review summary-template.md for template/ compatibility
   - Consider using `template/03_system_design/tpl_system_architecture.md`
   - Consider using `template/06_project_mgmt/tpl_risk_register.md`

2. **deep-codebase-discovery**
   - Update discovery-bundle-template.md to reference template/ templates
   - Use `template/03_system_design/tpl_adr.md` for architecture decisions

3. **legacy-cpp-porting-guardrails**
   - Verify scripts are using templates correctly
   - Update to use `template/02_detail_design/` for design artifacts
   - Update to use `template/04_testing/` for parity test artifacts

### Template Helper Library

Consider creating a shared template helper library:

```python
# template/template_helper.py

class TemplateHelper:
    """Shared template utilities for all skills."""

    @staticmethod
    def load_template(template_path: str) -> str:
        """Load template from template/ directory."""
        pass

    @staticmethod
    def replace_placeholders(template: str, data: Dict) -> str:
        """Replace placeholders in template."""
        pass

    @staticmethod
    def populate_table(template: str, table_name: str, data: List[Dict]) -> str:
        """Populate specific table in template."""
        pass

    @staticmethod
    def write_output(content: str, output_path: Path) -> None:
        """Write populated template to file."""
        pass
```

---

## Verification Checklist

### For New Skills

- [ ] Script uses templates from `template/` directory (when applicable)
- [ ] SKILL.md references templates explicitly
- [ ] Template usage documented in workflow section
- [ ] Placeholders documented and standardized
- [ ] Examples provided in SKILL.md

### For Existing Skills

- [ ] Templates explicitly referenced in SKILL.md
- [ ] Script uses `load_template()` pattern
- [ ] Placeholder replacement follows standard pattern
- [ ] Template structure preserved in output
- [ ] Error handling for missing templates

---

## Troubleshooting

### Common Issues

**Issue**: Template not found
- **Cause**: Incorrect template path or template not in template/ directory
- **Solution**: Verify template path exists, check SKILL.md references

**Issue**: Placeholders not replaced
- **Cause**: Placeholder format mismatch (`{var}` vs `{{var}}` vs `%var%`)
- **Solution**: Use standard `{variable}` format consistently

**Issue**: Table structure broken
- **Cause**: Incorrect table population logic
- **Solution**: Verify separator row (`|---|---|`) is added after header

**Issue**: Template encoding errors
- **Cause**: File not read as UTF-8
- **Solution**: Always use `encoding="utf-8"` when reading templates

---

**Last Updated**: 2025-04-16
**Next Review**: When adding new skills or templates
