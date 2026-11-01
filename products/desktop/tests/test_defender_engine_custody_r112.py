"""R112 synthetic scanner identity regressions; no real Defender commands."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "scripts" / "defender_engine_custody_r112.py"
spec = importlib.util.spec_from_file_location("defender_engine_custody_r112", SRC)
engine = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)


class DefenderEngineCustodyR112(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scanner = self.root / "MpCmdRun.exe"
        self.scanner.write_bytes(b"synthetic scanner image for offline tests")

    def test_regular_scanner_hash_and_identity(self):
        first = engine.fingerprint(self.scanner)
        self.assertEqual(len(first.sha256), 64)
        self.assertEqual(first.path_identity[2], self.scanner.stat().st_size)
        self.assertIsNone(engine.require_same_engine(self.scanner, first))

    def test_changed_bytes_fail_even_when_same_length(self):
        original = engine.fingerprint(self.scanner)
        self.scanner.write_bytes(b"x" * self.scanner.stat().st_size)
        with self.assertRaises(engine.EngineHold):
            engine.require_same_engine(self.scanner, original)

    def test_replaced_inode_same_content_denied(self):
        original = engine.fingerprint(self.scanner)
        replacement = self.root / "replacement.exe"
        shutil.copy2(self.scanner, replacement)
        os.replace(replacement, self.scanner)
        with self.assertRaises(engine.EngineHold):
            engine.require_same_engine(self.scanner, original)

    def test_removed_scanner_refused(self):
        original = engine.fingerprint(self.scanner)
        self.scanner.unlink()
        with self.assertRaises(engine.EngineHold):
            engine.require_same_engine(self.scanner, original)

    def test_reject_wrong_pin_type(self):
        with self.assertRaises(engine.EngineHold):
            engine.require_same_engine(self.scanner, {"sha256": "a" * 64})

    def test_empty_scanner_rejected(self):
        self.scanner.write_bytes(b"")
        with self.assertRaises(engine.EngineHold):
            engine.fingerprint(self.scanner)

    def test_scanner_exceeds_bound(self):
        with patch.object(engine, "MAX_SCANNER_BYTES", 3):
            with self.assertRaises(engine.EngineHold):
                engine.fingerprint(self.scanner)

    def test_scanner_symlink_rejected(self):
        link = self.root / "linked.exe"
        try:
            link.symlink_to(self.scanner)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        with self.assertRaises(engine.EngineHold):
            engine.fingerprint(link)

    def test_scanner_hardlink_rejected(self):
        link = self.root / "hardlinked.exe"
        try:
            os.link(self.scanner, link)
        except (OSError, NotImplementedError):
            self.skipTest("hardlinks unavailable on this host")
        with self.assertRaises(engine.EngineHold):
            engine.fingerprint(self.scanner)

    def test_cross_view_ctime_parity_windows_only(self):
        sig = (1, 2, 3, 4, 5)
        altered = (1, 2, 3, 4, 8)
        self.assertTrue(engine._same_cross_view(sig, altered, windows=True))
        self.assertFalse(engine._same_cross_view(sig, altered, windows=False))

    def test_cross_view_mtime_drift_refused_even_windows(self):
        self.assertFalse(engine._same_cross_view((1,2,3,4,5), (1,2,3,8,5), windows=True))

    def test_version_parses_three_four_and_revision(self):
        self.assertEqual(engine.platform_version("4.18.10"), (4,18,10,0,0,0))
        self.assertEqual(engine.platform_version("4.18.10.7-1"), (4,18,10,7,0,1))

    def test_malformed_version_refused(self):
        for name in ("latest", "4.18", "4.18.a.0", "4.18.99.1/sneaky", "4.18.3.7-", "4.18.3.7-1abc", "1.2.3.4.5.6"):
            with self.subTest(name=name):
                self.assertIsNone(engine.platform_version(name))

    def test_platform_preference_numeric_not_lexical(self):
        base = self.root / "Platform"
        for folder in ("4.18.9", "4.18.10", "4.18.10.3-1", "4.18.10.3-2"):
            d = base / folder
            d.mkdir(parents=True)
            (d / "MpCmdRun.exe").write_bytes(b"synthetic")
        names = [p.parent.name for p in engine.installed_platform_engines(base)]
        self.assertEqual(names, ["4.18.10.3-2", "4.18.10.3-1", "4.18.10", "4.18.9"])

    def test_platform_ignores_malformed_and_missing_scanners(self):
        base = self.root / "Platform"
        (base / "bad").mkdir(parents=True)
        (base / "4.18.7").mkdir()
        (base / "4.18.8").mkdir()
        (base / "4.18.8" / "MpCmdRun.exe").write_bytes(b"synthetic")
        self.assertEqual([p.parent.name for p in engine.installed_platform_engines(base)], ["4.18.8"])

    def test_platform_symlink_folder_ignored(self):
        base = self.root / "Platform"
        base.mkdir()
        real = self.root / "real"
        real.mkdir()
        (real / "MpCmdRun.exe").write_bytes(b"synthetic")
        try:
            (base / "4.18.9").symlink_to(real, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        self.assertEqual(engine.installed_platform_engines(base), [])

    def test_platform_symlink_scanner_ignored(self):
        base = self.root / "Platform"
        directory = base / "4.18.8"
        directory.mkdir(parents=True)
        try:
            (directory / "MpCmdRun.exe").symlink_to(self.scanner)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this host")
        self.assertEqual(engine.installed_platform_engines(base), [])

    def test_missing_platform_returns_empty(self):
        self.assertEqual(engine.installed_platform_engines(self.root / "missing"), [])

    def test_scan_module_does_not_import_network_client(self):
        source = SRC.read_text(encoding="utf-8")
        self.assertNotIn("requests", source)
        self.assertNotIn("urlopen", source)
        self.assertNotIn("subprocess.run", source)


if __name__ == "__main__":
    unittest.main()
