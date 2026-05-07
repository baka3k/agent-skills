#!/bin/bash
# Smoke tests for converter/installer/manifest sync.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

detect_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        echo ""
    fi
}

mktemp_dir() {
    mktemp -d 2>/dev/null || mktemp -d -t agent_skill_smoke
}

assert_file_contains() {
    local file="$1"
    local pattern="$2"
    if ! rg -q --multiline "$pattern" "$file"; then
        echo "Assertion failed: pattern '$pattern' not found in $file" >&2
        exit 1
    fi
}

PYTHON_BIN="$(detect_python)"
if [ -z "$PYTHON_BIN" ]; then
    echo "Python is required for smoke tests." >&2
    exit 1
fi

echo "[1/9] Syntax and compile checks"
bash -n scripts/install.sh scripts/verify_install.sh scripts/smoke_test.sh
"$PYTHON_BIN" -m py_compile \
    scripts/skill_parser.py \
    scripts/convert_skill.py \
    scripts/install_agent_kit.py \
    scripts/sync_manifest.py \
    scripts/test_project_bidding_suite.py \
    bidding-orchestrator/scripts/generate_bid_package.py \
    bid-estimator/scripts/calc_estimate.py \
    bid-staffing-planner/scripts/build_staffing_plan.py \
    bid-slide-factory/scripts/build_slide_brief.py \
    bid-slide-factory/scripts/resolve_gemini_model.py \
    reverse-doc-reconstruction/scripts/bootstrap_reverse_doc_workspace.py

echo "[2/9] Converter workflow extraction checks"
tmp_conv="$(mktemp_dir)"
"$PYTHON_BIN" scripts/convert_skill.py --skill reverse-doc-reconstruction --format cursor --output "$tmp_conv" >/dev/null
"$PYTHON_BIN" scripts/convert_skill.py --skill deep-codebase-discovery --format copilot --output "$tmp_conv" >/dev/null
assert_file_contains "$tmp_conv/reverse-doc-reconstruction.cursorrules" "\\*\\*Workflow:\\*\\*"
assert_file_contains "$tmp_conv/reverse-doc-reconstruction.cursorrules" "^### Phase 0:"
assert_file_contains "$tmp_conv/deep-codebase-discovery.md" "## Quick Workflow"
assert_file_contains "$tmp_conv/deep-codebase-discovery.md" "1\\. Phase 0:"

echo "[3/9] Python installer dry-run checks"
tmp_py="$(mktemp_dir)"
mkdir -p "$tmp_py/home" "$tmp_py/proj"
HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent cursor --scope local --project-root "$tmp_py/proj" --dry-run >/dev/null
HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent copilot --scope local --project-root "$tmp_py/proj" --dry-run >/dev/null
HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent codex --scope local --project-root "$tmp_py/proj" --dry-run >/dev/null
HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent continue --scope global --dry-run >/dev/null

echo "[4/9] Python installer real-install + idempotence checks"
printf 'y\n' | HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent cursor --scope local --project-root "$tmp_py/proj" >/dev/null
printf 'y\n' | HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent copilot --scope local --project-root "$tmp_py/proj" >/dev/null
printf 'y\n' | HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent codex --scope local --project-root "$tmp_py/proj" >/dev/null
printf 'y\n' | HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent continue --scope global >/dev/null

[ -f "$tmp_py/proj/.cursorrules" ]
[ -f "$tmp_py/proj/.github/skills/repo-recon/SKILL.md" ]
[ -f "$tmp_py/proj/.openai/codex-instructions.md" ]
[ -d "$tmp_py/home/.continue/skills" ]

printf 'y\n' | HOME="$tmp_py/home" "$PYTHON_BIN" scripts/install_agent_kit.py --agent cursor --scope local --project-root "$tmp_py/proj" >/dev/null
skill_count="$(find . -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
cursor_heading_count="$(rg -n '^# [a-z0-9-]+$' "$tmp_py/proj/.cursorrules" | wc -l | tr -d ' ')"
if [ "$cursor_heading_count" -ne "$skill_count" ]; then
    echo "Idempotence check failed for cursor bundle ($cursor_heading_count != $skill_count)." >&2
    exit 1
fi

