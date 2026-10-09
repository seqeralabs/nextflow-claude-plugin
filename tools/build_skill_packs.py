#!/usr/bin/env python3
"""Generate an eleven-skill core and opt-in plugins from the curated catalog.

Run after the original consolidation and manifest generation. Re-import upstream
content to change a completed partition; replay validates it without moving files.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PLAN = Path(__file__).with_name("skill_packs.json")
LINK = re.compile(r"(\[[^\]]*\]\()([^\s)]+)\)")


def write_pack_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def validate_pack_files(root: Path, sources: dict) -> None:
    for entry in sources["files"]:
        path = root / entry["path"]
        if not path.is_file():
            raise ValueError(f"missing bundled file: {entry['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["bundled_sha256"]:
            raise ValueError(f"bundled file changed: {entry['path']}; re-import before rebuilding packs")


def build_skill_packs(root: Path, plan: dict, assets: Path, version: str | None = None) -> None:
    assignments = [(name, "nextflow") for name in plan["core"]]
    assignments += [(name, pack["name"]) for pack in plan["packs"] for name in pack["skills"]]
    owners = dict(assignments)
    if len(owners) != len(assignments):
        raise ValueError("skill assigned more than once in pack plan")
    manifest = json.loads((root / ".claude-plugin/plugin.json").read_text())
    if version:
        manifest["version"] = version
    signature = hashlib.sha256(json.dumps({"plan": plan, "version": manifest["version"]}, sort_keys=True).encode()).hexdigest()
    sources = json.loads((root / "sources.json").read_text())
    curation = sources["claude_curation"]
    if curation.get("skill_pack_plan_sha256"):
        if curation["skill_pack_plan_sha256"] != signature:
            raise ValueError("skill pack plan changed; re-import before rebuilding packs")
        validate_pack_files(root, sources)
        validate_pack_inventory(root, plan)
        subprocess.run([sys.executable, "-I", str(Path(__file__).with_name("check_sources.py")), "--root", str(root)], check=True)
        return
    if (root / "packs").exists():
        raise ValueError("partial skill pack output; re-import before rebuilding packs")
    fold_plan = None
    if plan.get("consolidations"):
        fold_plan = assets / plan["consolidations"]
        folds = json.loads(fold_plan.read_text())
        removed = {fold["from"] for group in folds["groups"] for fold in group["folds"]}
    else:
        removed = set()
    live = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    if live not in (set(owners), set(owners) | removed):
        raise ValueError(f"skill pack inventory mismatch: unexpected={sorted(live - set(owners) - removed)}, missing={sorted(set(owners) - live)}")
    if fold_plan:
        subprocess.run([sys.executable, "-I", str(Path(__file__).with_name("consolidate_skills.py")), "--root", str(root), "--plan", str(fold_plan)], check=True)
        sources = json.loads((root / "sources.json").read_text())
        curation = sources["claude_curation"]
    old_paths = [p for p in (root / "skills").rglob("*") if p.is_file()]
    recorded = {entry["path"] for entry in sources["files"]}
    for path in old_paths:
        relative = str(path.relative_to(root))
        if relative not in recorded:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            sources["files"].append({"path": relative, "source": "imported-package/" + relative,
                                     "source_sha256": digest, "bundled_sha256": digest,
                                     "note": "No upstream provenance entry was provided; hash records imported bytes."})
    mapped = {}
    for path in old_paths:
        relative = path.relative_to(root / "skills")
        owner = owners[relative.parts[0]]
        base = root if owner == "nextflow" else root / "packs" / owner
        mapped[path.resolve()] = base / "skills" / relative
    for pack in plan["packs"]:
        base = root / "packs" / pack["name"]
        (base / "skills").mkdir(parents=True)
        for name in pack["skills"]:
            shutil.move(str(root / "skills" / name), base / "skills" / name)

    # Resolve in the original tree, then rewrite using each installed plugin root.
    # Filesystem links across cache roots become explicit namespaced skill handoffs.
    for old, new in mapped.items():
        if new.suffix != ".md":
            continue
        skill = old.relative_to(root / "skills").parts[0]
        owner = owners[skill]
        base = root if owner == "nextflow" else root / "packs" / owner

        def relocate_link(match):
            target, separator, anchor = match.group(2).partition("#")
            if not target or target.startswith(("/", "<")) or re.match(r"[a-zA-Z][\w+.-]*:", target):
                return match.group()
            original = (old.parent / target).resolve()
            destination = mapped.get(original, original)
            if destination.is_relative_to(base) and not (owner == "nextflow" and destination.is_relative_to(root / "packs")):
                return f"{match.group(1)}{Path(os.path.relpath(destination, new.parent)).as_posix()}{separator}{anchor})"
            if original == (root / "skills/launch-workflow/references/seqera-mcp/README.md").resolve():
                connection = base / "references/mcp-connection.md"
                return f"{match.group(1)}{Path(os.path.relpath(connection, new.parent)).as_posix()})"
            if original.is_relative_to(root / "skills"):
                name = original.relative_to(root / "skills").parts[0]
                label = match.group(1)[1:-2]
                return f"{label}: consult `{owners[name]}:{name}` and its matching reference (requires that plugin to be enabled)"
            raise ValueError(f"resource escapes plugin root: {new.relative_to(root)} -> {target}")

        text = LINK.sub(relocate_link, new.read_text())
        for name, pack_owner in owners.items():
            if pack_owner == "nextflow":
                continue
            pattern = rf"`{re.escape(name)}`|(?<![\w:/-]){re.escape(name)}(?![\w/-]|\.md\b)"
            # Descriptions retain ordinary words; qualify skill handoffs in bodies.
            front = re.match(r"\A---\n.*?\n---\n", text, re.S) if new.name == "SKILL.md" else None
            offset = front.end() if front else 0
            text = text[:offset] + re.sub(pattern, f"`{pack_owner}:{name}`", text[offset:])
        if new.name == "SKILL.md" and owner == "nextflow" and plan.get("core_guidance"):
            optional = root / "skills/build-nextflow-pipeline/references/optional-packs.md"
            relative = Path(os.path.relpath(optional, new.parent)).as_posix()
            text += f"\n\n## Optional specialist work\n\nFor infrastructure setup, nf-core maintenance/analysis, plugin development or broad provenance work, read [optional pack handoffs]({relative}). Check available namespaced skills first; if the pack is absent, explain how to explicitly install/enable it and stop that specialist task. Ordinary debugging and launch/resume remain in core.\n"
            if skill in {"build-nextflow-pipeline", "migrate-nextflow-code", "nf-pipeline-design", "repair-workflow"}:
                safety = root / "skills/build-nextflow-pipeline/references/nf-core-safety.md"
                relative = Path(os.path.relpath(safety, new.parent)).as_posix()
                text += f"\nWhen editing an nf-core project, read [nf-core safety]({relative}); basic safe edits do not require the optional maintenance pack.\n"
            if skill == "debug-local-run":
                text += "\nFor selecting a run or inspecting resume/cache identity, read [run identification](references/run-identification.md); the provenance pack is unnecessary for ordinary diagnosis.\n"
        if new.name == "SKILL.md" and owner != "nextflow":
            front = re.match(r"\A---\n.*?\n---\n", text, re.S)
            note = "\n## Core prerequisite\n\nUse this optional pack alongside the enabled `nextflow` core plugin. If a needed core skill is unavailable, ask the user to explicitly install/enable core. Local tasks need no Platform authentication. For Platform operations, use core\'s shared Seqera connection and request authentication if necessary; do not install plugins or start another MCP connection yourself.\n"
            text = text[:front.end()] + note + text[front.end():]
        new.write_text(text)

    entries = []
    for entry in sources["files"]:
        old = (root / entry["path"]).resolve()
        if old in mapped:
            entry["path"] = str(mapped[old].relative_to(root))
        entries.append(entry)
    for resource in plan.get("resources", []):
        source = assets / resource["source"]
        destination = root / resource["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        entries.append({"path": resource["path"], "source": "tools/" + resource["source"], "source_sha256": digest, "bundled_sha256": digest, "override": False})
    write_pack_json(root / ".claude-plugin/plugin.json", manifest)
    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    marketplace["plugins"] = [p for p in marketplace["plugins"] if p["name"] == manifest["name"]]
    marketplace["plugins"][0]["version"] = manifest["version"]
    for pack in plan["packs"]:
        base = root / "packs" / pack["name"]
        for filename in ["LICENSE", "NOTICE"]:
            if (root / filename).is_file():
                destination = base / filename
                shutil.copy2(root / filename, destination)
                destination.write_text(destination.read_text().rstrip("\n") + "\n")
        for entry in list(entries):
            if entry["path"].startswith("licenses/"):
                destination = base / entry["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / entry["path"], destination)
                destination.write_text(destination.read_text().rstrip("\n") + "\n")
                entries.append({**entry, "path": str(destination.relative_to(root))})
        pack_manifest = {key: value for key, value in manifest.items() if key not in {"name", "description", "icon", "mcpServers", "skills", "dependencies"}}
        pack_manifest.update(name=pack["name"], description=pack["description"])
        write_pack_json(base / ".claude-plugin/plugin.json", pack_manifest)
        marketplace["plugins"].append({"name": pack["name"], "source": f"./packs/{pack['name']}", "description": pack["description"], "version": manifest["version"]})
    write_pack_json(root / ".claude-plugin/marketplace.json", marketplace)
    edited = set()
    for entry in entries:
        digest = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
        if digest != entry["bundled_sha256"]:
            entry["override"] = True
        entry["bundled_sha256"] = digest
        if entry.get("override"):
            edited.add(entry["path"])
    sources["files"] = entries
    for pack in plan["packs"]:
        prefix = f"packs/{pack['name']}/"
        local_entries = [{**entry, "path": entry["path"][len(prefix):]}
                         for entry in entries if entry["path"].startswith(prefix)]
        local_sources = {key: value for key, value in sources.items() if key not in {"files", "claude_curation"}}
        local_sources["files"] = local_entries
        local_sources["distribution"] = {"plugin": pack["name"], "requires_core": "nextflow"}
        write_pack_json(root / prefix / "sources.json", local_sources)
    curation["edited_files"] = sorted(edited)
    curation["skill_pack_plan_sha256"] = signature
    curation["skill_packs"] = {"nextflow": plan["core"], **{p["name"]: p["skills"] for p in plan["packs"]}}
    write_pack_json(root / "sources.json", sources)
    validate_pack_inventory(root, plan)
    validate_pack_files(root, sources)
    subprocess.run([sys.executable, "-I", str(Path(__file__).with_name("check_sources.py")), "--root", str(root)], check=True)


def validate_pack_inventory(root: Path, plan: dict) -> None:
    for name, expected in [("nextflow", plan["core"])] + [(p["name"], p["skills"]) for p in plan["packs"]]:
        base = root if name == "nextflow" else root / "packs" / name
        actual = {p.parent.name for p in (base / "skills").glob("*/SKILL.md")}
        if actual != set(expected):
            raise ValueError(f"skill pack inventory mismatch for {name}: {sorted(actual)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--version", help="release version for all generated manifests; defaults to core manifest")
    args = parser.parse_args()
    build_skill_packs(args.root.resolve(), json.loads(args.plan.read_text()), args.plan.parent, args.version)


if __name__ == "__main__":
    main()
