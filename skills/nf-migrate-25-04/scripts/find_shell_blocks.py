#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Find deprecated process `shell` blocks in Nextflow files.

Nextflow 25.04 deprecates the `shell` section in processes. This script
scans .nf files for `shell` blocks and reports locations + context.

Note: Uses regex scanning (not AST) because no tree-sitter grammar exists
for Nextflow yet. The Java parser mishandles triple-quoted strings.

Usage:
    ./find_shell_blocks.py [directory]    # default: current dir
    ./find_shell_blocks.py path/to/pipeline

Exit codes:
    0 — no deprecated shell blocks found
    1 — deprecated shell blocks found
    2 — usage error
"""

import re
import sys
from pathlib import Path

# Matches `shell` keyword followed by a string opener, inside a process block.
# Handles: shell '''...''', shell """...""", shell '...', shell "..."
# Uses a non-consuming group to anchor at line start without eating \n.
SHELL_BLOCK_RE = re.compile(
    r"(?m)^[ \t]*shell\s+(?:'''|\"\"\"|\"|')",
)


def find_shell_blocks(directory: str = ".") -> list[dict]:
    """Find `shell` blocks in .nf files under directory."""
    results = []
    root = Path(directory)

    for nf_file in sorted(root.rglob("*.nf")):
        source = nf_file.read_text()
        for match in SHELL_BLOCK_RE.finditer(source):
            line_num = source[: match.start()].count("\n") + 1
            # Grab a few lines of context starting from the match line
            lines = source.splitlines()
            start_idx = line_num - 1
            end_idx = min(start_idx + 4, len(lines))
            preview = "\n".join(lines[start_idx : end_idx])

            results.append({
                "file": str(nf_file),
                "line": line_num,
                "preview": preview,
            })

    return results


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "."

    if not Path(directory).is_dir():
        print(f"Error: '{directory}' is not a directory", file=sys.stderr)
        sys.exit(2)

    results = find_shell_blocks(directory)

    if not results:
        print("✅ No deprecated `shell` blocks found.")
        sys.exit(0)

    print(f"⚠️  Found {len(results)} deprecated `shell` block(s):\n")
    for r in results:
        print(f"  {r['file']}:{r['line']}")
        for line in r["preview"].splitlines():
            print(f"    {line}")
        print()

    print("Migration notes:")
    print("  - Replace `shell` with `script`")
    print("  - Convert !{var} → ${var}")
    print("  - Escape literal bash $ as \\$ (was safe in shell blocks)")
    print("  - Audit every $ in the body — shell blocks ignored $, script blocks don't")
    sys.exit(1)


if __name__ == "__main__":
    main()
