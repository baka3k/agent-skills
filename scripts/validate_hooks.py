#!/usr/bin/env python3
"""Validate hooks YAML files with support for multi-document files."""

import sys
import yaml
from pathlib import Path


def validate_hook_file(hook_path: Path) -> tuple[bool, str, int]:
    """
    Validate a hook YAML file.

    Returns:
        (is_valid, message, hook_count)
    """
    try:
        with open(hook_path) as f:
            docs = list(yaml.safe_load_all(f))

        # Filter out None documents
        docs = [d for d in docs if d is not None]

        if not docs:
            return False, "No valid YAML documents found", 0

        # Check required fields in each document
        for i, doc in enumerate(docs):
            if not isinstance(doc, dict):
                return False, f"Document {i+1} is not a dictionary", 0

            # Skip validation for registry.yaml (has different structure)
            if hook_path.name == 'registry.yaml':
                # Just check it's valid YAML
                continue

            if 'name' not in doc:
                return False, f"Document {i+1} missing 'name' field", 0

            if 'type' not in doc and 'category' not in doc:
                # Registry entries have 'category' instead of 'type'
                return False, f"Document {i+1} missing 'type' field", 0

            if 'description' not in doc:
                return False, f"Document {i+1} missing 'description' field", 0

        return True, "Valid", len(docs)

    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}", 0
    except Exception as e:
        return False, f"Error: {e}", 0


def main() -> int:
    """Validate all hooks in the template/hooks directory."""

    # Determine hooks directory
    if len(sys.argv) > 1:
        hooks_dir = Path(sys.argv[1])
    else:
        hooks_dir = Path(__file__).parent.parent / "template" / "hooks"

    if not hooks_dir.exists():
        print(f"Error: Hooks directory not found: {hooks_dir}")
        return 1

    print(f"Validating hooks in: {hooks_dir}")
    print("=" * 60)

    hook_files = sorted(hooks_dir.glob("*.yaml"))
    if not hook_files:
        print("Error: No hook files found")
        return 1

    valid_count = 0
    invalid_count = 0
    total_hooks = 0

    for hook_file in hook_files:
        is_valid, message, hook_count = validate_hook_file(hook_file)

        if is_valid:
            valid_count += 1
            total_hooks += hook_count
            status = "✓"
            if hook_count > 1:
                print(f"{status} {hook_file.name}: {hook_count} hooks")
            else:
                print(f"{status} {hook_file.name}: valid")
        else:
            invalid_count += 1
            print(f"✗ {hook_file.name}: {message}")

    print("=" * 60)
    print(f"Results: {valid_count} valid, {invalid_count} invalid")
    print(f"Total hooks defined: {total_hooks}")

    return 0 if invalid_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
