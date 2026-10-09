"""Test generated plugin boundaries through the public pack-builder CLI."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI = Path(__file__).with_name("build_skill_packs.py")


class SkillPackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        files = {
            "skills/owner/SKILL.md": "---\nname: owner\ndescription: Build workflows\n---\n# Build\nUse `history`. Read [history](../history/SKILL.md).\n",
            "skills/history/SKILL.md": "---\nname: history\ndescription: Explain history\n---\n# History\nRead [owner](../owner/SKILL.md) and [details](references/details.md).\n",
            "skills/history/references/details.md": "Preserve cache semantics.\n",
            "skills/history/scripts/check.sh": "#!/bin/sh\nprintf 'history checked\\n'\n",
        }
        entries = []
        for relative, content in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            digest = hashlib.sha256(content.encode()).hexdigest()
            entries.append({"path": relative, "source": "upstream/" + relative,
                            "source_sha256": digest, "bundled_sha256": digest})
        (self.root / "sources.json").write_text(json.dumps({"files": entries, "claude_curation": {"edited_files": []}}))
        manifest = self.root / ".claude-plugin/plugin.json"
        manifest.parent.mkdir()
        manifest.write_text(json.dumps({"name": "nextflow", "version": "0.3.0", "description": "Pipeline authoring"}))
        (self.root / ".claude-plugin/marketplace.json").write_text(json.dumps({"name": "nextflow-claude-plugin", "owner": {"name": "Seqera"}, "plugins": [{"name": "nextflow", "source": "./", "version": "0.3.0"}]}))
        (self.root / ".mcp.json").write_text('{"mcpServers": {"seqera": {"type": "http", "url": "https://mcp.seqera.io/mcp"}}}')
        self.plan = self.root / "packs.json"
        self.plan.write_text(json.dumps({"core": ["owner"], "packs": [{"name": "nextflow-provenance", "description": "History", "skills": ["history"]}], "resources": []}))

    def run_cli(self):
        return subprocess.run([sys.executable, "-I", str(CLI), "--root", str(self.root), "--plan", str(self.plan)], text=True, capture_output=True)

    def test_moves_complete_skill_and_preserves_original_provenance(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({p.name for p in (self.root / "skills").iterdir()}, {"owner"})
        pack = self.root / "packs/nextflow-provenance"
        self.assertEqual((pack / "skills/history/references/details.md").read_text(), "Preserve cache semantics.\n")
        self.assertEqual((pack / "skills/history/scripts/check.sh").read_text(), "#!/bin/sh\nprintf 'history checked\\n'\n")
        self.assertIn("[details](references/details.md)", (pack / "skills/history/SKILL.md").read_text())
        self.assertIn("`nextflow:owner`", (pack / "skills/history/SKILL.md").read_text())
        self.assertNotIn("../owner/SKILL.md", (pack / "skills/history/SKILL.md").read_text())
        self.assertIn("`nextflow-provenance:history`", (self.root / "skills/owner/SKILL.md").read_text())
        manifest = json.loads((pack / ".claude-plugin/plugin.json").read_text())
        self.assertNotIn("dependencies", manifest)  # Installing a pack must not silently install core.
        self.assertFalse((pack / ".mcp.json").exists())
        sources = json.loads((self.root / "sources.json").read_text())
        moved = next(e for e in sources["files"] if e["path"].endswith("history/references/details.md"))
        self.assertEqual(moved["source"], "upstream/skills/history/references/details.md")
        for entry in sources["files"]:
            self.assertEqual(entry["bundled_sha256"], hashlib.sha256((self.root / entry["path"]).read_bytes()).hexdigest())
        local_sources = json.loads((pack / "sources.json").read_text())
        self.assertIn("skills/history/references/details.md", {e["path"] for e in local_sources["files"]})
        for entry in local_sources["files"]:
            self.assertEqual(entry["bundled_sha256"], hashlib.sha256((pack / entry["path"]).read_bytes()).hexdigest())
        marketplace = json.loads((self.root / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual([(p["name"], p["source"]) for p in marketplace["plugins"]], [("nextflow", "./"), ("nextflow-provenance", "./packs/nextflow-provenance")])

    def test_completed_generation_is_byte_identical_on_replay(self):
        self.assertEqual(self.run_cli().returncode, 0)
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.run_cli().returncode, 0)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_unknown_inventory_fails_before_moving_anything(self):
        rogue = self.root / "skills/unclassified/SKILL.md"
        rogue.parent.mkdir()
        rogue.write_text("unexpected upstream skill")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skill pack inventory mismatch", result.stderr)
        self.assertTrue((self.root / "skills/history/SKILL.md").is_file())
        self.assertFalse((self.root / "packs").exists())

    def test_missing_generated_resource_is_not_an_idempotent_success(self):
        self.assertEqual(self.run_cli().returncode, 0)
        (self.root / "packs/nextflow-provenance/skills/history/references/details.md").unlink()
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing bundled file", result.stderr)

    def test_unrecorded_imported_asset_is_kept_with_an_explicit_origin_gap(self):
        asset = self.root / "skills/history/requirements.txt"
        asset.write_text("pyyaml\n")
        self.assertEqual(self.run_cli().returncode, 0)
        sources = json.loads((self.root / "sources.json").read_text())
        entry = next(e for e in sources["files"] if e["path"].endswith("requirements.txt"))
        self.assertEqual(entry["source_sha256"], hashlib.sha256(b"pyyaml\n").hexdigest())
        self.assertIn("No upstream provenance entry", entry["note"])
        self.assertEqual((self.root / entry["path"]).read_text(), "pyyaml\n")

    def check_cli(self):
        return subprocess.run([sys.executable, "-I", str(CLI.with_name("check_sources.py")), "--root", str(self.root)], text=True, capture_output=True)

    def test_checker_rejects_a_link_that_only_works_in_the_monorepo(self):
        self.assertEqual(self.run_cli().returncode, 0)
        path = self.root / "packs/nextflow-provenance/skills/history/SKILL.md"
        path.write_text(path.read_text() + "\n[unsafe](../../../../skills/owner/SKILL.md)\n")
        result = self.check_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("link escapes installed plugin", result.stderr)

    def test_checker_rejects_a_duplicate_server_in_an_optional_pack(self):
        self.assertEqual(self.run_cli().returncode, 0)
        path = self.root / "packs/nextflow-provenance/.mcp.json"
        path.write_text('{"mcpServers": {"seqera": {}}}')
        result = self.check_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate MCP connection", result.stderr)

    def test_checker_rejects_a_manifest_version_mismatch(self):
        self.assertEqual(self.run_cli().returncode, 0)
        path = self.root / "packs/nextflow-provenance/.claude-plugin/plugin.json"
        manifest = json.loads(path.read_text())
        manifest["version"] = "99.0.0"
        path.write_text(json.dumps(manifest))
        result = self.check_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("name/version mismatch", result.stderr)

    def test_duplicate_assignment_is_rejected(self):
        plan = json.loads(self.plan.read_text())
        plan["packs"][0]["skills"].append("owner")
        self.plan.write_text(json.dumps(plan))
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("assigned more than once", result.stderr)


if __name__ == "__main__":
    unittest.main()
