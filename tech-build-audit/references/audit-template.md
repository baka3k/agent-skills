# Tech/Build Audit Template

## 1) Snapshot

- Repository:
- Commit/branch:
- Scan date:
- Audit scope:

## 2) Technology Matrix

| Area | Detected | Evidence | Confidence |
|---|---|---|---|
| Language/runtime | | | high/medium/low |
| Framework | | | high/medium/low |
| Package/build system | | | high/medium/low |
| CI/CD | | | high/medium/low |
| Deployment target | | | high/medium/low |

## 3) Build and Test Commands

| Ecosystem | Command | Source | Status |
|---|---|---|---|
| Node | `npm run build` | package.json | confirmed/inferred |
| Python | `python -m pytest` | pyproject/requirements | confirmed/inferred |

## 4) Platform Targets

- Web:
- API:
- Worker/batch:
- Mobile:
- Desktop:
- Container/Kubernetes:

## 5) Risks and Unknowns

| Topic | Risk | Evidence Gap | Recommended Probe |
|---|---|---|---|
| Build reproducibility | low/medium/high | | |
| Release pipeline | low/medium/high | | |

## 6) API Dependency Warnings

| Severity | Warning | Path | Evidence Type | Recommendation |
|---|---|---|---|---|
| high/medium/low | API calls driver directly / service coupled to framework | | graph_mcp/filesystem | |
