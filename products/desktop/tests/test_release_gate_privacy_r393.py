"""R393: local-first six-app release gate must not retain sensitive exceptions.

All inputs are synthetic; these tests do not build or authorize any EXE.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import release_gate as gate

PRIVATE = "PRIVATE_LEDGER_ACCOUNT_711_DO_NOT_EXPOSE"


class ReleaseGatePrivacyR393(unittest.TestCase):
    def reject(self, function, *args, message):
        with self.assertRaises(gate.GateFailure) as captured:
            function(*args)
        error = captured.exception
        self.assertIn(message, str(error))
        self.assertNotIn(PRIVATE, str(error))
        self.assertIsNone(error.__context__)
        self.assertIsNone(error.__cause__)

    def test_pe_decoder_private_error_cannot_escape(self):
        with patch.object(gate, "verify_amd64_pe",
                          side_effect=gate.PEFormatError(PRIVATE)):
            self.reject(gate._pe64, Path("LedgerDiffLite.exe"), message="PE32+")

    def test_pe_decoder_valid_path_unchanged(self):
        with patch.object(gate, "verify_amd64_pe") as decoder:
            self.assertIsNone(gate._pe64(Path("LedgerDiffLite.exe")))
            decoder.assert_called_once()

    def test_binary_hash_private_error_cannot_escape(self):
        with patch.object(gate, "sha256_candidate",
                          side_effect=gate.CandidateGuardError(PRIVATE)):
            self.reject(gate._sha, Path("LedgerDiffLite.exe"), message="custody")

    def test_checksum_hash_private_error_cannot_escape(self):
        with patch.object(gate, "sha256_candidate",
                          side_effect=gate.CandidateGuardError(PRIVATE)):
            self.reject(gate._sha, Path("SHA256SUMS.txt"), message="custody")

    def test_valid_hash_preserved(self):
        with patch.object(gate, "sha256_candidate", return_value="a" * 64):
            self.assertEqual(gate._sha(Path("LedgerDiffLite.exe")), "a" * 64)

    def test_inventory_parser_private_error_cannot_escape(self):
        with patch.object(gate, "_regular"):
            with patch.object(gate, "read_checksum_candidate", return_value=b"fake"):
                with patch.object(gate, "parse_canonical_inventory",
                                  side_effect=gate.CanonicalInventoryError(PRIVATE)):
                    self.reject(gate._inventory, Path("synthetic"), message="inventory")

    def test_inventory_reader_private_error_cannot_escape(self):
        with patch.object(gate, "_regular"):
            with patch.object(gate, "read_checksum_candidate",
                              side_effect=gate.CandidateGuardError(PRIVATE)):
                self.reject(gate._inventory, Path("synthetic"), message="inventory")

    def test_valid_inventory_preserved(self):
        wanted = {name: "a" * 64 for name in gate.EXPECTED}
        with patch.object(gate, "_regular"):
            with patch.object(gate, "read_checksum_candidate", return_value=b"fixture"):
                with patch.object(gate, "parse_canonical_inventory", return_value=wanted):
                    self.assertEqual(gate._inventory(Path("synthetic")), wanted)

    def test_smoke_provenance_private_error_cannot_escape(self):
        with patch.object(gate, "classify_smoke",
                          side_effect=gate.SmokeProvenanceError(PRIVATE)):
            self.reject(gate.verify, Path("not-used"), message="provenance")

    def _staging(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name) / "candidate"
        root.mkdir()
        for name in gate.EXPECTED:
            (root / name).write_bytes(b"NOT_AN_EXECUTABLE")
        (root / "SHA256SUMS.txt").write_bytes(b"synthetic")
        return root

    def test_directory_guard_private_error_cannot_escape(self):
        root = self._staging()
        with patch.object(gate, "classify_smoke", return_value="integrity_only"):
            with patch.object(gate, "_regular"):
                with patch.object(gate, "check_candidate_directory",
                                  side_effect=gate.CandidateGuardError(PRIVATE)):
                    self.reject(gate.verify, root, message="staging")

    def test_recheck_guard_private_error_cannot_escape(self):
        root = self._staging()
        with patch.object(gate, "classify_smoke", return_value="integrity_only"):
            with patch.object(gate, "_regular"):
                with patch.object(gate, "_pe64"):
                    with patch.object(gate, "_sha", return_value="a" * 64):
                        with patch.object(gate, "_inventory", return_value={n: "a" * 64 for n in gate.EXPECTED}):
                            with patch.object(gate, "check_candidate_directory",
                                              side_effect=[None, gate.CandidateGuardError(PRIVATE)]):
                                self.reject(gate.verify, root, message="staging")

    def test_smoke_runner_private_error_cannot_escape(self):
        root = self._staging()
        with patch.object(gate, "classify_smoke", return_value="synthetic_smoke_only"):
            with patch.object(gate, "_regular"):
                with patch.object(gate, "_pe64"):
                    with patch.object(gate, "_sha", return_value="a" * 64):
                        with patch.object(gate, "_inventory", return_value={n: "a" * 64 for n in gate.EXPECTED}):
                            with patch.object(gate, "check_candidate_directory"):
                                with patch.object(gate, "run_smoke_checked",
                                                  side_effect=gate.SmokeRunError(PRIVATE)):
                                    self.reject(lambda: gate.verify(root, smoke=True, runner=lambda *a, **k: None),
                                                message="smoke")

    def test_failure_never_authorizes_or_runs_candidate(self):
        root = self._staging()
        with patch.object(gate, "classify_smoke", return_value="integrity_only"):
            with patch.object(gate, "_regular"):
                with patch.object(gate, "check_candidate_directory",
                                  side_effect=gate.CandidateGuardError(PRIVATE)):
                    with patch.object(gate, "run_smoke_checked") as runner:
                        self.reject(gate.verify, root, message="staging")
                        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
