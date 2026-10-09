#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scan Nextflow project for all 25.04 deprecation/migration issues.

Checks:
  1. Deprecated `shell` blocks in processes
  2. `nextflow.preview.topic` flags (now unnecessary)
  3. Workflow output v2 `>>` syntax (replaced by assignment in v3)
  4. `-with-weblog` in scripts/configs (deprecated CLI flag)

Usage:
    ./find_deprecated_patterns.py [directory]

Exit codes:
    0 — clean
    1 — issues found
    2 — usage error
"""

import re
import sys
from pathlib import Path

CHECKS = [
    {
        "name": "deprecated `shell` block",
        "globs": ["*.nf"],
        "pattern": re.compile(r"(?m)^[ \t]*shell\s+(?:'''|\"\"\"|\"|')"),
        "fix": "Replace with `script`, convert !{var}→${var}, escape bash $ as \\$",
    },
    {
        "name": "`nextflow.preview.topic` flag (now unnecessary)",
        "globs": ["*.config", "*.nf"],
        "pattern": re.compile(r"nextflow\s*\.\s*preview\s*\.\s*topic"),
        "fix": "Remove — topic channels are out of preview in 25.04",
    },
    {
        "name": "workflow output v2 `>>` syntax",
        "globs": ["*.nf"],
        "pattern": re.compile(r"(?m)^[ \t]*\S+\s*>>\s*['\"]"),
        "fix": "Replace `FOO.out >> 'name'` with `name = FOO.out` in publish section",
    },
    {
        "name": "`-with-weblog` usage",
        "globs": ["*.sh", "*.config", "*.nf", "Makefile", "Justfile", "*.yml", "*.yaml"],
        "pattern": re.compile(r"-with-weblog\b"),
        "fix": "Switch to the nf-weblog plugin: https://github.com/nextflow-io/nf-weblog",
    },
]


def scan(directory: str = ".") -> list[dict]:
    root = Path(directory)
    findings = []

    for check in CHECKS:
        for glob in check["globs"]:
            for path in sorted(root.rglob(glob)):
                # Skip hidden dirs and work dirs
                parts = path.relative_to(root).parts
                if any(p.startswith(".") or p == "work" for p in parts):
                    continue

                try:
                    source = path.read_text()
                except (UnicodeDecodeError, PermissionError):
                    continue

                for match in check["pattern"].finditer(source):
                    line_num = source[: match.start()].count("\n") + 1
                    line_text = source.splitlines()[line_num - 1].strip()
                    findings.append({
                        "check": check["name"],
                        "fix": check["fix"],
                        "file": str(path),
                        "line": line_num,
                        "text": line_text[:120],
                    })

    return findings


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "."

    if not Path(directory).is_dir():
        print(f"Error: '{directory}' is not a directory", file=sys.stderr)
        sys.exit(2)

    findings = scan(directory)

    if not findings:
        print("✅ No Nextflow 25.04 migration issues found.")
        sys.exit(0)

    # Group by check
    by_check: dict[str, list] = {}
    for f in findings:
        by_check.setdefault(f["check"], []).append(f)

    total = len(findings)
    print(f"⚠️  Found {total} migration issue(s) across {len(by_check)} category(ies):\n")

    for check_name, items in by_check.items():
        print(f"── {check_name} ({len(items)} found) ──")
        print(f"   Fix: {items[0]['fix']}")
        for item in items:
            print(f"   {item['file']}:{item['line']}  {item['text']}")
        print()

    sys.exit(1)


if __name__ == "__main__":
    main()
