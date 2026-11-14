"""R418: one bounded source-file walk is also the only hashed manifest.

Synthetic source-only probes. They do not attest Windows binaries or authorize
premium distribution, payment approvals, or QD release.
"""
from __future__ import annotations

from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class BoundedOnePassSourceInventoryR418(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "desktop"
        self.root.mkdir()
        (self.root / "fvs_suite").mkdir()
        (self.root / "launchers").mkdir()
        (self.root / "fvs_suite" / "__init__.py").write_text(
            "# synthetic source\n", encoding="utf-8")
        (self.root / "fvs_suite" / "launcher.py").write_text(
            "import sys\n"
            "def launch(app):\n"
            "    if sys.argv[1:] != ['--smoke-test']:\n"
            "        raise SystemExit(13)\n", encoding="utf-8")
        (self.root / "offline_source_smoke_r408.py").write_bytes(
            Path(gate.__file__).read_bytes())
        for app, filename in gate.PRODUCTS:
            (self.root / "launchers" / filename).write_text(
                f"from fvs_suite.launcher import launch\nlaunch({app!r})\n",
                encoding="utf-8")

    def test_returned_manifest_covers_both_import_roots(self):
        paths = gate._verify_source_directories(self.root)
        self.assertEqual(len(paths), 8)
        self.assertTrue(any(p.parent.name == "fvs_suite" for p in paths))
        self.assertTrue(all(p.parent.name in ("fvs_suite", "launchers")
                            for p in paths))

    def test_digest_never_reenumerates_with_unbounded_rglob(self):
        with patch.object(Path, "rglob", side_effect=AssertionError(
                "unbounded source enumeration")) as forbidden:
            fingerprint = gate.source_digest(self.root)
        forbidden.assert_not_called()
        self.assertEqual(len(fingerprint), 64)

    def test_hashing_a_local_asset_changes_manifest_digest(self):
        asset = self.root / "fvs_suite" / "rules.json"
        asset.write_text('{"status":"review"}', encoding="utf-8")
        before = gate.source_digest(self.root)
        asset.write_text('{"status":"pending"}', encoding="utf-8")
        self.assertNotEqual(gate.source_digest(self.root), before)

    def test_digest_is_deterministic_across_fresh_enumeration(self):
        self.assertEqual(gate.source_digest(self.root),
                         gate.source_digest(self.root))

    def test_six_synthetic_launchers_run_in_both_modes_without_release(self):
        receipt = gate.run_gate(self.root, timeout=30)
        self.assertEqual(receipt["passed"], 12)
        self.assertEqual(receipt["required"], 12)
        self.assertFalse(receipt["release_authorized"])

    def test_513_import_files_fail_before_hash(self):
        for index in range(505):
            (self.root / "fvs_suite" / f"extra-{index}.txt").write_text(
                "x", encoding="utf-8")
        with patch.object(gate, "_read_verified_source_bytes",
                          side_effect=AssertionError("unexpected file hash")):
            with self.assertRaisesRegex(gate.SourceGateError, "safe bounds"):
                gate.source_digest(self.root)

    def test_oversized_directory_tree_is_rejected(self):
        for index in range(127):
            (self.root / "fvs_suite" / f"d{index}").mkdir()
        with self.assertRaisesRegex(gate.SourceGateError, "safe bounds"):
            gate.source_digest(self.root)

    def test_aggregate_bytes_are_rejected_before_reading(self):
        with patch.object(gate, "MAX_IMPORT_BYTES", 16):
            with patch.object(gate, "_read_verified_source_bytes",
                              side_effect=AssertionError("unexpected hash")):
                with self.assertRaisesRegex(gate.SourceGateError, "safe bounds"):
                    gate.source_digest(self.root)

    def test_compiled_import_is_never_in_manifest(self):
        (self.root / "fvs_suite" / "hidden.PyC").write_bytes(b"X")
        with self.assertRaisesRegex(gate.SourceGateError, "compiled import"):
            gate.source_digest(self.root)

    def test_hardlinked_source_is_rejected(self):
        external = Path(self.temp.name) / "private-data.txt"
        external.write_text("SECRET_CLIENT_DATA", encoding="utf-8")
        try:
            os.link(external, self.root / "fvs_suite" / "linked.txt")
        except (OSError, NotImplementedError):
            self.skipTest("hardlinks unavailable")
        with self.assertRaises(gate.SourceGateError) as caught:
            gate.source_digest(self.root)
        self.assertNotIn("SECRET_CLIENT_DATA", str(caught.exception))

    def test_symlinked_source_is_rejected(self):
        external = Path(self.temp.name) / "client-payroll.txt"
        external.write_text("SECRET_CLIENT_DATA", encoding="utf-8")
        try:
            (self.root / "fvs_suite" / "linked.txt").symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(gate.SourceGateError) as caught:
            gate.source_digest(self.root)
        self.assertNotIn("client-payroll.txt", str(caught.exception))

    def test_symlinked_import_directory_is_rejected(self):
        external = Path(self.temp.name) / "client-files"
        external.mkdir()
        try:
            (self.root / "fvs_suite" / "linked").symlink_to(
                external, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("directory symlinks unavailable")
        with self.assertRaises(gate.SourceGateError):
            gate.source_digest(self.root)


if __name__ == "__main__":
    unittest.main()
