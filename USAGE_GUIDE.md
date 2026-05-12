# Agent Skills Kit — Usage Guide

Detailed usage instructions for the 20 skills in the Agent Skills Kit.

---

## 📥 Installation

### Method 1: npm (Recommended)

```bash
npx @hyper_dev/skills

```

Or install globally:

```bash
npm install -g @hyper_dev/skills
hyper-dev-skills

```

### Method 2: Local Script

```bash
git clone https://github.com/hyper-dev/agent-skill.git
cd agent-skill
./scripts/install.sh

```

### Method 3: Python Installer

```bash
python scripts/install_agent_kit_with_templates.py --agent claude-code

```

---

## 🎯 Orchestration Skills

### 1. **bidding-orchestrator** — Hybrid Project Bidding

**Purpose:** Generate a complete proposal including estimation, staffing plan, and slide deck.

**When to use:**

* You need a full bid package: effort range, cost range, staffing, and slides.
* You need to compare fixed-price vs. T&M scenarios.
* You require citations from MCP evidence + web sources.

**Usage:**

```bash
# Input files
bidding-orchestrator/contracts/bid_brief.yaml
bidding-orchestrator/contracts/evidence_config.yaml
bidding-orchestrator/contracts/rate_card.yaml

# Run
python bidding-orchestrator/scripts/generate_bid_package.py \
  --bid-brief bidding-orchestrator/contracts/bid_brief.yaml \
  --evidence-config bidding-orchestrator/contracts/evidence_config.yaml \
  --rate-card bidding-orchestrator/contracts/rate_card.yaml \
  --output-dir outputs

```

**Output:**

* `outputs/proposal/proposal.md` — Proposal document
* `outputs/estimate/estimate_summary.json` — Cost & effort ranges
* `outputs/staffing/staffing_plan.md` — Phased staffing strategy
* `outputs/quality/quality_gates.md` — Lifecycle quality checklist
* `outputs/slides/bid_deck.pptx` — Presentation deck

**Skill dependencies:** bid-evidence-hub → bid-solution-designer → bid-estimator → bid-staffing-planner → bid-quality-gates → bid-slide-factory

---

### 2. **deep-codebase-discovery** — Full Technical Assessment

**Purpose:** Comprehensive codebase exploration: module mapping, stack analysis, critical flows, and risks.

**When to use:**

* Onboarding into a large or new codebase.
* End-to-end technical assessment is required.
* Preparing for architecture reviews, migration assessments, or handovers.
* You need a synthesized output from recon + build audit + summary.

**Usage:**

```bash
# CLI (via Claude Code, Cursor, Copilot)
/deep-codebase-discovery

# Arguments
--repo-root /path/to/repo
--project-id my-project
--scope full  # or: backend, frontend, infra, focused
--audience engineering  # or: management, mixed

```

**Input validation:**

* Repository path: must exist, be readable, and no path traversal.
* Project ID: alphanumeric + hyphens/underscores, max 100 chars.
* Scope: must be one of [full, backend, frontend, infra, focused].

**Output:**

* `discovery-data/module-inventory.md` — List of modules
* `discovery-data/entry-points.md` — API/CLI entry points
* `discovery-data/tech-stack.md` — Technology stack analysis
* `discovery-data/critical-flows.md` — Key data/control flows
* `discovery-data/risks.md` — Priority risks & recommendations
* `discovery-bundle.zip` — All artifacts

**MCP requirements:** mind_mcp (port 8789), graph_mcp (port 8788)

---

## 📊 Analysis Skills

### 3. **bid-evidence-hub** — Evidence Aggregation for Bidding

**Purpose:** Gather evidence from mind_mcp, graph_mcp, and web sources to inform bid decisions.

**When to use:**

* You need evidence-backed estimation.
* You need to cite sources for assumptions.
* You need to conduct research before deciding on staffing or scope.

**Usage:**

