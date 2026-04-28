# Skill Selection Guide - Tìm Hiểu Codebase

**Câu hỏi**: Tôi muốn tìm hiểu codebase dự án thì dùng skill nào?
**Trả lời**: Tùy thuộc vào mục đích cụ thể của bạn.

---

## 🎯 Decision Tree - Chọn Skill Phù Hợp

### Câu 1: Mục đích chính của bạn là gì?

#### A. Onboarding lần đầu, cần hiểu tổng quan hoàn chỉnh
→ **Dùng: `deep-codebase-discovery`** ⭐ RECOMMENDED

**Khi dùng**:
- Lần đầu tiếp xúc với codebase lớn/unfamiliar
- Cần đánh giá kỹ thuật toàn diện (cấu trúc, stack, flows, risks)
- Cần một output duy nhất kết hợp recon + build audit + summary
- Chuẩn bị architecture review, handover documentation, migration assessment
- Build understanding cho team members hoặc stakeholders mới

**Kết quả**:
```
1. Module mapping (repo-recon)
2. Stack/build/platform analysis (tech-build-audit)
3. Architecture summary (module-summary-report)
→ Một comprehensive discovery bundle
```

**Command**:
```bash
/skill deep-codebase-discovery

# Hoặc với Claude Code
/skill deep-codebase-discovery /path/to/repo --scope full
```

**Thông tin define ở**:
- `deep-codebase-discovery/SKILL.md` - Line 14-18 ("## When To Use")

---

#### B.1. Cần cấu trúc module và entry points nhanh
→ **Dùng: `repo-recon`**

**Khi dùng**:
- Cần hiểu cấu trúc nhanh của repository mới
- Cần module boundaries và entry points trước khi phân tích sâu
- Chuẩn bị cho refactor/audit/documentation
- Onboarding codebase không có documentation
- Cần tạo handover documentation hoặc architecture reviews

**Kết quả**:
```
- Module inventory
- Entry point map
- Integration boundaries
- Top-level structure
```

**Command**:
```bash
/skill repo-recon /path/to/repo --scope backend
```

**Thông tin define ở**:
- `repo-recon/SKILL.md` - Line 14-18 ("## When To Use")

---

#### B.2. Cần hiểu tech stack và build system
→ **Dùng: `tech-build-audit`**

**Khi dùng**:
- Cần detect core technologies, frameworks
- Cần hiểu build system, CI/CD pipeline
- Cần biết deployment targets
- Documentation tech stack bị thiếu hoặc outdated
- Chuẩn bị migration hoặc validating onboarding docs

**Kết quả**:
```
- Technology matrix
- Build commands
- Platform targets
- Tech stack risks
```

**Command**:
```bash
/skill tech-build-audit /path/to/repo
```

**Thông tin define ở**:
- `tech-build-audit/SKILL.md` - Line 14-19 ("## When To Use")

---

#### B.3. Đã có findings, cần summary cho stakeholders
→ **Dùng: `module-summary-report`**

**Khi dùng**:
- Đã có repo-recon và tech-build-audit findings
- Stakeholders cần summary ngắn gọn, actionable
- Cần reconcile evidence từ MCP thành readable narrative
- Cần architecture summary cho technical handover
- Cần executive summary với next steps

**Kết quả**:
```
- Decision-ready summary
- Module responsibilities
- Risk assessment
- Actionable next steps
```

**Command**:
```bash
/skill module-summary-report
```

**Thông tin define ở**:
- `module-summary-report/SKILL.md` - Line 14-18 ("## When To Use")

---

## 📊 Comparison Table

| Skill | Mục đích | Input | Output | Thời gian |
|-------|---------|-------|--------|----------|
| **deep-codebase-discovery** | Comprehensive understanding | Repo path | Full bundle (recon + audit + summary) | ~15 min |
| **repo-recon** | Structure & modules | Repo path | Module inventory | ~3 min |
| **tech-build-audit** | Tech stack & build | Repo path | Tech matrix | ~3 min |
| **module-summary-report** | Synthesis & summary | Recon + audit findings | Executive summary | ~5 min |

---

## 🗂️ Thông Tin Define Ở Đâu?

### 1. Trong từng SKILL.md file

Mỗi skill đều có section **"## When To Use"** ngay đầu file:

```
deep-codebase-discovery/SKILL.md      → Line 12-18
repo-recon/SKILL.md                    → Line 12-18
tech-build-audit/SKILL.md              → Line 12-19
module-summary-report/SKILL.md         → Line 12-18
bug-impact-analyzer/SKILL.md           → Line 12-20
reverse-doc-reconstruction/SKILL.md    → Line 12-18
legacy-cpp-porting-guardrails/SKILL.md → Line 14-22
```

### 2. Trong README.md

| Section | Line | Content |
|---------|------|---------|
| **7 Agent Skills** table | 21-29 | Description & Category của mỗi skill |
| **Multi-Platform Support** table | 33-39 | Installation & Usage |

