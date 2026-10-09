#!/usr/bin/env python3
"""Verify that bundled files match the hashes recorded in sources.json and that manifests agree."""

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    errors = []

    sources = json.loads((REPO / "sources.json").read_text())
    for entry in sources["files"]:
        path = REPO / entry["path"]
        if not path.is_file():
            errors.append(f"missing bundled file: {entry['path']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != entry["bundled_sha256"]:
            errors.append(f"hash mismatch: {entry['path']}")

    plugin = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    marketplace = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
    entries = [p for p in marketplace["plugins"] if p["name"] == plugin["name"]]
    if len(entries) != 1:
        errors.append(f"marketplace must list plugin {plugin['name']} exactly once")
    elif entries[0].get("version") != plugin["version"]:
        errors.append(f"version mismatch: plugin.json {plugin['version']} vs marketplace {entries[0].get('version')}")

    for skill in sorted((REPO / "skills").iterdir()):
        if skill.is_dir() and not (skill / "SKILL.md").is_file():
            errors.append(f"skill directory without SKILL.md: {skill.name}")

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    print(f"checked {len(sources['files'])} files, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