```bash
python bid-evidence-hub/scripts/aggregate_evidence.py \
  --evidence-config evidence_config.yaml \
  --output evidence_log.json

```

**Output:**

* `evidence_log.json` — List of evidence + sources + confidence scores

---

### 4. **bid-quality-gates** — Proposal Lifecycle QA

**Purpose:** Validate the complete proposal through 5 lifecycle gates.

**When to use:**

* Before submitting a proposal.
* You need a QA checklist to ensure scope clarity, architecture readiness, and estimation confidence.
* You want to optimize proposal quality.

**Usage:**

```bash
# Input
proposal_draft.md
architecture_diagram.md

# Gate checks
- Gate 1: Scope Clarity (scope definitions clear? stakeholders aligned?)
- Gate 2: Architecture Readiness (design finalized? tradeoffs documented?)
- Gate 3: Estimation Confidence (effort/cost justified? risks quantified?)
- Gate 4: Delivery Readiness (team available? dependencies clear?)
- Gate 5: Production Readiness (monitoring? runbooks? security?)

```

**Output:**

* Quality gates report with pass/fail + remediation steps

---

### 5. **bid-estimator** — Hybrid Cost & Effort Estimation

**Purpose:** Calculate best/base/worst case effort (person-months) + cost (fixed-price/T&M).

**When to use:**

* You need an effort range for a proposal.
* You need both fixed-price and T&M scenarios.
* You need complexity-weighted estimates.

**Usage:**

```bash
# Input: work breakdown structure (WBS)
{
  "projects": [
    {
      "id": "p1",
      "name": "Backend API",
      "complexity": 3,  # 1-5 scale
      "stories": 40,
      "riskFactor": 1.2
    }
  ]
}

# Output
{
  "effort": {
    "best": 6,      # person-months
    "base": 8,
    "worst": 12
  },
  "fixed_price": {
    "low": 240000,  # USD
    "mid": 320000,
    "high": 480000
  }
}

```

---

### 6. **bug-impact-analyzer** — Bug Analysis & Scope Assessment

**Purpose:** Analyze bugs: severity, reach, fix complexity, and regression scope.

**When to use:**

* Triaging bugs: understanding bug severity + impact radius.
* You need evidence citations (file paths, call graphs).
* You need to estimate fix complexity + regression risk.

**Usage:**

```bash
/bug-impact-analyzer

# Input
--bug-id issue-123
--repo-root /path/to/repo
--scope full  # local, module, system, full

```

**Output:**

* Bug classification (severity, impact tier)
* Call graph tracing: where the bug affects the system
* Fix complexity estimate (simple, medium, complex)
* Regression risk assessment
* Evidence citations

---

### 7. **knows** — Unified Evidence Retrieval

**Purpose:** Answer questions with citations from Git history + MCP + memory files.

**When to use:**

* "Why was this changed?"
* "What impacts this function?"
* You need architectural context with citations.
* You need historical context + graph + notes.

**Usage:**

```bash
/knows

# Input
--question "Why did we choose this architecture?"
--focus-hint src/api/handler.ts
--evidence-sources git,mcp,memory

# Output: Answer + Evidence log (citations + confidence)

```

**Evidence hierarchy:**

1. Git context (commit history, blame)
2. MCP context (mind_mcp project knowledge, graph_mcp call graphs)
3. Memory files (memory.md, agent.md, claude/cursor notes)

---

### 8. **repo-recon** — Repository Structure Analysis

**Purpose:** Map modules, entry points, and runtime surfaces of an unfamiliar codebase.

**When to use:**

* Onboarding into a new codebase.
* Preparing for an architecture review.
* Creating handover documentation.
* You need a module inventory + entry-point map.

**Usage:**

```bash
/repo-recon

# Arguments
--repo-root /path/to/repo
--focus backend  # all, backend, frontend, infra, data
--depth standard  # quick, standard, deep

```

