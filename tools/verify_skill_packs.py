#!/usr/bin/env python3
"""Verify actual Claude discovery in fresh configs, without credentials or API calls."""

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXPECTED = {
    "nextflow": {"build-nextflow-pipeline", "nf-pipeline-design", "repair-workflow", "debug-local-run", "debug-seqera-failed-run", "nf-test", "migrate-nextflow-code", "nextflow-schema", "nextflow-config", "create-container", "launch-workflow"},
    "nextflow-platform": {"ce-credentials-setup", "seqera-data-links", "seqerakit"},
    "nextflow-nf-core": {"nextflow-development", "maintain-nf-core-pipeline"},
    "nextflow-plugins": {"nf-plugin-development"},
    "nextflow-provenance": {"nextflow-history", "nf-data-lineage"},
}


def verify_claude_installations(root: Path) -> dict:
    scenarios = [["nextflow"]] + [["nextflow", name] for name in EXPECTED if name != "nextflow"]
    scenarios += [list(EXPECTED), ["nextflow-plugins"]]
    report = {"claude_version": subprocess.check_output(["claude", "--version"], text=True).strip(), "scenarios": []}
    for names in scenarios:
        with tempfile.TemporaryDirectory(prefix="nextflow-pack-install-") as config:
            env = {**os.environ, "CLAUDE_CONFIG_DIR": config}

            def command(*args):
                result = subprocess.run(["claude", "plugin", *args], cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
                if result.returncode:
                    raise ValueError(f"Claude plugin command failed ({' '.join(args)}):\n{result.stdout}")
                return result.stdout

            command("marketplace", "add", str(root))
            for name in names:
                command("install", f"{name}@nextflow-claude-plugin")
            installed = command("list")
            total_skills = 0
            total_servers = 0
            inventories = {}
            for name in names:
                details = command("details", f"{name}@nextflow-claude-plugin")
                match = re.search(r"Skills \((\d+)\)\s+([^\n]+)", details)
                if not match:
                    raise ValueError(f"Claude did not report skills for {name}: {details}")
                actual = set(match.group(2).strip().split(", "))
                if actual != EXPECTED[name] or int(match.group(1)) != len(actual):
                    raise ValueError(f"Claude skill discovery mismatch for {name}: {sorted(actual)}")
                servers = re.search(r"MCP servers \((\d+)\)", details)
                if not servers:
                    raise ValueError(f"Claude did not report MCP inventory for {name}")
                count = int(servers.group(1))
                if count != (1 if name == "nextflow" else 0):
                    raise ValueError(f"Unexpected MCP registrations for {name}: {count}")
                total_skills += len(actual)
                total_servers += count
                inventories[name] = sorted(actual)
            for name in EXPECTED:
                if name not in names and f"{name}@nextflow-claude-plugin" in installed:
                    raise ValueError(f"Plugin silently installed: {name}")
            report["scenarios"].append({"plugins": names, "skills": total_skills, "mcp_servers": total_servers, "inventories": inventories, "status": "pass"})
            print(f"PASS {' + '.join(names)}: {total_skills} skills, {total_servers} MCP servers")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = verify_claude_installations(args.root.resolve())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
