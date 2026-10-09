#!/usr/bin/env python3
"""Verify bundled hashes, plugin inventories, versions and installed-root links."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def check_plugin_packages(root: Path) -> list[str]:
    errors = []
    sources = json.loads((root / "sources.json").read_text())
    recorded = set()
    for entry in sources["files"]:
        relative = entry["path"]
        if relative in recorded:
            errors.append(f"duplicate bundled path: {relative}")
        recorded.add(relative)
        path = root / relative
        if not path.is_file():
            errors.append(f"missing bundled file: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != entry["bundled_sha256"]:
            errors.append(f"hash mismatch: {relative}")

    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    listed = set()
    for entry in marketplace["plugins"]:
        name = entry["name"]
        if name in listed:
            errors.append(f"marketplace must list plugin {name} exactly once")
        listed.add(name)
        source = entry["source"]
        base = (root / source).resolve()
        if not base.is_relative_to(root.resolve()):
            errors.append(f"plugin source escapes marketplace: {source}")
            continue
        manifest = base / ".claude-plugin/plugin.json"
        if not manifest.is_file():
            errors.append(f"missing plugin manifest: {source}")
            continue
        plugin = json.loads(manifest.read_text())
        if plugin["name"] != name or entry.get("version") != plugin.get("version"):
            errors.append(f"name/version mismatch for {name}")
        if base != root.resolve() and ((base / ".mcp.json").exists() or plugin.get("mcpServers")):
            errors.append(f"optional plugin registers a duplicate MCP connection: {name}")
        if base != root.resolve():
            local_manifest = base / "sources.json"
            if not local_manifest.is_file():
                errors.append(f"missing installed-pack provenance: {name}")
            else:
                prefix = str(base.relative_to(root)) + "/"
                expected_files = [{**e, "path": e["path"][len(prefix):]} for e in sources["files"] if e["path"].startswith(prefix)]
                if json.loads(local_manifest.read_text())["files"] != expected_files:
                    errors.append(f"installed-pack provenance mismatch: {name}")
        actual = set()
        for skill in sorted((base / "skills").iterdir()):
            if not skill.is_dir():
                continue
            if not (skill / "SKILL.md").is_file():
                errors.append(f"skill directory without SKILL.md: {name}/{skill.name}")
            actual.add(skill.name)
        expected = sources["claude_curation"].get("skill_packs", {}).get(name)
        if expected is not None and actual != set(expected):
            errors.append(f"skill inventory mismatch for {name}")
        for path in (base / "skills").rglob("*"):
            if not path.is_file():
                continue
            if str(path.relative_to(root)) not in recorded:
                errors.append(f"unrecorded bundled file: {path.relative_to(root)}")
            if path.suffix != ".md":
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", path.read_text()):
                if target.startswith(("#", "/", "<")) or re.match(r"[a-zA-Z][\w+.-]*:", target):
                    continue
                destination = (path.parent / target.partition("#")[0]).resolve()
                if not destination.is_file():
                    errors.append(f"missing local link: {path.relative_to(root)} -> {target}")
                elif not destination.is_relative_to(base) or (base == root.resolve() and destination.is_relative_to(root / "packs")):
                    errors.append(f"link escapes installed plugin: {path.relative_to(root)} -> {target}")
    expected_plugins = sources["claude_curation"].get("skill_packs", {})
    if expected_plugins and listed != set(expected_plugins):
        errors.append("marketplace plugin inventory differs from generated partition")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = check_plugin_packages(root)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    sources = json.loads((root / "sources.json").read_text())
    print(f"checked {len(sources['files'])} files, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