**Output:**

* Module inventory (folder structure + responsibilities)
* Entry points (CLI commands, HTTP endpoints, APIs)
* Runtime surfaces (configurations, environment vars)
* Critical paths (main flows)

---

### 9. **tech-build-audit** — Stack & Build System Analysis

**Purpose:** Detect technologies, build systems, CI/CD pipelines, and deployment targets.

**When to use:**

* You need to document an unknown project stack.
* Preparing for migration planning.
* Validating onboarding docs.
* Estimating build & runtime risks.

**Usage:**

```bash
/tech-build-audit

# Arguments
--repo-root /path/to/repo
--target-env local  # local, container, cloud, hybrid
--depth standard  # quick, standard, deep

```

**Output:**

* **Core technologies:** Languages, frameworks, libraries
* **Build system:** Build tool, build commands, CI/CD
* **Deployment targets:** Container (Docker), Cloud (AWS/Azure), On-prem
* **Platform assumptions:** OS, runtime, network
* **API dependencies:** External services, webhooks, integrations
* **Risk classification:** Build risks, runtime risks, scalability risks

---

## 🔄 Synthesis Skills

### 10. **bid-solution-designer** — Baseline vs Optimized Solutions

**Purpose:** Design two solution options: baseline (minimal) + optimized (recommended).

**When to use:**

* You need to present multiple solution options.
* You need to document architecture tradeoffs.
* You need a cost-quality-timeline impact analysis.

**Usage:**

```bash
# Input: Requirements + constraints
{
  "scope": "Build SaaS dashboard",
  "constraints": ["budget: $100k", "timeline: 3 months"],
  "priority": ["performance", "security"]
}

# Output
- Solution A: Baseline (faster, lower cost)
- Solution B: Optimized (recommended, better long-term)
- Tradeoffs: cost, timeline, quality, scalability

```

---

### 11. **module-summary-report** — Architecture Summary

**Purpose:** Synthesize module findings into a concise architecture report (for engineering or management audiences).

**When to use:**

* You need to communicate codebase structure to stakeholders.
* You need to format output from repo-recon + tech-build-audit professionally.
* You need a readable, decision-focused report.

**Usage:**

```bash
/module-summary-report

# Input (from repo-recon + tech-build-audit)
--modules modules.json
--stack stack.json
--audience engineering  # engineering, management, mixed

```

**Output:**

* Module summaries (responsibilities, tech stack, risks)
* System-level narrative (architecture, data flow, deployment)
* Key decisions + tradeoffs
* Prioritized risks + recommendations

---

## 📖 Documentation Skills

### 12. **reverse-doc-reconstruction** — Generate Docs from Code

**Purpose:** Reverse engineer documentation from source code: entry points, call flows, and domain entities.

**When to use:**

* Codebase has no docs (legacy systems).
* You need to rebuild missing specifications.
* You need migration-ready docs from implementation-first systems.

**Usage:**

```bash
/reverse-doc-reconstruction

# Arguments
--repo-root /path/to/repo
--output-dir ./docs/generated
--module my-module
--depth deep  # quick, deep

# Output
docs/generated/
├── 00_requirements.md        # Inferred requirements
├── 01_usecases/              # Use cases from code flow
│   ├── usecase_1.md
│   └── usecase_2.md
├── 02_detail_design/         # Design from implementation
│   ├── api_design.md
│   ├── data_design.md
│   └── flow_design.md
└── 03_architecture.md        # System architecture

```

---

### 13. **bid-slide-factory** — Generate Bid Presentation Deck

**Purpose:** Create slides for a bid presentation from proposal artifacts.

**When to use:**

* You need a professional presentation deck.
* You need to present a proposal to a client.
* You need to convert proposal + estimates into a visual format.

**Usage:**

```bash
python bid-slide-factory/scripts/generate_slides.py \
  --proposal proposal.md \
  --estimate estimate.json \
  --staffing staffing.md \
  --output bid_deck.pptx

```