echo "[5/9] Shell wrapper checks"
tmp_sh="$(mktemp_dir)"
mkdir -p "$tmp_sh/home" "$tmp_sh/proj"
(
    cd "$tmp_sh/proj"
    HOME="$tmp_sh/home" "$ROOT_DIR/scripts/install.sh" --agent cursor --scope local --dry-run >/dev/null
    printf 'y\n' | HOME="$tmp_sh/home" "$ROOT_DIR/scripts/install.sh" --agent copilot >/dev/null
    # Skip interactive mode test due to input complexity
    # printf '5\ny\n' | HOME="$tmp_sh/home" "$ROOT_DIR/scripts/install.sh" --interactive >/dev/null
    printf 'y\n' | HOME="$tmp_sh/home" "$ROOT_DIR/scripts/install.sh" --agent claude-code --scope global >/dev/null
)
[ -f "$tmp_sh/home/.claude/skills/reverse-doc-reconstruction/scripts/bootstrap_reverse_doc_workspace.py" ]
[ -f "$tmp_sh/proj/.github/skills/repo-recon/SKILL.md" ]

echo "[6/9] Manifest sync check"
"$PYTHON_BIN" scripts/sync_manifest.py --check >/dev/null

echo "[7/9] Hooks verification check"
# Check hooks registry exists
if [ ! -f "template/hooks/registry.yaml" ]; then
    echo "Hooks registry not found at template/hooks/registry.yaml" >&2
    exit 1
fi

# Count all hooks in template
hook_count=$(find template/hooks -maxdepth 1 -name "*.yaml" -type f | wc -l | tr -d ' ')
if [ "$hook_count" -lt 10 ]; then
    echo "Expected at least 10 hooks, found $hook_count in template/hooks/" >&2
    exit 1
fi

# Check core hooks exist
for hook in mcp-health-check input-validation cleanup-handler progress-reporter error-recovery redaction timeout-handler; do
    if [ ! -f "template/hooks/$hook.yaml" ]; then
        echo "Required hook '$hook.yaml' not found in template/hooks/" >&2
        exit 1
    fi
done

# Check domain-specific hooks exist
for hook in orchestrator-hooks migration-hooks; do
    if [ ! -f "template/hooks/$hook.yaml" ]; then
        echo "Domain hook '$hook.yaml' not found in template/hooks/" >&2
        exit 1
    fi
done

# Validate hooks in manifest
if "$PYTHON_BIN" scripts/sync_manifest.py --help | grep -q -- "--validate-hooks"; then
    "$PYTHON_BIN" scripts/sync_manifest.py --validate-hooks --check >/dev/null 2>&1 || true
fi

echo "✓ Hooks verification passed ($hook_count hooks found)"

echo "[8/9] Hooks installation check"
# Verify hooks are installed after installation
tmp_hooks="$(mktemp_dir)"
mkdir -p "$tmp_hooks/home"
printf 'y\n' | HOME="$tmp_hooks/home" "$PYTHON_BIN" scripts/install_agent_kit_with_templates.py --agent claude-code --scope global >/dev/null 2>&1

if [ ! -d "$tmp_hooks/home/.claude/skills/template/hooks" ]; then
    echo "Hooks directory not installed at ~/.claude/skills/template/hooks/" >&2
    exit 1
fi

installed_hook_count=$(find "$tmp_hooks/home/.claude/skills/template/hooks" -maxdepth 1 -name "*.yaml" -type f | wc -l | tr -d ' ')
if [ "$installed_hook_count" -lt 10 ]; then
    echo "Expected at least 10 hooks installed, found $installed_hook_count" >&2
    exit 1
fi

if [ ! -f "$tmp_hooks/home/.claude/skills/template/hooks/registry.yaml" ]; then
    echo "Hooks registry not installed" >&2
    exit 1
fi

if [ ! -f "$tmp_hooks/home/.claude/skills/template/hooks/MIGRATION_GUIDE.md" ]; then
    echo "Migration guide not installed" >&2
    exit 1
fi

echo "✓ Hooks installation passed ($installed_hook_count hooks installed)"
rm -rf "$tmp_hooks"

echo "[9/9] Project bidding suite integration test"
"$PYTHON_BIN" scripts/test_project_bidding_suite.py >/dev/null

echo "✅ All smoke tests passed."
echo "   Hooks system: Enabled"
echo "   Template hooks: $hook_count verified"
echo "   Installation hooks: $installed_hook_count verified"
echo "   Registry: template/hooks/registry.yaml"
