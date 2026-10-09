#!/usr/bin/env python3
"""Import a built Agent Plugins package (directory or .zip) into this repo as a Claude Code plugin.

The generic package is produced elsewhere from private sources. This script copies its
host-neutral content (skills, scripts, assets, licenses, provenance) into the repo root and
regenerates the Claude-specific manifests, so this repo never needs access to those sources.

Usage:
    python3 -I tools/import_package.py /path/to/nextflow.zip
    python3 -I tools/import_package.py /path/to/nextflow/
"""

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Content copied verbatim from the generic package. Everything else in the package
# (plugin.json, mcp.json, .codex-plugin/, README.md) is host-specific and regenerated here.
CONTENT = ["skills", "scripts", "assets", "licenses", "sources.json"]

REPOSITORY = "https://github.com/seqeralabs/nextflow-claude-plugin"
LICENSE = "Apache-2.0 AND BUSL-1.1"
AUTHOR = {"name": "Seqera", "url": "https://seqera.io"}
MCP_URL = "https://mcp.seqera.io/mcp"


def locate_package(source: Path, workdir: Path) -> Path:
    if source.is_file():
        with zipfile.ZipFile(source) as archive:
            for member in archive.namelist():
                target = (workdir / member).resolve()
                if not target.is_relative_to(workdir.resolve()):
                    sys.exit(f"refusing unsafe archive member: {member}")
            archive.extractall(workdir)
        source = workdir
    if (source / "plugin.json").is_file():
        return source
    candidates = [p.parent for p in source.glob("*/plugin.json")]
    if len(candidates) != 1:
        sys.exit(f"expected exactly one package with plugin.json under {source}, found {len(candidates)}")
    return candidates[0]


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="generic package directory or .zip")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        package = locate_package(args.source.resolve(), Path(tmp))
        generic = json.loads((package / "plugin.json").read_text())

        for name in CONTENT:
            src, dst = package / name, REPO / name
            if not src.exists():
                sys.exit(f"package is missing {name}")
            if dst.is_dir():
                shutil.rmtree(dst)
            elif dst.exists():
                dst.unlink()
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        review = generic.get("extensions", {}).get("com.openai", {}).get("review", {}).get("test_cases")
        if review:
            write_json(REPO / "evals" / "review-cases.json", review)

    name, version, description = generic["name"], generic["version"], generic["description"]

    write_json(REPO / ".claude-plugin" / "plugin.json", {
        "name": name,
        "version": version,
        "description": description,
        "author": AUTHOR,
        "homepage": REPOSITORY,
        "repository": REPOSITORY,
        "license": LICENSE,
        "keywords": generic.get("keywords", []),
    })

    write_json(REPO / ".claude-plugin" / "marketplace.json", {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "nextflow-claude-plugin",
        "owner": AUTHOR,
        "metadata": {"description": "Nextflow and Seqera Platform plugin for Claude Code"},
        "plugins": [{
            "name": name,
            "source": "./",
            "description": description,
            "version": version,
            "author": AUTHOR,
            "homepage": REPOSITORY,
            "license": LICENSE,
            "category": "development",
            "keywords": generic.get("keywords", []),
        }],
    })

    write_json(REPO / ".mcp.json", {"mcpServers": {"seqera": {"type": "http", "url": MCP_URL}}})

    skills = sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md"))
    print(f"imported {name} {version}: {len(skills)} skills")


if __name__ == "__main__":
    main()
