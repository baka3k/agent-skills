---
description: Detect core technologies, build systems, CI/CD pipelines, deployment targets, and platform assumptions by combining mind_mcp project knowledge with graph_mcp semantic code evidence.
variables:
  input:
    - name: $REPO_ROOT
      source: CLI --repo-root
      required: true
    - name: $TARGET_ENV
      source: CLI --env (default: auto; options: local, container, cloud, hybrid, auto)
      required: false
    - name: $DEPTH
      source: CLI --depth (default: standard; options: quick, standard, deep)
      required: false
  preflight:
    - name: build-report
      source: output file (write)
      required: true
    - name: tech-stack
      source: output file (write)
      required: true
handoffs:
  - label: Generate Module Summary Report
    agent: hi.module-summary-report
    prompt: |
      Tổng hợp findings thành architecture summary.
      Inventory: recon-data/module-inventory.json. Audit: audit-data/tech-stack.json.
      Repo: $REPO_ROOT.
  - label: Chain into Deep Discovery
    agent: hi.deep-codebase-discovery
    prompt: |
      Kết hợp tech-build-audit output vào deep codebase discovery pipeline.
      Repo: $REPO_ROOT. Scope: full.
hooks:
  pre:
    - name: mcp-health-check
      description: Verify MCP Graph + Mind connectivity
      timeout: 15s
      required: true
    - name: input-validation
      description: Validate repo path, target environment, depth parameters
      scope: ["repo_root", "target_env", "depth"]
      enable_redaction: true
  post:
    - name: validate-outputs
      description: Verify all required output files were generated
      required_files:
        - audit-data/build-report.md
        - audit-data/tech-stack.json
        - audit-data/ci-cd-pipelines.md
---

# Tech Build Audit Agent

> **Version:** 2.0  
> **Date:** 2026-05-19  
> **Purpose:** Phân tích stack công nghệ, build system, CI/CD, deployment targets của một repository.

---

## User Input

```text
$ARGUMENTS
```

Bạn **PHẢI** xem xét input của user trước khi thực hiện (nếu không rỗng).

---

## 🎯 What This Agent Does

Agent này phân tích toàn bộ khía cạnh kỹ thuật liên quan đến build và deployment:

1. **Knowledge Retrieval (mind_mcp)**: Lấy context về tech stack từ knowledge base
2. **Build Surface Analysis (graph_mcp)**: Phân tích build files, dependency graphs
3. **Filesystem Audit**: Scan cấu trúc build configs (Docker, CI/CD, package managers)
4. **Platform Classification**: Xác định deployment targets (cloud, container, hybrid)

---

## When To Use

- Cần bức tranh reliable về tech stack, build commands, deployment surfaces
- Đang validate onboarding docs hoặc chuẩn bị migration/build stabilization
- Cần API-layer dependency guardrails và build/runtime risk signals
- Đang audit deployment configurations và CI/CD pipelines
- Cần document platform assumptions cho cloud/container migrations

## Avoid Using When

- Chỉ cần module ownership/entry-point mapping (dùng repo-recon)
- Chỉ cần high-level summary (dùng module-summary-report)
- Chỉ focus vào một bug's blast radius (dùng bug-impact-analyzer)
- Chỉ cần architectural decision records (dùng deep-codebase-discovery)

---

## Input Parameters

| Parameter   | Required | Default | Description                                                |
|-------------|----------|---------|------------------------------------------------------------|
| `--repo-root`| Yes      | —       | Đường dẫn tuyệt đối tới repository                          |
| `--env`      | No       | `auto`  | Target environment: local, container, cloud, hybrid, auto  |
| `--depth`    | No       | `standard`| Độ sâu: quick, standard, deep                            |

---

## Output Location

Tất cả output được tạo trong `audit-data/`.

```
<workspace>/
└── audit-data/
    ├── build-report.md            # Build system analysis + commands
    ├── tech-stack.json            # Core technologies, frameworks, versions
    ├── ci-cd-pipelines.md         # CI/CD pipeline analysis
    ├── platform-targets.md        # Deployment targets & platform assumptions
    └── api-dependencies.md        # (deep) API-layer dependency analysis
```

---

## Depth Levels

| Level    | Scope                                                              |
|----------|--------------------------------------------------------------------|
| `quick`   | Build commands và basic platform detection                         |
| `standard`| Build commands, CI/CD, platform detection, configs                |
| `deep`    | Tất cả standard + API dependency analysis và runtime tracing      |

---

## Target Environment

| Env         | Phân tích bổ sung                                              |
|-------------|-----------------------------------------------------------------|
| `local`      | Local dev setup, environment variables, port mapping            |
| `container`  | Dockerfile, docker-compose, container registry, image sizes     |
| `cloud`      | Cloud deploy configs (K8s, App Service, Lambda, Cloud Run...)  |
| `hybrid`     | Kết hợp container + cloud                                       |
| `auto`       | Tự động phát hiện từ cấu trúc repo                              |

---

## Sensitive Data Handling

Mọi output đều được redact tự động:

- API keys, passwords, secrets, tokens → `[REDACTED_*]`
- Cloud keys (AWS/GCP/Azure), Docker registry URLs → `[REDACTED_*]`
- Connection strings, IP addresses, emails → `[REDACTED_*]`
- `.env` files: giữ key, redact value
