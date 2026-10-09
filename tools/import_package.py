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
import hashlib
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
LICENSE = "Apache-2.0"

# Seqera releases the portal-derived skill files bundled in this plugin under Apache-2.0
# (the portal itself stays under BSL-1.1), so the portal license file is not distributed.
PORTAL_LICENSE = "licenses/portal-BSL-1.1.txt"
AUTHOR = {"name": "Seqera", "url": "https://seqera.io"}

# Version of the Claude plugin. It is released independently of the generic package
# because the Claude build curates the skill set below; bump it on every release.
VERSION = "0.2.1"

# Skills from the generic package that are not shipped in the Claude plugin.
EXCLUDED_SKILLS = [
    "enumerate-alternative-tools",  # duplicate of find-alternative-tools
    "generate-pipeline-docs",
    "generate-pipeline-memory",
    "genomics-workflow-acceleration",
    "nf-aggregate",
    "nf-pipeline-structure",  # folded into nf-pipeline-design
    "nf-storedir",
    "parabricks",
    "seqera-cli-agent",
]

# Product names renamed throughout the shipped skills and the plugin description.
RENAMES = [("Seqera Platform", "Nextflow Platform")]

# Exact text edits so the remaining skills don't point at excluded ones. Each edit must
# match exactly once, so upstream wording changes fail the import instead of slipping through.
EDITS = [
    ("skills/audit-conversion-readiness/SKILL.md",
     "- `enumerate-alternative-tools` — tools blocked by license, GPU",
     "- `find-alternative-tools` — tools blocked by license, GPU"),
    ("skills/audit-conversion-readiness/references/tool-availability.md",
     "`enumerate-alternative-tools` for a CPU path.",
     "`find-alternative-tools` for a CPU path."),
    ("skills/nf-pipeline-design/SKILL.md",
     "- `enumerate-alternative-tools` — tool choice at a branch",
     "- `find-alternative-tools` — tool choice at a branch"),
    ("skills/nf-pipeline-design/SKILL.md",
     """  shape", "tuple shape", "operator vs module". Pair with `nf-pipeline-structure`
  (which analyzes existing pipelines); this skill prescribes the rules for
  writing them. Use this skill before writing any new `.nf` file in an
  unfamiliar layout.""",
     """  shape", "tuple shape", "operator vs module". Also use it to analyze how an
  existing pipeline is organized — processes, modules, subworkflows, channels
  and data flow — when the user asks how a pipeline works or before changing
  it. Use this skill before writing any new `.nf` file in an unfamiliar layout."""),
    ("skills/maintain-nf-core-pipeline/SKILL.md",
     "- `nf-pipeline-structure`",
     "- `nf-pipeline-design`"),
    ("skills/nf-docker-scripts/SKILL.md",
     "- `nf-pipeline-structure` — understanding pipeline layout including shared helper commands",
     "- `nf-pipeline-design` — understanding pipeline layout including shared helper commands"),
    ("skills/nf-plugin-development/SKILL.md",
     "- `nf-pipeline-structure` — Standard pipeline organization",
     "- `nf-pipeline-design` — Standard pipeline organization"),
]
MCP_URL = "https://mcp.seqera.io/mcp"

# Listing icon shown in plugin browsers and the plugin directory.
ICON = "./assets/nextflow-uploaded-logo.png"


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


def relicense_portal_files() -> None:
    (REPO / PORTAL_LICENSE).unlink(missing_ok=True)
    path = REPO / "sources.json"
    sources = json.loads(path.read_text())
    files = []
    for entry in sources["files"]:
        if entry["path"] != PORTAL_LICENSE:
            files.append(entry)
    sources["files"] = files
    sources["relicensed"] = {
        "sources": "portal",
        "from": "BUSL-1.1",
        "to": LICENSE,
        "by": "Seqera Labs, S.L.",
        "note": "Portal-derived files bundled in this plugin are distributed under Apache-2.0; see LICENSE and NOTICE.",
    }
    write_json(path, sources)


def rename(text: str) -> str:
    for old, new in RENAMES:
        text = text.replace(old, new)
    return text


def curate_skills() -> None:
    for skill in EXCLUDED_SKILLS:
        path = REPO / "skills" / skill
        if not path.is_dir():
            sys.exit(f"excluded skill not found in package: {skill}")
        shutil.rmtree(path)

    edited = set()
    for rel, old, new in EDITS:
        path = REPO / rel
        text = path.read_text()
        if text.count(old) != 1:
            sys.exit(f"edit for {rel} matched {text.count(old)} times; update EDITS")
        path.write_text(text.replace(old, new))
        edited.add(rel)

    for path in sorted((REPO / "skills").rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".txt", ".py", ".sh", ".json", ".yml", ".yaml"):
            continue
        text = path.read_text()
        renamed = rename(text)
        if renamed != text:
            path.write_text(renamed)
            edited.add(str(path.relative_to(REPO)))

    for skill in EXCLUDED_SKILLS:
        for path in (REPO / "skills").rglob("*"):
            if path.is_file() and f"`{skill}`" in path.read_text(errors="ignore"):
                sys.exit(f"{path.relative_to(REPO)} still references excluded skill {skill}; add an edit")

    path = REPO / "sources.json"
    sources = json.loads(path.read_text())
    files = []
    for entry in sources["files"]:
        if entry["path"].split("/")[:2] in [["skills", s] for s in EXCLUDED_SKILLS]:
            continue
        if entry["path"] in edited:
            entry["bundled_sha256"] = hashlib.sha256((REPO / entry["path"]).read_bytes()).hexdigest()
            entry["override"] = True
        files.append(entry)
    sources["files"] = files
    sources["claude_curation"] = {
        "excluded_skills": EXCLUDED_SKILLS,
        "renames": [{"from": old, "to": new} for old, new in RENAMES],
        "edited_files": sorted(edited),
    }
    write_json(path, sources)


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

        relicense_portal_files()
        curate_skills()

        review = generic.get("extensions", {}).get("com.openai", {}).get("review", {}).get("test_cases")
        if review:
            write_json(REPO / "evals" / "review-cases.json", review)

    name, version, description = generic["name"], VERSION, rename(generic["description"])

    write_json(REPO / ".claude-plugin" / "plugin.json", {
        "name": name,
        "version": version,
        "description": description,
        "icon": ICON,
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
        "metadata": {"description": "Nextflow plugin for Claude Code"},
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

    if not (REPO / ICON).is_file():
        sys.exit(f"icon not found: {ICON}")

    skills = sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md"))
    print(f"imported {name} {version}: {len(skills)} skills")


if __name__ == "__main__":
    main()