**Output:**

* `bid_deck.pptx` — PowerPoint slides
* Fallback: `bid_deck.md` (if PPTX is unavailable)

---

## 🔧 Porting Skills

### 14. **legacy-cpp-porting-guardrails** — Safe C++ to Modern Language Porting

**Purpose:** Port large legacy C++ files with behavior preservation, slice-by-slice migration, and parity tests.

**When to use:**

* Files are thousands of lines, functions are hundreds to thousands of lines.
* Stateful/side-effect-heavy logic is present.
* Existing tests are weak or missing.

**Usage:**

```bash
/legacy-cpp-porting-guardrails

# Arguments
--source-file legacy.cpp
--target-language java  # java, python, rust
--build-command-legacy "g++ legacy.cpp"
--build-command-target "mvn build"

# Workflow
1. MCP context discovery
2. Scope analysis (call graph)
3. Behavior contract extraction
4. Golden parity harness generation (test baseline)
5. Slice-by-slice porting

```

---

### 15. **cpp-java-migration-planner** — C++ → Java Dependency-Aware Planning

**Purpose:** Plan migration order: compute dependency-aware module/file/function waves.

**When to use:**

* You need a structured migration order.
* You need to reduce cycle dependencies.
* You need a risk-scored execution plan.

**Usage:**

```bash
/cpp-java-migration-planner

# Arguments
--source-repo /path/to/cpp/repo
--target-language java

# Output
migration_plan.md
├── Wave 1 (no dependencies)
│   ├── Module A (low risk)
│   ├── Module B (low risk)
├── Wave 2 (depends on Wave 1)
│   ├── Module C (medium risk)
└── Wave 3 (final integration)
    └── Main Module (high risk)

```

---

### 16. **cpp-java-pre-porting** — Pre-porting Analysis

**Purpose:** Perform pre-porting analysis + compatibility gap inventory + compat-layer design.

**When to use:**

* Before starting the porting process.
* You need to understand compatibility gaps.
* You need to design a compat-layer strategy.

**Usage:**

```bash
/cpp-java-pre-porting

# Input: C++ source files

# Output
compat_analysis.md
├── C++ features → Java mappings
├── Compatibility gaps
├── Compat-layer design recommendations
├── Type mapping table
├── Migration roadmap
└── Risk assessment

```

---

### 17. **cpp-java-file-structure-porting** — 1:1 File Skeleton Migration

**Purpose:** Port file structure from C++ to Java: 1:1 package/class/function name mapping.

**When to use:**

* File-level porting phase.
* You need strict name preservation.
* You need dependency-aware task breakdown.

**Usage:**

```bash
/cpp-java-file-structure-porting

# Arguments
--source-file MyClass.cpp
--target-language java

# Output
MyClass.java (skeleton)
├── Package structure (preserved)
├── Class structure (preserved)
├── Function signatures (preserved)
└── Dependency list + task breakdown

```

---

### 18. **cpp-java-function-porting** — 1:1 Function Conversion

**Purpose:** Port individual functions from C++ to Java with 1:1 name preservation and dependency analysis.

**When to use:**

* Function-level porting phase.
* You need to understand function dependencies.
* You need function-level migration tasks.

**Usage:**

```bash
/cpp-java-function-porting

# Arguments
--source-file MyClass.cpp
--function-name calculatePrice

# Output
Function migration task
├── Type mappings
├── Dependency list
├── Implementation strategy
└── Compatibility notes

```

---

### 19. **cpp-java-porting-orchestrator** — End-to-End C++ → Java Orchestration

**Purpose:** Orchestrate full C++ → Java migration: pre-porting → file → function → parity tests.

**When to use:**

* Complete C++ → Java migration.
* You need a structured, staged approach.
* You need parity-focused checkpoints.

**Usage:**

