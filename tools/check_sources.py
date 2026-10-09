#!/usr/bin/env python3
"""Verify that bundled files match the hashes recorded in sources.json and that manifests agree."""

import hashlib
import json
import re
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

    codex = json.loads((REPO / ".codex-plugin" / "plugin.json").read_text())
    if codex["version"] != plugin["version"]:
        errors.append("Codex and Claude plugin versions differ")

    expected = {"build-nextflow-pipeline", "nf-pipeline-design", "repair-workflow",
                "debug-local-run", "debug-seqera-failed-run", "nf-test", "migrate-nextflow-code",
                "nextflow-schema", "nextflow-config", "create-container", "launch-workflow"}
    actual = {p.parent.name for p in (REPO / "skills").glob("*/SKILL.md")}
    if actual != expected:
        errors.append(f"skill inventory mismatch: missing {sorted(expected - actual)}, unexpected {sorted(actual - expected)}")
    recorded = {entry["path"] for entry in sources["files"]}
    for path in sorted((REPO / "skills").rglob("*")):
        if path.is_file() and path.relative_to(REPO).as_posix() not in recorded:
            errors.append(f"unrecorded skill resource: {path.relative_to(REPO)}")
    for path in sorted((REPO / "skills").rglob("*.md")):
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", path.read_text()):
            location = target.partition("#")[0]
            if not location or location.startswith(("/", "<")) or re.match(r"[a-zA-Z][\w+.-]*:", location):
                continue
            if not (path.parent / location).resolve().exists():
                errors.append(f"broken local link: {path.relative_to(REPO)} -> {target}")

    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    print(f"checked {len(sources['files'])} files, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
