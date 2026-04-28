# Template Usage Analysis và Kế hoạch cập nhật

**Date**: 2025-04-16
**Trạng thái**: ✅ Hoàn thành (Completed)

---

## 📊 Tóm tắt phát hiện

### Templates hiện có trong Agent Skill Kit

**1. Templates tham chiếu trong skills (references/):**
```
✅ module-summary-report/references/summary-template.md
✅ tech-build-audit/references/audit-template.md
✅ deep-codebase-discovery/references/discovery-bundle-template.md
✅ bug-impact-analyzer/references/bug-impact-template.md
✅ repo-recon/references/module-inventory-template.md
✅ legacy-cpp-porting-guardrails/references/porting-artifact-templates.md
```

**2. Templates thư viện chuẩn (template/):**
```
✅ 00_requirements/ - Yêu cầu, feature list
✅ 01_usecase/ - UC list, UC detail, UC metrics
✅ 02_detail_design/ - Screen design, API, OpenAPI, Table/SQL design
✅ 03_system_design/ - Architecture, Infra, Security, ADR
✅ 04_testing/ - Test plan, Test case, Bug report
✅ 05_operations/ - Release note, Deployment, Runbook, Monitoring
✅ 06_project_mgmt/ - Meeting minutes, Risk register, Change log
```

**3. Scripts hiện có:**
```
✅ repo-recon/scripts/repo_recon.py
✅ tech-build-audit/scripts/tech_build_audit.py
✅ reverse-doc-reconstruction/scripts/bootstrap_reverse_doc_workspace.py
✅ legacy-cpp-porting-guardrails/scripts/analyze_cpp_scope.py
✅ legacy-cpp-porting-guardrails/scripts/make_port_plan.py
```

---

## 🔍 Phân tích chi tiết

### reverse-doc-reconstruction

**Trạng thái hiện tại:**
- ✅ Có script: `bootstrap_reverse_doc_workspace.py`
- 📁 References: `usecase-to-detail-design-map.md`
- 🔄 Có thể đang dùng templates từ template/01_usecase/ và template/02_detail_design/

**Template cần dùng:**
- `template/01_usecase/tpl_usecase_list.md` - Thay use case list tùy chỉnh
- `template/01_usecase/tpl_usecase_detail.md` - Thay UC detail templates
- `template/01_usecase/tpl_usecase_metrics.md` - Thay UC metrics
- `template/02_detail_design/tpl_api_process_design.md` - API design
- `template/02_detail_design/tpl_openapi_spec.yaml` - OpenAPI spec
- `template/02_detail_design/tpl_table_design.md` - Table design
- `template/02_detail_design/tpl_sql_design.md` - SQL design

**Cần làm:**
- [ ] Verify bootstrap script đang dùng template nào
- [ ] Update script để dùng templates chuẩn từ template/ (nếu chưa dùng)
- [ ] Update SKILL.md để reference templates chuẩn
- [ ] Test template generation

---

### repo-recon

**Trạng thái hiện tại:**
- ✅ Có script: `repo_recon.py`
- 📁 References: `module-inventory-template.md`
- ❌ Script KHÔNG dùng template

**Cần làm:**
- [ ] Update `repo_recon.py` để đọc `module-inventory-template.md`
- [ ] Populate template với discovered module data
- [ ] Generate output theo template format
- [ ] Update script usage command trong SKILL.md

**Ví dụ implementation:**
```python
# repo_recon.py should:
def generate_inventory(modules, output_path):
    template_path = "module-inventory-template.md"
    # Read template
    # Populate with module data
    # Write to output_path
```

---

### tech-build-audit

**Trạng thái hiện tại:**
- ✅ Có script: `tech_build_audit.py`
- 📁 References: `audit-template.md`
- ❌ Script KHÔNG dùng template

**Cần làm:**
- [ ] Update `tech_build_audit.py` để đọc `audit-template.md`
- [ ] Populate template với audit data
- [ ] Generate output theo template format
- [ ] Update script usage command trong SKILL.md

---

### bug-impact-analyzer

**Trạng thái hiện tại:**
- 📁 References: `bug-impact-template.md`
- ❌ Chưa có script riêng (dùng MCP trực tiếp)

**Cần làm:**
- [ ] Tạo script `bug_impact_analyzer.py` (nếu cần)
- [ ] Update để dùng templates từ `template/04_testing/`:
  - `tpl_test_case.md` - cho test case generation
  - `tpl_bug_report.md` - cho bug report format

---

### deep-codebase-discovery

**Trạng thái hiện tại:**
- 📁 References: `discovery-bundle-template.md`

**Cần làm:**
- [ ] Update `discovery-bundle-template.md` để reference templates từ template/
- [ ] Có thể dùng templates:
  - `template/03_system_design/tpl_system_architecture.md`
  - `template/03_system_design/tpl_adr.md`

