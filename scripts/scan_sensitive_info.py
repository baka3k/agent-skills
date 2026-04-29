#!/usr/bin/env python3
"""Scan SKILL.md files for sensitive information."""

import re
from pathlib import Path
from typing import List, Dict, Tuple

# Sensitive patterns to look for
SENSITIVE_PATTERNS = {
    'real_urls': re.compile(r'https?://(?!example\.com|localhost|127\.0\.0\.1)[a-zA-Z0-9.-]+\.[a-z]{2,}[/\S]*'),
    'real_emails': re.compile(r'\b[a-zA-Z0-9._%+-]+@(?!example\.com|test\.com|localhost)[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'real_aws_keys': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    'real_gcp_keys': re.compile(r'\b[0-9a-f]{32}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'),
    'real_connection_strings': re.compile(r'(postgresql|mongodb|mysql|redis)://[^<\s"\']{10,}'),
    'real_api_keys': re.compile(r'\b[A-Za-z0-9+/]{32,}={0,2}\b'),
    'real_passwords': re.compile(r'password\s*[:=]\s*["\']?[^<\s"\']{4,}["\']?', re.IGNORECASE),
    'real_ips': re.compile(r'\b(?!127\.0\.0\.1|0\.0\.0\.1|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)(?:\d{1,3}\.){3}\d{1,3}\b'),
}

# Common patterns that are NOT sensitive (false positives)
FALSE_POSITIVE_PATTERNS = {
    'commas': ',',
    'periods': r'\.\.\.',
    'placeholders': re.compile(r'\{[^}]*\}'),
    'backtick_refs': re.compile(r'`[^`]{1,50}`'),
    'common_names': re.compile(r'\b(Module|Project|Team|Admin|User|Config|Data|System|Application|Service|Client|Server|Manager|Controller|Handler|Router|Middleware|Repository|Model|View|DTO|DAO|API|HTTP|REST|GraphQL|SQL|NoSQL|Cache|Queue|Logger|Validator|Formatter|Parser|Serializer|Deserializer|Encoder|Decoder|Encryptor|Decryptor|Auth|Token|Session|Cookie|Header|Body|Request|Response|Error|Exception|Warning|Info|Debug|Trace|Log|Test|Mock|Stub|Spy|Factory|Builder|Prototype|Singleton|Observer|Strategy|Command|Adapter|Facade|Proxy|Decorator|Iterator|Composite|Flyweight|State|Template|Bridge|Visitor|Memento|Mediator|Chain)\b', re.IGNORECASE),
}

def scan_file(file_path: Path) -> List[Dict]:
    """Scan a single file for sensitive information."""
    findings = []

    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip lines that are obviously examples
            if any(marker in line.lower() for marker in ['example', 'placeholder', 'your_', 'xxx', 'todo', 'tbd']):
                continue

            for pattern_name, pattern in SENSITIVE_PATTERNS.items():
                matches = pattern.finditer(line)
                for match in matches:
                    matched_text = match.group(0)

                    # Check if it's in backticks (code reference)
                    if f'`{matched_text}`' in line or f"`{matched_text}'" in line:
                        continue

                    # Check for false positives
                    is_false_positive = False
                    for fp_name, fp_pattern in FALSE_POSITIVE_PATTERNS.items():
                        if isinstance(fp_pattern, str):
                            if fp_pattern in matched_text:
                                is_false_positive = True
                                break
                        elif hasattr(fp_pattern, 'search'):
                            if fp_pattern.search(matched_text):
                                is_false_positive = True
                                break

                    if is_false_positive:
                        continue

                    # Check if it's a common tech term
                    common_tech_terms = [
                        'ApplicationContext', 'ServletContext', 'DbContext',
                        'HttpClient', 'HttpResponse', 'HttpRequest',
                        'SqlConnection', 'MongoClient', 'RedisClient',
                        'AWS_ACCESS_KEY', 'AWS_SECRET', 'API_KEY', 'SECRET_KEY',
                        'DB_CONNECTION', 'DB_HOST', 'DB_PORT', 'DB_NAME',
                        'CONFIG_FILE', 'CONFIG_PATH', 'DATA_DIR', 'LOG_DIR',
                        'USER_HOME', 'APP_HOME', 'BASE_DIR', 'ROOT_DIR',
                    ]
                    if any(term.lower() in matched_text.lower() for term in common_tech_terms):
                        continue

                    findings.append({
                        'line': line_num,
                        'pattern': pattern_name,
                        'match': matched_text,
                        'context': line.strip()[:100],
                    })

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return findings

def main():
    """Main scan function."""
    base_dir = Path('/Users/hieplq1.rpm/AI/agent-skill')
    skill_dirs = [
        'bug-impact-analyzer',
        'module-summary-report',
        'tech-build-audit',
        'repo-recon',
        'deep-codebase-discovery',
        'reverse-doc-reconstruction',
        'legacy-cpp-porting-guardrails',
    ]

    all_findings = {}

    for skill_dir in skill_dirs:
        skill_path = base_dir / skill_dir / 'SKILL.md'
        if skill_path.exists():
            findings = scan_file(skill_path)
            if findings:
                all_findings[skill_dir] = findings

    # Report findings
    if all_findings:
        print("🚨 POTENTIAL SENSITIVE INFORMATION FOUND:\n")
        for skill_dir, findings in all_findings.items():
            print(f"\n{'='*60}")
            print(f"SKILL: {skill_dir}")
            print(f"{'='*60}")
            for finding in findings[:10]:  # Limit to 10 per skill
                print(f"\n  Line {finding['line']} ({finding['pattern']}):")
                print(f"    Match: {finding['match']}")
                print(f"    Context: {finding['context']}")
            if len(findings) > 10:
                print(f"\n  ... and {len(findings) - 10} more")
    else:
        print("✅ No sensitive information found in SKILL.md files")
        print("\nScanned patterns:")
        for pattern_name in SENSITIVE_PATTERNS.keys():
            print(f"  - {pattern_name}")

    print(f"\n{'='*60}")
    print(f"Total skills scanned: {len(skill_dirs)}")
    print(f"Skills with findings: {len(all_findings)}")

if __name__ == '__main__':
    main()
