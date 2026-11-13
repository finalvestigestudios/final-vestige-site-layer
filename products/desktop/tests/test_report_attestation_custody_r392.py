"""R392: private offline attestation JSON / path / handle custody.

Synthetic bytes only; does not prove any Windows executable is safe to ship.
The three NTFS junction cases run only on a genuine Windows runner.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_attestation as target

PRIVATE = "PRIVATE_ACCOUNT_4817_DO_NOT_DISCLOSE"


class AttestationCustodyR392(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidates = self.root / "dist"
        self.candidates.mkdir()
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.report = self.evidence / "receipt.json"
        self.raw = b'{"synthetic":true}'
        self.report.write_bytes(self.raw)

    def reject(self, func, *args, expected=None):
        with self.assertRaises(target.ReportAttestationError) as caught:
            func(*args)
        error = caught.exception
        if expected:
            self.assertIn(expected, str(error))
        self.assertNotIn(PRIVATE, str(error))
        self.assertIsNone(error.__cause__)
        self.assertIsNone(error.__context__)

    def test_valid_read_preserves_bytes_and_hash(self):
        data, digest = target._read_verified_report(self.report, self.candidates)
        self.assertEqual(data, self.raw)
        self.assertEqual(digest, hashlib.sha256(self.raw).hexdigest())

    def test_second_read_is_deterministic(self):
        self.assertEqual(target._read_verified_report(self.report, self.candidates),
                         target._read_verified_report(self.report, self.candidates))

    def test_bad_json_discards_sensitive_decoder_context(self):
        self.reject(target._validate_report, ('{"' + PRIVATE + '":').encode(),
                    expected="Malformed verification JSON")

    def test_invalid_utf8_discards_sensitive_byte_context(self):
        self.reject(target._validate_report, PRIVATE.encode() + b"\xff",
                    expected="Malformed verification JSON")

    def test_private_malformed_list_fails_without_private_message(self):
        self.reject(target._validate_report, (PRIVATE + "[,]").encode(),
                    expected="Malformed verification JSON")

    def test_duplicate_object_key_fails_closed(self):
        self.reject(target._validate_report, b'{"x":1,"x":2}',
                    expected="Duplicate JSON key")

    def test_nonfinite_constant_fails_closed(self):
        self.reject(target._validate_report, b'{"x":NaN}',
                    expected="Nonfinite numeric evidence")

    def test_unexpected_scalar_fails_closed(self):
        self.reject(target._validate_report, b'"' + PRIVATE.encode() + b'"',
                    expected="Unexpected verification schema")

    def test_valid_report_schema_retains_six_names_and_hold(self):
        sample = {
            "schema": 1, "status": "integrity_only",
            "release_authorized": False, "premium_entitlement_verified": False,
            "codesigning_verified": False, "malware_scan_verified": False,
            "verified_utc": "2026-11-12T01:02:03+00:00",
            "checksums_sha256": "a" * 64,
            "windows_executables_verified": False, "smoke_simulated": False,
            "artifacts": [
                {"name": n, "sha256": "b" * 64, "pe_machine": "AMD64",
                 "smoke": "not_run"} for n in target.gate.EXPECTED
            ],
        }
        self.assertEqual(target._validate_report(
            json.dumps(sample).encode("utf-8")), sample)

    def test_invalid_calendar_discards_datetime_error_context(self):
        # A syntactically shaped UTC timestamp with impossible calendar fields
        # must not preserve the original ValueError as __context__.
        sample = {key: False for key in target.REPORT_KEYS}
        sample.update(schema=1, status="integrity_only",
                      verified_utc="2026-99-99T99:99:99+00:00",
                      windows_executables_verified=False, smoke_simulated=False)
        with patch.object(target.json, "loads", return_value=sample):
            self.reject(target._validate_report, b'{}',
                        expected="Invalid verification timestamp")

    def test_candidate_gate_failure_discards_private_context(self):
        # The attestation report is deliberately synthetic, not a release.
        with patch.object(target, "_read_verified_report",
                          return_value=(self.raw, "a" * 64)):
            with patch.object(target, "_validate_report",
                              return_value={"checksums_sha256": "b" * 64}):
                with patch.object(target.gate, "verify",
                                  side_effect=OSError(PRIVATE)):
                    self.reject(target.verify_report, self.report,
                                self.candidates,
                                expected="Candidate executable verification failed")

    def test_empty_report_rejected(self):
        self.report.write_bytes(b"")
        self.reject(target._read_verified_report, self.report, self.candidates,
                    expected="bounded ordinary")

    def test_oversized_report_rejected(self):
        self.report.write_bytes(b"x" * (target.MAX_REPORT_BYTES + 1))
        self.reject(target._read_verified_report, self.report, self.candidates,
                    expected="bounded ordinary")

    def test_report_inside_binary_directory_rejected(self):
        internal = self.candidates / "candidate.json"
        internal.write_bytes(self.raw)
        self.reject(target._read_verified_report, internal, self.candidates,
                    expected="inside the candidate directory")

    def test_report_symlink_rejected(self):
        link = self.root / "report-link.json"
        try:
            link.symlink_to(self.report)
        except (OSError, NotImplementedError):
            self.skipTest("filesystem symlinks not permitted")
        self.reject(target._read_verified_report, link, self.candidates)

    def test_parent_symlink_rejected_before_open(self):
        link = self.root / "alias"
        try:
            link.symlink_to(self.evidence, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("filesystem symlinks not permitted")
        with patch.object(target.os, "open", side_effect=AssertionError("opened alias")):
            self.reject(target._read_verified_report, link / self.report.name, self.candidates)

    def test_nested_symlink_parent_rejected(self):
        nested = self.evidence / "nested"
        nested.mkdir()
        path = nested / "another.json"
        path.write_bytes(self.raw)
        link = self.root / "alias"
        try:
            link.symlink_to(self.evidence, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("filesystem symlinks not permitted")
        self.reject(target._read_verified_report, link / "nested" / path.name, self.candidates)

    def test_explicit_parent_traversal_rejected(self):
        self.reject(target._read_verified_report,
                    self.evidence / "ghost" / ".." / self.report.name, self.candidates)

    def test_hardlinked_report_rejected(self):
        link = self.root / "hardlink.json"
        os.link(self.report, link)
        self.reject(target._read_verified_report, self.report, self.candidates,
                    expected="bounded ordinary")

    def test_private_open_failure_has_no_retained_context(self):
        with patch.object(target.os, "open", side_effect=OSError(PRIVATE)):
            self.reject(target._read_verified_report, self.report, self.candidates,
                        expected="could not be read safely")

    def test_private_ancestor_error_has_no_retained_context(self):
        with patch.object(Path, "lstat", side_effect=OSError(PRIVATE)):
            self.reject(target._read_verified_report, self.report, self.candidates,
                        expected="could not be read safely")

    def test_fdopen_failure_closes_owned_descriptor(self):
        owned = []
        real_open = target.os.open
        def capture(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            owned.append(fd)
            return fd
        with patch.object(target.os, "open", side_effect=capture):
            with patch.object(target.os, "fdopen", side_effect=OSError(PRIVATE)):
                self.reject(target._read_verified_report, self.report, self.candidates,
                            expected="could not be read safely")
        self.assertEqual(len(owned), 1)
        with self.assertRaises(OSError):
            os.fstat(owned[0])

    def test_in_flight_parent_change_rejected(self):
        original = target.snapshot_candidate_parents
        calls = 0
        def changed(path):
            nonlocal calls
            calls += 1
            result = original(path)
            if calls == 2:
                return result[:-1] + (("different-parent", *result[-1][1:]),)
            return result
        with patch.object(target, "snapshot_candidate_parents", side_effect=changed):
            self.reject(target._read_verified_report, self.report, self.candidates,
                        expected="changed during reading")

    def test_windows_reparse_path_metadata_rejected(self):
        with patch.object(target, "unsafe_windows_reparse", return_value=True):
            self.reject(target._read_verified_report, self.report, self.candidates,
                        expected="bounded ordinary")

    def test_windows_reparse_descriptor_metadata_rejected(self):
        actual = target.unsafe_windows_reparse
        checks = 0
        def reparse(info):
            nonlocal checks
            checks += 1
            return checks == 2
        with patch.object(target, "unsafe_windows_reparse", side_effect=reparse):
            self.reject(target._read_verified_report, self.report, self.candidates,
                        expected="changed during opening")
        self.assertGreaterEqual(checks, 2)

    def test_rejection_does_not_modify_original_report(self):
        original = self.report.read_bytes()
        with patch.object(target.os, "open", side_effect=OSError(PRIVATE)):
            self.reject(target._read_verified_report, self.report, self.candidates)
        self.assertEqual(self.report.read_bytes(), original)

    @unittest.skipUnless(os.name == "nt", "requires native NTFS Windows runner")
    def test_native_ntfs_junction_parent_rejected(self):
        junction = self.root / "ntfs-junction"
        proc = subprocess.run(["cmd.exe", "/D", "/C", "mklink", "/J",
                               str(junction), str(self.evidence)],
                              capture_output=True, check=False)
        if proc.returncode:
            self.fail("Windows NTFS junction fixture unavailable: HOLD")
        self.reject(target._read_verified_report,
                    junction / self.report.name, self.candidates)

    @unittest.skipUnless(os.name == "nt", "requires native NTFS Windows runner")
    def test_native_ntfs_junction_nested_parent_rejected(self):
        nested = self.evidence / "subdir"
        nested.mkdir()
        child = nested / "receipt.json"
        child.write_bytes(self.raw)
        junction = self.root / "ntfs-junction"
        proc = subprocess.run(["cmd.exe", "/D", "/C", "mklink", "/J",
                               str(junction), str(self.evidence)],
                              capture_output=True, check=False)
        if proc.returncode:
            self.fail("Windows NTFS junction fixture unavailable: HOLD")
        self.reject(target._read_verified_report,
                    junction / "subdir" / "receipt.json", self.candidates)


if __name__ == "__main__":
    unittest.main()