### 3. Trong QUICK_START.md

Các use cases và examples cho từng skill.

### 4. Trong MANIFEST.json

Metadata của mỗi skill:
```json
{
  "name": "deep-codebase-discovery",
  "description": "Orchestrator cho full pipeline discovery",
  "category": "Orchestration",
  "when_to_use": [...]
}
```

---

## 🎖️ Recommended Workflow

### Scenario 1: Onboarding Lần Đầu (Best Practice)

```
1. deep-codebase-discovery (COMPREHENSIVE)
   ↓
   Tự động chạy:
   - repo-recon (module mapping)
   - tech-build-audit (stack analysis)
   - module-summary-report (synthesis)
   ↓
   Output: Complete discovery bundle
```

**Command**:
```bash
/skill deep-codebase-discovery /path/to/repo --scope full
```

**Ưu điểm**:
- ✅ Một command duy nhất
- ✅ Full understanding
- ✅ Tự động kết hợp 3 skills

---

### Scenario 2: Step-by-Step (Flexible)

```
1. repo-recon
   → Module inventory

2. tech-build-audit
   → Tech stack

3. module-summary-report
   → Synthesis
```

**Commands**:
```bash
/skill repo-recon /path/to/repo
/skill tech-build-audit /path/to/repo
/skill module-summary-report
```

**Ưu điểm**:
- ✅ Control từng step
- ✅ Có thể pause giữa các step
- ✅ Deep dive vào từng area

---

## 📖 Quick Reference

### Tìm hiểu codebase → Dựa vào depth:

| Depth | Skill | Time |
|-------|-------|------|
| **Super quick** (2-3 min) | `repo-recon` | Module structure |
| **Quick** (2-3 min) | `tech-build-audit` | Tech stack |
| **Standard** (10 min) | `repo-recon` + `tech-build-audit` | Structure + Stack |
| **Comprehensive** (15 min) | `deep-codebase-discovery` | Everything ⭐ |

### Tìm hiểu codebase → Dựa vào role:

| Role | Recommended Skill |
|------|-------------------|
| **New developer** | `deep-codebase-discovery` |
| **Tech Lead** | `repo-recon` + `tech-build-audit` |
| **Architect** | `deep-codebase-discovery` |
| **Manager** | `module-summary-report` |
| **QA/Tester** | `tech-build-audit` + `bug-impact-analyzer` |

---

## 🔍 How to Find This Information

### Method 1: Read SKILL.md files

```bash
# Xem when to use của từng skill
cat deep-codebase-discovery/SKILL.md | grep -A 10 "## When To Use"
cat repo-recon/SKILL.md | grep -A 10 "## When To Use"
```

### Method 2: Check README.md

```bash
# Xem skill descriptions
cat README.md | grep -A 10 "## 📦 What's Included"
```

### Method 3: Use this guide

Bạn đang đọc: `SKILL_SELECTION_GUIDE.md` ✅

### Method 4: Ask Claude Code

```bash
# Trong Claude Code
/skill deep-codebase-discovery

# Hoặc hỏi trực tiếp
"Which skill should I use to understand this codebase?"
```

---

## 💡 Pro Tips

### Tip 1: Start with deep-codebase-discovery

Nếu không sure → Dùng `deep-codebase-discovery`:
- Comprehensive nhất
- Tự động kết hợp repo-recon + tech-build-audit + module-summary-report
- Một command → Full understanding

### Tip 2: Use repo-recon for quick structure

Nếu chỉ cần structure nhanh → Dùng `repo-recon`:
- 2-3 phút → Module inventory
- Entry points, integration boundaries
- Good for initial exploration

### Tip 3: Combine skills for deep understanding

```
repo-recon (structure)
  +
tech-build-audit (stack)
  +
module-summary-report (synthesis)
  =
deep-codebase-discovery (orchestrated)
```

---

## 🎯 Answer Summary

### Question: Muốn tìm hiểu codebase dự án thì dùng skill nào?

**Answer**:
1. **Best choice**: `deep-codebase-discovery` ⭐
   - Comprehensive, một command xong tất

2. **Flexible choice**: Combine `repo-recon` + `tech-build-audit` + `module-summary-report`
   - Step-by-step, control tốt hơn

### Question: Thông tin này define ở đâu?

**Answer**:
1. **Primary**: Mỗi skill's `SKILL.md` file → Section "## When To Use" (Line 12-18)
2. **Secondary**: `README.md` → "7 Agent Skills" table (Line 21-29)
3. **This Guide**: `SKILL_SELECTION_GUIDE.md` (comprehensive)

---

**Last Updated**: 2025-04-17
**Related Docs**:
- README.md - Skill descriptions
- QUICK_START.md - Usage examples
- Individual SKILL.md files - Detailed when to use
