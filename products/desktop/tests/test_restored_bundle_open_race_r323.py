"""R323 offline, synthetic premium evidence: nonblocking descriptor-open custody.

POSIX FIFO-swap cases run in killable children, so the predecessor's blocking
O_RDONLY bug is a bounded test failure rather than a hung CI job. Windows runs
portable normal-path tests without claiming POSIX FIFO semantics there.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import verify_restored_bundle_r320 as inspector


_CHILD = r'''
import os, sys
from pathlib import Path
from scripts import verify_restored_bundle_r320 as v
folder, target = Path(sys.argv[1]), sys.argv[2]
real_open = os.open
swapped = False

def racing_open(path, flags, *args, **kwargs):
    global swapped
    if not swapped and Path(path).name == target:
        swapped = True
        os.unlink(path)
        os.mkfifo(path)
    return real_open(path, flags, *args, **kwargs)

v.os.open = racing_open
try:
    v.inspect_bundle(folder)
except v.BundleHold as exc:
    if swapped and str(exc) == v.ERROR and exc.__context__ is None:
        print("HOLD")
        raise SystemExit(0)
    raise SystemExit(3)
raise SystemExit(4)
'''


class RestoredBundleOpenRaceR323(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r323-synthetic-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name) / "evidence"
        self.folder.mkdir()
        self.report = b"ref,amount\nSYNTHETIC-1,18.20\n"
        self.journal = b'{"review":"pending"}\n'
        self.write_bundle("grants", True)

    @staticmethod
    def digest(raw):
        return hashlib.sha256(raw).hexdigest()

    def write_bundle(self, product, with_journal):
        (self.folder / inspector.REPORT).write_bytes(self.report)
        if with_journal:
            (self.folder / inspector.JOURNAL).write_bytes(self.journal)
        else:
            (self.folder / inspector.JOURNAL).unlink(missing_ok=True)
        manifest = {
            "schema": 1, "product": product,
            "sealed_utc": "2026-11-09T10:05:00+00:00",
            "report_filename": "synthetic.csv",
            "report_sha256": self.digest(self.report),
            "journal_filename": "synthetic.jsonl" if with_journal else None,
            "journal_sha256": self.digest(self.journal) if with_journal else None,
            "journal_present": with_journal,
            "review_event_count": 1 if with_journal else 0,
        }
        (self.folder / inspector.MANIFEST).write_text(
            json.dumps(manifest), encoding="utf-8")

    def test_all_four_normal_product_journal_combinations(self):
        for product in ("grants", "procurement"):
            for has_journal in (False, True):
                with self.subTest(product=product, journal=has_journal):
                    self.write_bundle(product, has_journal)
                    receipt = inspector.inspect_bundle(self.folder)
                    self.assertEqual(receipt["product"], product)
                    self.assertEqual(receipt["members_verified"], 3 if has_journal else 2)
                    self.assertFalse(receipt["source_authenticated"])
                    self.assertFalse(receipt["release_authorized"])
                    self.assertTrue(receipt["review_required"])

    def test_nonblocking_open_flag_on_every_restored_member(self):
        if not hasattr(os, "O_NONBLOCK"):
            self.skipTest("O_NONBLOCK not exposed on this platform")
        actual_open = os.open
        opens = []

        def record_open(path, flags, *args, **kwargs):
            opens.append((Path(path).name, flags))
            return actual_open(path, flags, *args, **kwargs)

        with mock.patch.object(inspector.os, "open", side_effect=record_open):
            inspector.inspect_bundle(self.folder)
        self.assertEqual(
            [name for name, _ in opens],
            [inspector.MANIFEST, inspector.REPORT, inspector.JOURNAL,
             inspector.REPORT, inspector.JOURNAL, inspector.MANIFEST])
        for filename, flags in opens:
            with self.subTest(filename=filename):
                self.assertNotEqual(flags & os.O_NONBLOCK, 0)

    def test_report_and_manifest_open_flags_without_journal(self):
        self.write_bundle("procurement", False)
        flags_seen = []
        original = os.open

        def capture(path, flags, *a, **kw):
            flags_seen.append((Path(path).name, flags))
            return original(path, flags, *a, **kw)

        with mock.patch.object(inspector.os, "open", side_effect=capture):
            receipt = inspector.inspect_bundle(self.folder)
        self.assertEqual(receipt["members_verified"], 2)
        self.assertEqual([name for name, _ in flags_seen],
                         [inspector.MANIFEST, inspector.REPORT,
                          inspector.REPORT, inspector.MANIFEST])
        if hasattr(os, "O_NONBLOCK"):
            self.assertTrue(all(flags & os.O_NONBLOCK for _, flags in flags_seen))

    def test_inspector_does_not_write_to_normal_bundle(self):
        before = {p.name: p.read_bytes() for p in self.folder.iterdir()}
        inspector.inspect_bundle(self.folder)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.folder.iterdir()})

    def test_external_witness_unchanged_and_private(self):
        receipt = inspector.inspect_with_external_witness(
            self.folder, product="grants", report_sha256=self.digest(self.report),
            journal_sha256=self.digest(self.journal))
        self.assertTrue(receipt["external_witness_matched"])
        self.assertFalse(receipt["source_authenticated"])
        with self.assertRaises(inspector.BundleHold) as failed:
            inspector.inspect_with_external_witness(
                self.folder, product="grants", report_sha256="0" * 64,
                journal_sha256=self.digest(self.journal))
        self.assertEqual(str(failed.exception), inspector.ERROR)
        self.assertIsNone(failed.exception.__context__)

    def test_original_fifo_is_rejected_before_open(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("requires POSIX FIFO")
        path = self.folder / inspector.REPORT
        path.unlink()
        os.mkfifo(path)
        with self.assertRaises(inspector.BundleHold) as failed:
            inspector.inspect_bundle(self.folder)
        self.assertEqual(str(failed.exception), inspector.ERROR)
        self.assertIsNone(failed.exception.__context__)

    def _raced_member_holds_without_hanging(self, member):
        if not (hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK")):
            self.skipTest("requires POSIX FIFO and O_NONBLOCK")
        # Kill the child on timeout. Predecessor lacks O_NONBLOCK and hangs.
        outcome = subprocess.run(
            [sys.executable, "-c", _CHILD, str(self.folder), member],
            capture_output=True, text=True, timeout=4,
            env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])},
        )
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertEqual(outcome.stdout.strip(), "HOLD")
        self.assertNotIn(str(self.folder), outcome.stdout + outcome.stderr)

    def test_manifest_swapped_for_fifo_between_lstat_and_open(self):
        self._raced_member_holds_without_hanging(inspector.MANIFEST)

    def test_report_swapped_for_fifo_between_lstat_and_open(self):
        self._raced_member_holds_without_hanging(inspector.REPORT)

    def test_journal_swapped_for_fifo_between_lstat_and_open(self):
        self._raced_member_holds_without_hanging(inspector.JOURNAL)


if __name__ == "__main__":
    unittest.main()
