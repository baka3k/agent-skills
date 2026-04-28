#!/usr/bin/env python3
"""Technology/build/platform auditor for repositories."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Set


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    ".cache",
}

ALLOWED_DOT_DIRS = {".github", ".devcontainer", ".vscode"}

CODE_FILE_EXTS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".java",
    ".kt",
    ".cs",
    ".vb",
    ".rb",
    ".php",
}

MAX_SCAN_BYTES = 1_500_000

API_LAYER_HINTS = {
    "api",
    "apis",
    "controller",
    "controllers",
    "handler",
    "handlers",
    "route",
    "routes",
    "endpoint",
    "endpoints",
    "rest",
    "graphql",
    "socket",
    "communication",
    "adapter",
    "gateway",
    "interface",
}

SERVICE_LAYER_HINTS = {
    "service",
    "services",
    "domain",
    "usecase",
    "usecases",
    "application",
    "core",
    "business",
}

DRIVER_PATTERNS = [
    ("python-db-driver", r"\b(psycopg2|sqlite3|pymysql|mysql\.connector|pymongo|motor)\b"),
    ("python-low-level-sqlalchemy", r"\b(sqlalchemy\.create_engine|sqlalchemy\.engine)\b"),
    ("node-db-driver", r"(require\(['\"](pg|mysql2|mongodb|oracledb|mariadb)['\"]\)|from ['\"](pg|mysql2|mongodb|oracledb|mariadb)['\"])"),
    ("go-db-driver", r"(import\s+\"database/sql\"|github\.com/jackc/pgx|go\.mongodb\.org/mongo-driver|github\.com/go-sql-driver/mysql)"),
    ("java-db-driver", r"\b(java\.sql\.|org\.postgresql|com\.mysql\.cj|com\.mongodb\.client)\b"),
    ("dotnet-db-driver", r"\b(npgsql|system\.data\.sqlclient|microsoft\.data\.sqlclient|mongodb\.driver|mysql\.data)\b"),
    ("dotnet-oracle-driver", r"\b(oracleconnection|oraclecommand|oracledatareader|oracleclient)\b"),
]

DIRECT_DB_OP_PATTERNS = [
    ("sql-execute", r"\b(cursor\s*\(|execute\s*\(|executemany\s*\(|preparestatement\s*\()"),
    ("connection-open", r"\b(connect\s*\(|create_engine\s*\(|opendb\s*\(|sql\.open\s*\()"),
    ("raw-query", r"\b(query\s*\(|raw\s*\(|queryrow\s*\()"),
    ("mongo-direct-op", r"\b(findone?\s*\(|insertone?\s*\(|insertmany\s*\(|updateone?\s*\(|deletemany\s*\()"),
    ("dotnet-datareader", r"\b(executereader|executenonquery|executescalar)\b"),
]

FRAMEWORK_PATTERNS = [
    ("fastapi", r"\bfrom\s+fastapi\b|\bfastapi\b"),
    ("flask", r"\bfrom\s+flask\b|\bflask\b"),
    ("django", r"\bdjango\."),
    ("express", r"\bexpress\b"),
    ("nestjs", r"\b@nestjs/|\bnestfactory\b"),
    ("spring-web", r"\borg\.springframework\.web\b|\b@restcontroller\b"),
    ("gin", r"\bgithub\.com/gin-gonic/gin\b"),
    ("fiber", r"\bgithub\.com/gofiber/fiber\b"),
    ("aspnet-core", r"\b(microsoft\.aspnetcore|controllerbase|minimalapi)\b"),
]


def should_skip_dir(dirname: str) -> bool:
    if dirname in IGNORED_DIRS:
        return True
    return dirname.startswith(".") and dirname not in ALLOWED_DOT_DIRS


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        current_path = Path(current)
        for filename in files:
            file_path = current_path / filename
            if file_path.is_symlink():
                continue
            yield file_path


def add_signal(store: Dict[str, Set[str]], key: str, value: str) -> None:
    store[key].add(value)


def add_evidence(evidence: List[Dict[str, str]], category: str, signal: str, rel: Path) -> None:
    evidence.append(
        {
            "category": category,
            "signal": signal,
            "path": rel.as_posix(),
        }
    )


def parse_makefile_targets(path: Path) -> List[str]:
    targets = []
    target_re = re.compile(r"^([A-Za-z0-9_.-]+)\s*:")
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line or line.startswith("\t") or line.startswith("#"):
                continue
            match = target_re.match(line)
            if not match:
                continue
            target = match.group(1)
            if target.startswith("."):
                continue
            targets.append(target)
    except OSError:
        return []
    return targets[:25]


def is_api_layer_path(rel: Path) -> bool:
    parts = [p.lower() for p in rel.parts]
    basename = rel.stem.lower()
    if any(hint in part for part in parts for hint in API_LAYER_HINTS):
        return True
    return any(
        hint in basename for hint in ("controller", "handler", "route", "endpoint")
    )


def is_service_layer_path(rel: Path) -> bool:
    parts = [p.lower() for p in rel.parts]
    basename = rel.stem.lower()
    if any(hint in part for part in parts for hint in SERVICE_LAYER_HINTS):
        return True
    return any(hint in basename for hint in ("service", "usecase", "domain"))


def read_text_safe(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_SCAN_BYTES:
            return ""
    except OSError:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def detect_api_dependency_warnings(root: Path) -> List[Dict[str, object]]:
    warnings: List[Dict[str, object]] = []

    for file_path in iter_files(root):
        if file_path.suffix.lower() not in CODE_FILE_EXTS:
            continue
        rel = file_path.relative_to(root)
        text = read_text_safe(file_path)
        if not text:
            continue
        lower_text = text.lower()

        api_layer = is_api_layer_path(rel)
        service_layer = is_service_layer_path(rel)

        framework_hits = [
            label for label, pattern in FRAMEWORK_PATTERNS if re.search(pattern, lower_text)
        ]
        driver_hits = [
            label for label, pattern in DRIVER_PATTERNS if re.search(pattern, lower_text)
        ]
        db_op_hits = [
            label
            for label, pattern in DIRECT_DB_OP_PATTERNS
            if re.search(pattern, lower_text)
        ]

        if api_layer and (driver_hits or db_op_hits):
            severity = "high" if (driver_hits and db_op_hits) else "medium"
            warnings.append(
                {
                    "warning_id": "api-direct-driver-access",
                    "severity": severity,
                    "path": rel.as_posix(),
                    "title": "API layer may call database driver directly",
                    "evidence": sorted((driver_hits + db_op_hits)[:6]),
                    "recommendation": "Route API through service/repository boundary; keep driver usage out of controllers/handlers.",
                }
            )

        if service_layer and framework_hits:
            warnings.append(
                {
                    "warning_id": "service-layer-framework-coupling",
                    "severity": "medium",
                    "path": rel.as_posix(),
                    "title": "Service/domain layer may depend on web framework APIs",
                    "evidence": sorted(framework_hits[:6]),
                    "recommendation": "Move framework-specific concerns to API adapter layer and keep service/domain framework-agnostic.",
                }
            )

    # Stable ordering for reproducible output.
    warnings.sort(
        key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}.get(str(x.get("severity")), 9),
            str(x.get("path")),
            str(x.get("warning_id")),
        )
    )
    return warnings[:150]


def parse_package_json(path: Path, rel: Path, signals: Dict[str, Set[str]], evidence: List[Dict[str, str]], commands: Set[str]) -> None:
    try:
        package_data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        add_evidence(evidence, "parse", "invalid-package-json", rel)
        return

    add_signal(signals, "technologies", "Node.js")
    add_signal(signals, "build_systems", "npm-compatible")
    add_evidence(evidence, "manifest", "package.json", rel)

    deps = {}
    for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        section_data = package_data.get(section, {})
        if isinstance(section_data, dict):
            deps.update(section_data)

    framework_map = {
        "react": "React",
        "next": "Next.js",
        "vue": "Vue",
        "nuxt": "Nuxt",
        "@angular/core": "Angular",
        "svelte": "Svelte",
        "nestjs": "NestJS",
        "express": "Express",
        "fastify": "Fastify",
        "electron": "Electron",
        "react-native": "React Native",
    }
    for dep_name, framework in framework_map.items():
        if dep_name in deps:
            add_signal(signals, "frameworks", framework)
            add_evidence(evidence, "dependency", dep_name, rel)

    scripts = package_data.get("scripts", {})
    if isinstance(scripts, dict):
        for key in ("build", "test", "lint", "start", "dev", "ci"):
            if key in scripts:
                commands.add(f"npm run {key}")


def detect(root: Path) -> Dict:
    signals: Dict[str, Set[str]] = defaultdict(set)
    evidence: List[Dict[str, str]] = []
    commands: Set[str] = set()

    for file_path in iter_files(root):
        rel = file_path.relative_to(root)
        rel_posix = rel.as_posix()
        name = file_path.name
        name_lower = name.lower()

        if rel_posix.startswith(".github/workflows/") and file_path.suffix.lower() in {".yml", ".yaml"}:
            add_signal(signals, "ci_cd", "GitHub Actions")
            add_evidence(evidence, "ci_cd", "github-actions-workflow", rel)

        if name_lower == ".gitlab-ci.yml":
            add_signal(signals, "ci_cd", "GitLab CI")
            add_evidence(evidence, "ci_cd", "gitlab-ci", rel)
        if name == "Jenkinsfile":
            add_signal(signals, "ci_cd", "Jenkins")
            add_evidence(evidence, "ci_cd", "jenkinsfile", rel)
        if name_lower == "azure-pipelines.yml":
            add_signal(signals, "ci_cd", "Azure Pipelines")
            add_evidence(evidence, "ci_cd", "azure-pipelines", rel)
        if rel_posix.startswith(".circleci/") and name_lower == "config.yml":
            add_signal(signals, "ci_cd", "CircleCI")
            add_evidence(evidence, "ci_cd", "circleci-config", rel)

        if name_lower == "package.json":
            parse_package_json(file_path, rel, signals, evidence, commands)

        if name_lower in {"package-lock.json", "npm-shrinkwrap.json"}:
            add_signal(signals, "package_managers", "npm")
            add_evidence(evidence, "lockfile", "npm-lock", rel)
        if name_lower in {"yarn.lock", ".yarnrc.yml"}:
            add_signal(signals, "package_managers", "yarn")
            add_evidence(evidence, "lockfile", "yarn-lock", rel)
        if name_lower in {"pnpm-lock.yaml", "pnpm-workspace.yaml"}:
            add_signal(signals, "package_managers", "pnpm")
            add_evidence(evidence, "lockfile", "pnpm-lock", rel)
        if name_lower == "bun.lockb":
            add_signal(signals, "package_managers", "bun")
            add_evidence(evidence, "lockfile", "bun-lock", rel)

        if name_lower in {"requirements.txt", "pyproject.toml", "setup.py", "pipfile"}:
            add_signal(signals, "technologies", "Python")
            add_signal(signals, "build_systems", "pip/pyproject")
            add_evidence(evidence, "manifest", name_lower, rel)
            commands.add("python -m pytest")
            commands.add("python -m pip install -r requirements.txt")

        if name_lower == "go.mod":
            add_signal(signals, "technologies", "Go")
            add_signal(signals, "build_systems", "go toolchain")
            add_evidence(evidence, "manifest", "go.mod", rel)
            commands.add("go test ./...")
            commands.add("go build ./...")

        if name_lower == "cargo.toml":
            add_signal(signals, "technologies", "Rust")
            add_signal(signals, "build_systems", "cargo")
            add_evidence(evidence, "manifest", "cargo.toml", rel)
            commands.add("cargo test")
            commands.add("cargo build")

        if name_lower in {"pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"}:
            add_signal(signals, "technologies", "JVM")
            add_signal(signals, "build_systems", "maven/gradle")
            add_evidence(evidence, "manifest", name_lower, rel)
            commands.add("mvn test")
            commands.add("./gradlew test")

        if file_path.suffix.lower() in {".csproj", ".sln"}:
            add_signal(signals, "technologies", ".NET")
            add_signal(signals, "build_systems", "dotnet")
            add_evidence(evidence, "manifest", file_path.suffix.lower(), rel)
            commands.add("dotnet build")
            commands.add("dotnet test")

        if name == "Makefile" or name_lower == "makefile":
            add_signal(signals, "build_systems", "make")
            add_evidence(evidence, "manifest", "makefile", rel)
            targets = parse_makefile_targets(file_path)
            for target in ("build", "test", "lint"):
                if target in targets:
                    commands.add(f"make {target}")

        if name_lower == "cmakelists.txt":
            add_signal(signals, "build_systems", "cmake")
            add_evidence(evidence, "manifest", "cmakelists.txt", rel)

        if name.startswith("Dockerfile") or name_lower in {"docker-compose.yml", "docker-compose.yaml"}:
            add_signal(signals, "platform_targets", "Container")
            add_signal(signals, "deploy_targets", "Docker")
            add_evidence(evidence, "platform", "docker", rel)

        if file_path.suffix.lower() in {".yaml", ".yml"}:
            if any(token in name_lower for token in ("deployment", "service", "ingress", "kustomization")):
                add_signal(signals, "deploy_targets", "Kubernetes")
                add_signal(signals, "platform_targets", "Container Orchestrated")
                add_evidence(evidence, "platform", "kubernetes-manifest-hint", rel)
            if name_lower == "serverless.yml":
                add_signal(signals, "deploy_targets", "Serverless")
                add_evidence(evidence, "platform", "serverless", rel)

        if file_path.suffix.lower() == ".tf":
            add_signal(signals, "iac_tools", "Terraform")
            add_evidence(evidence, "iac", "terraform", rel)

        if name == "Pulumi.yaml":
            add_signal(signals, "iac_tools", "Pulumi")
            add_evidence(evidence, "iac", "pulumi", rel)

        if name_lower in {"vercel.json", "netlify.toml", "render.yaml", "fly.toml"}:
            mapping = {
                "vercel.json": "Vercel",
                "netlify.toml": "Netlify",
                "render.yaml": "Render",
                "fly.toml": "Fly.io",
            }
            add_signal(signals, "deploy_targets", mapping[name_lower])
            add_evidence(evidence, "platform", mapping[name_lower], rel)

        if name_lower in {"androidmanifest.xml", "build.gradle", "build.gradle.kts"} and "android" in rel_posix.lower():
            add_signal(signals, "platform_targets", "Android")
            add_evidence(evidence, "platform", "android", rel)
        if name_lower in {"podfile", "project.pbxproj"} or "ios/" in rel_posix.lower():
            add_signal(signals, "platform_targets", "iOS")
            add_evidence(evidence, "platform", "ios", rel)

    if "npm-compatible" in signals["build_systems"] and signals["package_managers"]:
        # Replace generic signal with concrete package managers when known.
        signals["build_systems"].discard("npm-compatible")
        for pm in sorted(signals["package_managers"]):
            signals["build_systems"].add(pm)

    api_warnings = detect_api_dependency_warnings(root)

    result = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "root": str(root.resolve()),
        "technologies": sorted(signals["technologies"]),
        "frameworks": sorted(signals["frameworks"]),
        "build_systems": sorted(signals["build_systems"]),
        "ci_cd": sorted(signals["ci_cd"]),
        "platform_targets": sorted(signals["platform_targets"]),
        "deploy_targets": sorted(signals["deploy_targets"]),
        "iac_tools": sorted(signals["iac_tools"]),
        "build_commands": sorted(commands),
        "api_dependency_warnings": api_warnings,
        "evidence": evidence[:300],
    }
    return result


def load_template(template_path: str) -> str:
    """Load template from file."""
    script_dir = Path(__file__).parent
    template_abs_path = script_dir.parent / "references" / template_path
    with open(template_abs_path, "r", encoding="utf-8") as f:
        return f.read()


def populate_template(template: str, data: Dict) -> str:
    """Populate audit template with scan data.

    Maps scan results to template sections:
    - Snapshot: Repository, scan date, scope
    - Technology Matrix: Languages, frameworks, build systems, CI/CD, deployment
    - Build and Test Commands: Detected build commands by ecosystem
    - Platform Targets: Web, API, worker, mobile, desktop, container/Kubernetes
    - Risks and Unknowns: Build reproducibility, release pipeline gaps
    - API Dependency Warnings: Framework coupling, direct driver access
    """
    lines = template.split("\n")
    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Section 1: Snapshot
        if line.strip().startswith("- Repository:"):
            output_lines.append(f"- Repository: `{data.get('root', 'N/A')}`")
        elif line.strip().startswith("- Commit/branch:"):
            output_lines.append(f"- Commit/branch: `{data.get('commit', 'N/A')}`")
        elif line.strip().startswith("- Scan date:"):
            output_lines.append(f"- Scan date: `{data.get('generated_at_utc', 'N/A')}`")
        elif line.strip().startswith("- Audit scope:"):
            output_lines.append(f"- Audit scope: `{data.get('scope', 'Full repository scan')}`")

        # Section 2: Technology Matrix
        elif line.strip() == "| Area | Detected | Evidence | Confidence |":
            output_lines.append(line)
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|")

            # Map technologies to areas
            areas = _build_technology_matrix(data)
            for area in areas:
                detected = area["detected"]
                evidence = area["evidence"]
                confidence = area["confidence"]
                output_lines.append(f"| {area['area']} | {detected} | {evidence} | {confidence} |")

            # Skip template rows
            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("|") or lines[i + 1].strip() == ""):
                i += 1

        # Section 3: Build and Test Commands
        elif line.strip() == "| Ecosystem | Command | Source | Status |":
            output_lines.append(line)
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|")

            commands = _build_command_table(data)
            for cmd in commands:
                output_lines.append(f"| {cmd['ecosystem']} | `{cmd['command']}` | {cmd['source']} | {cmd['status']} |")

            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("|") or lines[i + 1].strip() == ""):
                i += 1

        # Section 4: Platform Targets
        elif line.strip().startswith("- Web:"):
            targets = data.get("platform_targets", [])
            web = "✓" if any(t.lower() in ["web", "browser"] for t in targets) else ""
            output_lines.append(f"- Web: {web}")
        elif line.strip().startswith("- API:"):
            api = "✓" if any(t.lower() in ["api", "server"] for t in targets) else ""
            output_lines.append(f"- API: {api}")
        elif line.strip().startswith("- Worker/batch:"):
            worker = "✓" if any(t.lower() in ["worker", "batch", "job"] for t in targets) else ""
            output_lines.append(f"- Worker/batch: {worker}")
        elif line.strip().startswith("- Mobile:"):
            mobile = "✓" if any(t.lower() in ["android", "ios"] for t in targets) else ""
            output_lines.append(f"- Mobile: {mobile}")
        elif line.strip().startswith("- Desktop:"):
            desktop = "✓" if any(t.lower() in ["electron", "desktop"] for t in targets) else ""
            output_lines.append(f"- Desktop: {desktop}")
        elif line.strip().startswith("- Container/Kubernetes:"):
            container = "✓" if any(t.lower() in ["container", "kubernetes", "docker"] for t in targets) else ""
            output_lines.append(f"- Container/Kubernetes: {container}")

        # Section 5: Risks and Unknowns
        elif line.strip() == "| Topic | Risk | Evidence Gap | Recommended Probe |":
            output_lines.append(line)
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|")

            risks = _generate_risks(data)
            for risk in risks:
                output_lines.append(f"| {risk['topic']} | {risk['risk']} | {risk['evidence_gap']} | {risk['recommended_probe']} |")

            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("|") or lines[i + 1].strip() == ""):
                i += 1

        # Section 6: API Dependency Warnings
        elif line.strip() == "| Severity | Warning | Path | Evidence Type | Recommendation |":
            output_lines.append(line)
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith("|---"):
                output_lines.append("|---|---|---|---|---|")

            warnings = data.get("api_dependency_warnings", [])
            if warnings:
                for warning in warnings[:80]:
                    severity = warning.get("severity", "low")
                    title = warning.get("title", "")
                    path = warning.get("path", "")
                    evidence = ", ".join(warning.get("evidence", [])[:3])
                    recommendation = warning.get("recommendation", "")
                    output_lines.append(f"| {severity} | {title} | `{path}` | {evidence} | {recommendation} |")
            else:
                output_lines.append("| | | | | |")

            while i + 1 < len(lines) and (lines[i + 1].strip().startswith("|") or lines[i + 1].strip() == ""):
                i += 1

        else:
            output_lines.append(line)

        i += 1

    return "\n".join(output_lines)


def _build_technology_matrix(data: Dict) -> List[Dict]:
    """Build technology matrix rows for template."""
    technologies = data.get("technologies", [])
    frameworks = data.get("frameworks", [])
    build_systems = data.get("build_systems", [])
    ci_cd = data.get("ci_cd", [])
    deploy_targets = data.get("deploy_targets", [])

    rows = []

    # Language/runtime
    lang = ", ".join(technologies) if technologies else "Unknown"
    lang_confidence = "high" if technologies else "low"
    rows.append({
        "area": "Language/runtime",
        "detected": lang,
        "evidence": "Manifest files (package.json, pom.xml, etc.)",
        "confidence": lang_confidence
    })

    # Framework
    framework = ", ".join(frameworks) if frameworks else "None detected"
    framework_confidence = "high" if frameworks else "low"
    rows.append({
        "area": "Framework",
        "detected": framework,
        "evidence": "Dependency analysis" if frameworks else "No web framework signatures found",
        "confidence": framework_confidence
    })

    # Package/build system
    build_sys = ", ".join(build_systems) if build_systems else "Unknown"
    build_confidence = "high" if build_systems else "medium"
    rows.append({
        "area": "Package/build system",
        "detected": build_sys,
        "evidence": "Build configuration files",
        "confidence": build_confidence
    })

    # CI/CD
    cicd = ", ".join(ci_cd) if ci_cd else "None detected"
    cicd_confidence = "high" if ci_cd else "medium"
    rows.append({
        "area": "CI/CD",
        "detected": cicd,
        "evidence": "CI configuration files" if ci_cd else "No CI config detected",
        "confidence": cicd_confidence
    })

    # Deployment target
    deploy = ", ".join(deploy_targets) if deploy_targets else "Unknown"
    deploy_confidence = "high" if deploy_targets else "low"
    rows.append({
        "area": "Deployment target",
        "detected": deploy,
        "evidence": "Deployment configuration files",
        "confidence": deploy_confidence
    })

    return rows


def _build_command_table(data: Dict) -> List[Dict]:
    """Build command table rows for template."""
    commands = data.get("build_commands", [])
    techs = data.get("technologies", [])

    rows = []

    # Group commands by ecosystem
    if any("node" in t.lower() for t in techs):
        node_cmds = [c for c in commands if "npm" in c or "yarn" in c or "pnpm" in c or "bun" in c]
        for cmd in node_cmds[:3]:
            rows.append({
                "ecosystem": "Node",
                "command": cmd,
                "source": "package.json scripts",
                "status": "confirmed"
            })

    if any("python" in t.lower() for t in techs):
        py_cmds = [c for c in commands if "python" in c or "pytest" in c or "pip" in c]
        for cmd in py_cmds[:3]:
            rows.append({
                "ecosystem": "Python",
                "command": cmd,
                "source": "pyproject/requirements",
                "status": "inferred"
            })

    if any("go" in t.lower() for t in techs):
        go_cmds = [c for c in commands if "go" in c]
        for cmd in go_cmds[:2]:
            rows.append({
                "ecosystem": "Go",
                "command": cmd,
                "source": "go.mod",
                "status": "confirmed"
            })

    if any("rust" in t.lower() or "cargo" in c for c in commands for c in [c]):
        rust_cmds = [c for c in commands if "cargo" in c]
        for cmd in rust_cmds[:2]:
            rows.append({
                "ecosystem": "Rust",
                "command": cmd,
                "source": "Cargo.toml",
                "status": "confirmed"
            })

    if not rows:
        rows.append({
            "ecosystem": "Unknown",
            "command": "No commands detected",
            "source": "N/A",
            "status": "low"
        })

    return rows


def _generate_risks(data: Dict) -> List[Dict]:
    """Generate risk assessments based on scan data."""
    risks = []

    # Check for build reproducibility risks
    build_systems = data.get("build_systems", [])
    has_lock_file = any(lock in str(build_systems).lower() for lock in ["lock", "freeze", "clamp"])

    if not has_lock_file:
        risks.append({
            "topic": "Build reproducibility",
            "risk": "medium",
            "evidence_gap": "No dependency lock file detected",
            "recommended_probe": "Check for package-lock.json, requirements.txt, go.sum, Cargo.lock"
        })

    # Check for CI/CD gaps
    ci_cd = data.get("ci_cd", [])
    if not ci_cd:
        risks.append({
            "topic": "Release pipeline",
            "risk": "high",
            "evidence_gap": "No CI/CD configuration detected",
            "recommended_probe": "Look for .github/workflows/, .gitlab-ci.yml, Jenkinsfile in repository"
        })

    # Check for deployment configuration
    deploy_targets = data.get("deploy_targets", [])
    if not deploy_targets:
        risks.append({
            "topic": "Deployment strategy",
            "risk": "medium",
            "evidence_gap": "No deployment configuration detected",
            "recommended_probe": "Check for Dockerfile, docker-compose.yml, Kubernetes manifests"
        })

    # Check for API dependency warnings
    api_warnings = data.get("api_dependency_warnings", [])
    if api_warnings:
        high_severity = sum(1 for w in api_warnings if w.get("severity") == "high")
        if high_severity > 0:
            risks.append({
                "topic": "API layer architecture",
                "risk": "high",
                "evidence_gap": f"{high_severity} high-severity API dependency warnings detected",
                "recommended_probe": "Review API layer files for direct database driver access"
            })

    return risks


def to_markdown(data: Dict) -> str:
    """Generate markdown output using audit template."""
    template = load_template("audit-template.md")
    return populate_template(template, data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect technologies, build systems, and platform targets."
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository root path")
    parser.add_argument("--json", dest="json_out", help="Write JSON output to file")
    parser.add_argument("--md", dest="md_out", help="Write markdown output to file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Invalid repository path: {root}")

    data = detect(root)
    md = to_markdown(data)

    if args.json_out:
        Path(args.json_out).expanduser().write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )
    if args.md_out:
        Path(args.md_out).expanduser().write_text(md + "\n", encoding="utf-8")

    if not args.json_out and not args.md_out:
        print(json.dumps(data, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
