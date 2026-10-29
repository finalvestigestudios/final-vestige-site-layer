"""R37: synthetic offline candidate-package hardening, never executing binaries."""
from __future__ import annotations

import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from candidate_guard import (
    CandidateGuardError, MAX_EXE_BYTES, MAX_CHECKSUM_BYTES,
    check_candidate_directory, read_checksum_candidate, sha256_candidate,
)

APPS = (
    "LedgerDiffLite.exe", "InvoiceTwinScout.exe", "SpendMapLite.exe",
    "PolicyDeltaDesk.exe", "GrantAuditStudioPro.exe", "ProcureGuardStudioPro.exe",
)


class CandidateGuardR37Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r37-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.payloads = {}
        entries = []
        for index, name in enumerate(APPS):
            data = bytes([index + 1]) * 512
            self.payloads[name] = data
            (self.root / name).write_bytes(data)
            entries.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
        self.inventory = self.root / "SHA256SUMS.txt"
        self.inventory.write_text("\n".join(entries) + "\n", encoding="ascii")

    def check(self):
        check_candidate_directory(self.root, APPS)

    def test_exact_seven_file_candidate(self):
        self.check()

    def test_all_six_digests_are_precise(self):
        for app in APPS:
            self.assertEqual(sha256_candidate(self.root / app), hashlib.sha256(self.payloads[app]).hexdigest())

    def test_checksum_bytes_are_identical(self):
        self.assertEqual(read_checksum_candidate(self.inventory), self.inventory.read_bytes())

    def test_extra_json_report_rejected(self):
        (self.root / "offline-candidate-evidence.json").write_text("{}")
        with self.assertRaisesRegex(CandidateGuardError, "unapproved"):
            self.check()

    def test_secret_file_cannot_be_accidentally_bundled(self):
        (self.root / "premium-license-private.key").write_bytes(b"secret")
        with self.assertRaises(CandidateGuardError) as raised:
            self.check()
        self.assertNotIn("premium-license-private.key", str(raised.exception))

    def test_hidden_payload_rejected(self):
        (self.root / ".exfiltration").write_text("x")
        with self.assertRaises(CandidateGuardError):
            self.check()

    def test_directory_payload_rejected(self):
        (self.root / "support").mkdir()
        with self.assertRaises(CandidateGuardError):
            self.check()

    def test_unknown_executable_rejected(self):
        (self.root / "unknown.exe").write_bytes(b"MZ")
        with self.assertRaises(CandidateGuardError):
            self.check()

    def test_missing_expected_binary_rejected(self):
        (self.root / APPS[0]).unlink()
        with self.assertRaises(CandidateGuardError):
            self.check()

    def test_missing_checksum_file_rejected(self):
        self.inventory.unlink()
        with self.assertRaises(CandidateGuardError):
            self.check()

    def test_bad_case_variant_rejected(self):
        (self.root / APPS[0]).rename(self.root / APPS[0].lower())
        with self.assertRaises(CandidateGuardError):
            self.check()

    def test_expected_symlink_rejected(self):
        target = self.root / APPS[0]
        target.unlink()
        try:
            target.symlink_to(self.root / APPS[1])
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unsupported on this host")
        with self.assertRaises(CandidateGuardError):
            self.check()
        with self.assertRaises(CandidateGuardError):
            sha256_candidate(target)

    def test_inventory_symlink_rejected(self):
        self.inventory.unlink()
        try:
            self.inventory.symlink_to(self.root / APPS[0])
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unsupported")
        with self.assertRaises(CandidateGuardError):
            read_checksum_candidate(self.inventory)

    def test_hardlink_alias_rejected(self):
        target = self.root / APPS[1]
        target.unlink()
        try:
            os.link(self.root / APPS[0], target)
        except OSError:
            self.skipTest("Hardlinks unsupported")
        with self.assertRaises(CandidateGuardError):
            self.check()
        with self.assertRaises(CandidateGuardError):
            sha256_candidate(target)

    def test_executable_size_limit_prevents_hashing(self):
        with (self.root / APPS[0]).open("wb") as stream:
            stream.truncate(MAX_EXE_BYTES + 1)
        with self.assertRaisesRegex(CandidateGuardError, "safety limit"):
            sha256_candidate(self.root / APPS[0])

    def test_checksum_size_limit_prevents_read(self):
        with self.inventory.open("wb") as stream:
            stream.truncate(MAX_CHECKSUM_BYTES + 1)
        with self.assertRaisesRegex(CandidateGuardError, "safety limit"):
            read_checksum_candidate(self.inventory)

    @unittest.skipIf(os.name == "nt", "Windows sharing prevents guaranteed concurrent writes")
    def test_detect_same_length_edit_while_streaming(self):
        import candidate_guard
        path = self.root / APPS[0]
        actual = candidate_guard._read_chunks
        def tamper(stream):
            for chunk in actual(stream):
                path.write_bytes(b"X" * len(chunk))
                yield chunk
        with patch.object(candidate_guard, "_read_chunks", side_effect=tamper):
            with self.assertRaisesRegex(CandidateGuardError, "changed"):
                sha256_candidate(path)

    @unittest.skipIf(os.name == "nt", "Windows sharing prevents guaranteed open-handle unlink")
    def test_detect_path_replacement_while_streaming(self):
        import candidate_guard
        path = self.root / APPS[0]
        actual = candidate_guard._read_chunks
        def swap(stream):
            for chunk in actual(stream):
                path.unlink()
                path.write_bytes(chunk)
                yield chunk
        with patch.object(candidate_guard, "_read_chunks", side_effect=swap):
            with self.assertRaisesRegex(CandidateGuardError, "changed"):
                sha256_candidate(path)

    @unittest.skipIf(os.name == "nt", "Windows sharing prevents guaranteed open-handle unlink")
    def test_detect_candidate_swap_to_symlink_after_open(self):
        import candidate_guard
        path = self.root / APPS[0]
        actual = candidate_guard._read_chunks
        def swap(stream):
            for chunk in actual(stream):
                path.unlink()
                try:
                    path.symlink_to(self.root / APPS[1])
                except (OSError, NotImplementedError):
                    self.skipTest("Symlinks unsupported")
                yield chunk
        with patch.object(candidate_guard, "_read_chunks", side_effect=swap):
            with self.assertRaises(CandidateGuardError):
                sha256_candidate(path)

    def test_empty_inventory_read_is_bounded(self):
        self.inventory.write_bytes(b"")
        self.assertEqual(read_checksum_candidate(self.inventory), b"")

    def test_package_directory_symlink_rejected(self):
        link = self.root.parent / (self.root.name + "-alias")
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unsupported")
        self.addCleanup(link.unlink)
        with self.assertRaisesRegex(CandidateGuardError, "real directory"):
            check_candidate_directory(link, APPS)

    def test_unknown_file_is_never_disclosed_in_error(self):
        private = self.root / "Secret Client Name customer.csv"
        private.write_text("private")
        with self.assertRaises(CandidateGuardError) as raised:
            self.check()
        self.assertNotIn("Secret Client Name", str(raised.exception))
        self.assertNotIn(str(self.root), str(raised.exception))


if __name__ == "__main__":
    unittest.main()
