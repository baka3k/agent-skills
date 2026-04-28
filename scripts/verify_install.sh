#!/bin/bash
# Verification script for Agent Skills Kit installation

set -e

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$KIT_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

check_claude_code() {
    print_header "Checking Claude Code Installation"

    local skills_dir="$HOME/.claude/skills"
    if [ ! -d "$skills_dir" ]; then
        print_error "Skills directory not found: $skills_dir"
        return 1
    fi

    print_success "Skills directory exists: $skills_dir"

    local count=0
    for skill_dir in "$skills_dir"/*/; do
        if [ -d "$skill_dir" ]; then
            local skill_name=$(basename "$skill_dir")
            if [ -f "$skill_dir/SKILL.md" ]; then
                print_success "Skill: $skill_name"
                ((count++))
            fi
        fi
    done

    echo ""
    print_info "Total skills installed: $count"
    echo ""

    if [ $count -eq 0 ]; then
        print_error "No skills found"
        return 1
    fi

    return 0
}

check_cursor_global() {
    print_header "Checking Cursor Global Installation"

    local cursor_file="$HOME/.cursorrules"
    if [ ! -f "$cursor_file" ]; then
        print_error "Cursor file not found: $cursor_file"
        return 1
    fi

    print_success "Cursor file exists: $cursor_file"

    # Check for agent skills kit marker
    if grep -q "Agent Skills Kit" "$cursor_file"; then
        print_success "Agent Skills Kit detected in .cursorrules"

        # Count skills
        local count=$(grep -c "^#.*Skill" "$cursor_file" || true)
        print_info "Approximately $count skills found"
    else
        print_info "No Agent Skills Kit content found"
    fi

    echo ""
    print_info "File size: $(wc -l < "$cursor_file") lines"
    echo ""

    return 0
}

check_cursor_local() {
    print_header "Checking Cursor Local Installation"

    local cursor_file=".cursorrules"
    if [ ! -f "$cursor_file" ]; then
        print_error "Cursor file not found: $(pwd)/.cursorrules"
        print_info "Are you in the correct project directory?"
        return 1
    fi

    print_success "Cursor file exists: $(pwd)/.cursorrules"

    if grep -q "Agent Skills Kit" "$cursor_file"; then
        print_success "Agent Skills Kit detected in .cursorrules"
        local count=$(grep -c "^#.*Skill" "$cursor_file" || true)
        print_info "Approximately $count skills found"
    fi

    echo ""
    return 0
}

check_continue() {
    print_header "Checking Continue.dev Installation"

    local skills_dir="$HOME/.continue/skills"
    if [ ! -d "$skills_dir" ]; then
        print_error "Skills directory not found: $skills_dir"
        return 1
    fi

    print_success "Skills directory exists: $skills_dir"

    local count=0
    for skill_file in "$skills_dir"/*.json; do
        if [ -f "$skill_file" ]; then
            local skill_name=$(basename "$skill_file" .json)
            print_success "Skill: $skill_name"
            ((count++))
        fi
    done

    echo ""
    print_info "Total skills installed: $count"
    echo ""

    if [ $count -eq 0 ]; then
        print_error "No skills found"
        return 1
    fi

    return 0
}

check_copilot() {
    print_header "Checking GitHub Copilot Installation"

    local copilot_dir=".github/skills"
    if [ ! -d "$copilot_dir" ]; then
        print_error "Copilot skills directory not found: $(pwd)/$copilot_dir"
        print_info "Are you in the correct project directory?"
        return 1
    fi

    print_success "Copilot skills directory exists: $(pwd)/$copilot_dir"

    local count=0
    for skill_dir in "$copilot_dir"/*/; do
        if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
            local skill_name=$(basename "$skill_dir")
            print_success "Skill: $skill_name"
            ((count++))
        fi
    done

    echo ""
    print_info "Total skills installed: $count"
    echo ""

    if [ $count -eq 0 ]; then
        print_error "No skills found for Copilot"
        return 1
    fi

    return 0
}

check_codex() {
    print_header "Checking OpenAI CodeX Installation"

    local codex_file=".openai/codex-instructions.md"
    if [ ! -f "$codex_file" ]; then
        print_error "CodeX file not found: $(pwd)/$codex_file"
        print_info "Are you in the correct project directory?"
        return 1
    fi

    print_success "CodeX file exists: $(pwd)/$codex_file"

    if grep -q "Agent Skills Kit" "$codex_file"; then
        print_success "Agent Skills Kit detected in codex-instructions.md"
        local count=$(grep -c "^# " "$codex_file" || true)
        print_info "Approximately $count sections found"
    fi

    echo ""
    print_info "File size: $(wc -l < "$codex_file") lines"
    echo ""

    return 0
}

main() {
    print_header "Agent Skills Kit - Installation Verification"
    echo ""

    # Check if we're in the right directory
    if [ ! -f "$KIT_ROOT/scripts/install.sh" ]; then
        print_error "Installer script not found. Are you in the agent-skill directory?"
        exit 1
    fi

    print_success "Agent Skills Kit directory detected"
    echo ""

    # Check all platforms
    local errors=0

    check_claude_code || ((errors++))
    check_cursor_global || ((errors++))
    check_cursor_local || ((errors++))
    check_continue || ((errors++))
    check_copilot || ((errors++))
    check_codex || ((errors++))

    # Summary
    print_header "Verification Summary"

    if [ $errors -eq 0 ]; then
        print_success "All checks passed!"
        echo ""
        print_info "Your Agent Skills Kit installation looks good."
        echo ""
        print_info "Next steps:"
        echo "  - Restart your AI editor/CLI"
        echo "  - Try using a skill"
        echo "    • Claude Code: /skill deep-codebase-discovery"
        echo "    • Cursor: Just ask 'Analyze my codebase'"
        echo "    • Continue: Ctrl+Shift+A → Select skill"
        echo "    • Copilot: use skills from .github/skills"
        echo "    • CodeX: use .openai/codex-instructions.md prompts"
    else
        print_error "$errors check(s) failed"
        echo ""
        print_info "Some installations may be missing or incomplete."
        print_info "Run the installer again:"
        echo "  ./scripts/install.sh --interactive"
    fi

    echo ""
}

main "$@"