```bash
/cpp-java-porting-orchestrator

# Arguments
--source-repo /path/to/cpp
--target-repo /path/to/java
--scope full

# Phases
1. Pre-porting analysis
2. File structure porting
3. Function porting
4. Legacy guardrails + parity tests
5. Migration validation

```

---

### 20. **bid-staffing-planner** — Phase-Based Staffing Strategy

**Purpose:** Generate staffing plan by phase: Discovery, Foundation, Build, UAT, Go-live.

**When to use:**

* You need a staffing strategy for a bid.
* You need team composition per phase.
* You need resource planning.

**Usage:**

```bash
python bid-staffing-planner/scripts/generate_staffing.py \
  --estimate estimate.json \
  --duration-months 12 \
  --output staffing_plan.md

# Output
Staffing Plan
├── Discovery (Month 1-2): 2 architects, 1 PM
├── Foundation (Month 3-4): 1 architect, 3 engineers, 1 DevOps
├── Build (Month 5-10): 5 engineers, 2 QA, 1 DevOps
├── UAT (Month 11): 2 engineers, 2 QA
└── Go-live (Month 12): 1 architect, 2 engineers, 1 DevOps

```

---

## 🚀 Quick Reference by Use Case

### "Need a complete bid package"

1. Setup: `contracts/bid_brief.yaml`, `contracts/evidence_config.yaml`
2. Run: `/bidding-orchestrator`
3. Output: proposal.md + estimate + staffing + slides

### "Need to understand a new codebase"

1. Run: `/deep-codebase-discovery --scope full`
2. Output: Module map + tech stack + critical flows + risks

### "Need to find bug impact"

1. Run: `/bug-impact-analyzer --bug-id issue-123`
2. Output: Impact scope + fix complexity + regression risk

### "Need to port C++ → Java"

1. Run: `/cpp-java-porting-orchestrator --source-repo <path>`
2. Phases: Pre-analysis → File porting → Function porting → Validation

### "Need documentation from code"

1. Run: `/reverse-doc-reconstruction --repo-root <path> --depth deep`
2. Output: Requirements + Use cases + Design + Architecture

---

## 🔗 Chaining Skills

**Recommended workflows:**

```
Bidding workflow:
bidding-orchestrator 
  → bid-evidence-hub 
  → bid-solution-designer 
  → bid-estimator 
  → bid-staffing-planner 
  → bid-quality-gates 
  → bid-slide-factory

Discovery workflow:
deep-codebase-discovery 
  → repo-recon 
  → tech-build-audit 
  → module-summary-report

Migration workflow:
cpp-java-porting-orchestrator 
  → cpp-java-pre-porting 
  → cpp-java-migration-planner 
  → cpp-java-file-structure-porting 
  → cpp-java-function-porting 
  → legacy-cpp-porting-guardrails

```

---

## 📝 Input Validation & Security

* **Path validation**: No path traversal (`../`), readable, within scope.
* **Project ID**: Alphanumeric + hyphens/underscores, max 100 chars.
* **Scope**: Must match predefined set (full, backend, frontend, etc.).
* **Evidence sources**: Validate against available MCP databases.
* **Rate cards**: Optional; estimates still produced if missing.

---

## 🆘 Troubleshooting

### MCP Connection Error

```bash
# Check if MCP servers running
lsof -i :8788  # graph_mcp
lsof -i :8789  # mind_mcp

# Restart MCP servers (hyper-pack)
make stop && make start

```

### Skill Not Found

```bash
# Verify installation
ls ~/.claude/skills/  # for Claude Code
cat .github/skills/*/SKILL.md  # for Copilot

```

### Output Directory Error

```bash
# Create output directory
mkdir -p outputs
chmod 755 outputs

```

---

## 📞 Support

* Issues: GitHub Issues in `hyper-dev/agent-skill`
* Documentation: See individual `*/SKILL.md` files
* Examples: Check `*/examples/` directories