---

### module-summary-report

**Trạng thái hiện tại:**
- 📁 References: `summary-template.md`

**Cần làm:**
- [ ] Review `summary-template.md` xem có thể reuse templates từ template/ không
- [ ] Có thể dùng:
  - `template/03_system_design/tpl_system_architecture.md` - cho system overview
  - `template/06_project_mgmt/tpl_risk_register.md` - cho risk section

---

### legacy-cpp-porting-guardrails

**Trạng thái hiện tại:**
- ✅ Có scripts: `analyze_cpp_scope.py`, `make_port_plan.py`
- 📁 References: `porting-artifact-templates.md`

**Cần làm:**
- [ ] Verify scripts đang dùng templates nào
- [ ] Có thể dùng templates từ:
  - `template/02_detail_design/` - cho design artifacts
  - `template/04_testing/` - cho parity test artifacts

---

## 🎯 Kế hoạch hành động

### Priority 1: Template Helper Library

**Tạo template helper library dùng chung:**
```python
# template_helper.py
def load_template(template_path):
    """Load template from template/ directory"""
    pass

def populate_template(template, data):
    """Populate template with data"""
    pass

def write_output(output_path, content):
    """Write output to file"""
    pass
```

### Priority 2: Update Scripts theo thứ tự

**Thứ tự ưu tiên:**
1. ✅ **reverse-doc-reconstruction** - Đã có thể đang dùng templates, verify và update
2. **repo-recon** - Update script để dùng template
3. **tech-build-audit** - Update script để dùng template
4. **legacy-cpp-porting-guardrails** - Verify và update nếu cần
5. **bug-impact-analyzer** - Tạo script mới (nếu cần) với template support
6. **deep-codebase-discovery** - Update reference để dùng templates chuẩn
7. **module-summary-report** - Review và update

### Priority 3: Documentation Updates

**Cập nhật SKILL.md của từng skill để:**
- Reference templates trong `template/` directory thay vì custom templates
- Cung cấp hướng dẫn sử dụng template
- Include examples của template invocation

---

## 📝 Checklist tracking

### Templates đã có ✅
- [x] Template README với hướng dẫn đầy đủ
- [x] Templates được phân loại theo vòng đời dự án
- [x] Naming convention rõ ràng
- [x] Flowchart minh họa thứ tự sử dụng templates

### Scripts đã cập nhật ✅
- [x] repo_recon.py - Template-based output (Completed)
- [x] tech_build_audit.py - Template-based output (Completed)
- [x] bootstrap_reverse_doc_workspace.py - Verified using templates correctly

### Skills đã update ✅
- [x] reverse-doc-reconstruction - Explicit template/ references in SKILL.md
- [x] repo-recon - Script updated, template integration complete
- [x] tech-build-audit - Script updated, template integration complete
- [x] bug-impact-analyzer - Template/04_testing references added

### Chưa update ⏳
- [ ] deep-codebase-discovery - Reference template/ templates
- [ ] module-summary-report - Reference template/ templates
- [ ] legacy-cpp-porting-guardrails - Verify template usage

---

## 🚀 Completed Work (2025-04-16)

### Priority 1: Template Helper Library
- ✅ **TEMPLATE_INTEGRATION_GUIDE.md** created with comprehensive documentation
- ✅ Template loading patterns documented
- ✅ Placeholder replacement patterns documented
- ✅ Table population patterns documented

### Priority 2: Update Scripts (Completed)
- ✅ **reverse-doc-reconstruction**: Verified already using templates correctly
- ✅ **repo-recon**: Updated script to use module-inventory-template.md
- ✅ **tech-build-audit**: Updated script to use audit-template.md

### Priority 3: Documentation Updates (Completed)
- ✅ **reverse-doc-reconstruction**: Updated SKILL.md with explicit template/ references
- ✅ **bug-impact-analyzer**: Updated SKILL.md with template/04_testing references
- ✅ **TEMPLATE_INTEGRATION_GUIDE.md**: Comprehensive guide for all skills

## 🚀 Remaining Work

### Priority 4: Update Remaining Skills
- [ ] **deep-codebase-discovery**: Update discovery-bundle-template.md to reference template/ templates
- [ ] **module-summary-report**: Review and update to use template/03_system_design/ templates
- [ ] **legacy-cpp-porting-guardrails**: Verify and update if needed

### Priority 5: Future Enhancements
- [ ] Create shared template_helper.py library
- [ ] Add automation to validate template usage
- [ ] Create template unit tests
- [ ] Document template versioning strategy

---

**Người tạo**: Claude Sonnet 4.6
**Người review**: TBD
**Next review**: Khi cập nhật xong tất cả scripts
