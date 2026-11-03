#!/usr/bin/env python3
"""R95 adversarial tests of real R92 -> R93 -> R94 staging artifact custody."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "experience2/evidence-atlas/tools"
spec = importlib.util.spec_from_file_location("r94", TOOLS / "build_curated_atlas_r94.py")
r94 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r94)


class R95InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.basedir = tempfile.TemporaryDirectory()
        base = Path(cls.basedir.name)
        subprocess.run([sys.executable, str(TOOLS / "build_reciprocal_routes_r92.py"),
                        str(base / "r92")], check=True, stdout=subprocess.DEVNULL)
        subprocess.run([sys.executable, str(TOOLS / "build_source_passports_r93.py"),
                        "--src", str(base / "r92"), "--out", str(base / "r93")],
                       check=True, stdout=subprocess.DEVNULL)
        cls.clean = base / "r93"

    @classmethod
    def tearDownClass(cls):
        cls.basedir.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "src"
        shutil.copytree(self.clean, self.src)

    def runbuild(self):
        return r94.build(self.src, self.root / "out", self.root / "sealed.zip")

    def test_real_inherited_inventory_contains_21_regular_sources(self):
        names = {p.name for p in self.src.iterdir()}
        self.assertEqual(names, r94.R92_INPUTS | r94.R93_INPUTS)
        self.assertEqual(len(r94.verify_input_inventory(self.src)), 21)

    def test_full_archive_is_sha256_sealed_not_only_three_new_files(self):
        receipt = self.runbuild()
        self.assertEqual(len(receipt["files"]), 24)
        self.assertEqual(set(receipt["files"]),
                         {p.name for p in (self.root / "out").iterdir()
                          if p.name != "R94_ATLAS_RECEIPT.json"})
        for name, digest in receipt["files"].items():
            self.assertEqual(digest, r94.sha(self.root / "out" / name), name)
        self.assertEqual(receipt["release"], "STAGING_HOLD")
        self.assertFalse(receipt["publication_approved"])

    def test_unapproved_js_is_rejected_before_copy(self):
        (self.src / "a-new-tracker.js").write_text("fetch('https://example.com/collect')\n")
        with self.assertRaisesRegex(ValueError, "R94_UNREVIEWED_ASSET"):
            self.runbuild()
        self.assertFalse((self.root / "out").exists())

    def test_unapproved_html_is_rejected(self):
        (self.src / "surprise.html").write_text('<iframe src="https://example.com"></iframe>')
        with self.assertRaisesRegex(ValueError, "R94_UNREVIEWED_ASSET"):
            self.runbuild()

    def test_unapproved_json_is_rejected(self):
        (self.src / "extra-source.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "R94_UNREVIEWED_ASSET"):
            self.runbuild()

    def test_unapproved_directory_is_rejected(self):
        (self.src / "payload").mkdir()
        with self.assertRaisesRegex(ValueError, "R94_UNREVIEWED_ASSET"):
            self.runbuild()

    def test_inherited_symlink_not_followed(self):
        path = self.src / "reading_room_r88.js"
        moved = self.root / "outside.js"
        path.rename(moved)
        try:
            path.symlink_to(moved)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on test volume")
        with self.assertRaisesRegex(ValueError, "NONREGULAR"):
            self.runbuild()

    def test_missing_research_passport_script_fails(self):
        (self.src / "source_passports_r93.js").unlink()
        with self.assertRaisesRegex(ValueError, "R94_CUSTODY_FILE_MISSING"):
            self.runbuild()

    def test_inherited_opaque_script_mutation_fails(self):
        p = self.src / "reading_room_r88.js"
        p.write_text(p.read_text() + "\n// injected\n")
        with self.assertRaisesRegex(ValueError, "R94_INHERITED_ASSET_HASH_MISMATCH"):
            self.runbuild()

    def test_bad_inherited_asset_gate_fails(self):
        p = self.src / "R91_ASSET_BOUNDARY_RECEIPT.json"
        d = json.loads(p.read_text())
        d["network_asset_dependencies"] = 1
        p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, "R94_INHERITED_ASSET_CUSTODY_GATE"):
            self.runbuild()

    def test_inherited_receipt_is_covered_by_new_full_archive_hashes(self):
        receipt = self.runbuild()
        name = "R87_RAIL_RECEIPT.json"
        self.assertIn(name, receipt["files"])
        p = self.root / "out" / name
        p.write_text(p.read_text() + "\n")
        self.assertNotEqual(receipt["files"][name], r94.sha(p))

    def test_source_root_symlink_fails(self):
        linked = self.root / "linked-src"
        try:
            linked.symlink_to(self.src, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "R94_UNREVIEWED_ASSET"):
            r94.build(linked, self.root / "out")


if __name__ == "__main__":
    unittest.main()
