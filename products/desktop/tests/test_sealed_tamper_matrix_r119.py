"""R119 adverse-case contracts for all eight sealed records (synthetic bytes).

The Windows CI integration separately exercises ACTUAL six native-smoked EXEs.
These tests never assert physical Win11 acceptance, malware clearance or release.
"""
from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sealed_candidate_handoff_r117 as handoff
import sealed_tamper_matrix_r119 as matrix


class AllEntryTamperR119Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.work = self.root / "private-work"
        self.work.mkdir(mode=0o700)
        self.dist = self.root / "dist"
        self.dist.mkdir()
        self.r9 = self.root / "r9.json"
        self.r9.write_bytes(b'{"synthetic":"not a native Windows report"}')
        for index, name in enumerate(handoff.NAMES):
            (self.dist / name).write_bytes(b"MZ SYNTHETIC NOT AN EXE" + bytes([index + 3]) * 37)
        (self.dist / "SHA256SUMS.txt").write_bytes(b"FAKE - NO RELEASE\n")
        self.custody_patch = mock.patch.object(handoff, "_custody", return_value=None)
        self.custody_patch.start()
        self.addCleanup(self.custody_patch.stop)

    def run_matrix(self):
        return matrix.verify_all_entry_tamper_rejection(self.dist, self.r9, self.work)

    def assert_clean(self):
        self.assertEqual(list(self.work.iterdir()), [])

    def test_six_app_and_two_evidence_records_have_16_fail_closed_cases(self):
        response = self.run_matrix()
        self.assertEqual(response["private_records_checked"], 8)
        self.assertEqual(response["six_exes"], 6)
        self.assertEqual(response["tamper_cases_rejected"], 16)
        self.assertEqual(response["status"], "CI_EPHEMERAL_ALL_ENTRY_TAMPER_REJECTION_ONLY")
        self.assertFalse(response["release_authorized"])
        self.assertFalse(response["premium_distribution_authorized"])
        self.assertFalse(response["independent_r9_pin"])
        self.assertFalse(response["physical_windows11_acceptance"])
        self.assert_clean()

    def test_never_modifies_original_executable_or_r9_bytes(self):
        paths = handoff._paths(self.dist, self.r9)
        before = {name: handoff._hash(path) for name, path in paths.items()}
        self.run_matrix()
        self.assertEqual(before, {name: handoff._hash(path) for name, path in paths.items()})
        self.assert_clean()

    def test_all_six_executable_names_and_two_evidence_names_remain_exact(self):
        self.assertEqual(len(handoff.NAMES), 6)
        self.assertEqual(len(handoff.ENTRIES), 8)
        self.assertEqual([n.removeprefix("exes/") for n in handoff.ENTRIES[:6]],
                         list(handoff.NAMES))
        self.assertEqual(handoff.ENTRIES[-2:],
                         ("exes/SHA256SUMS.txt", "evidence/r9-report.json"))

    def test_missing_first_executable_fails_before_bundle_creation(self):
        (self.dist / handoff.NAMES[0]).unlink()
        with self.assertRaises(OSError):
            self.run_matrix()
        self.assert_clean()

    def test_bad_r9_custody_fails_before_key_generation(self):
        with mock.patch.object(handoff, "_custody",
                               side_effect=handoff.HandoffHold("private location")):
            with self.assertRaises(handoff.HandoffHold):
                self.run_matrix()
        self.assert_clean()

    def test_sealer_forged_release_claim_fails_closed(self):
        seal = handoff.seal

        def forged(*args):
            result = seal(*args)
            return {**result, "release_authorized": True}

        with mock.patch.object(handoff, "seal", side_effect=forged):
            with self.assertRaises(matrix.MatrixHold):
                self.run_matrix()
        self.assert_clean()

    def test_unsealer_that_accepts_modified_ciphertext_fails(self):
        with mock.patch.object(handoff, "unseal", return_value={
                "status": "FAKE", "six_exes": 6, "release_authorized": False}):
            with self.assertRaises(matrix.MatrixHold):
                self.run_matrix()
        self.assert_clean()

    def test_dishonest_acceptance_on_last_tag_is_detected(self):
        unseal = handoff.unseal
        calls = 0

        def dishonest(*args):
            nonlocal calls
            calls += 1
            if calls == 16:
                return {"status": "FAKE", "release_authorized": False}
            return unseal(*args)

        with mock.patch.object(handoff, "unseal", side_effect=dishonest):
            with self.assertRaises(matrix.MatrixHold):
                self.run_matrix()
        self.assertEqual(calls, 16)
        self.assert_clean()

    def test_all_mutations_are_reverted_when_decryptor_fails_unexpectedly(self):
        # A non-HandoffHold error is NOT considered authentication rejection.
        seen_hashes = []
        unseal = handoff.unseal

        def failed(*args):
            seen_hashes.append(handoff._hash(args[0]))
            raise OSError("synthetic private failure")

        with mock.patch.object(handoff, "unseal", side_effect=failed):
            with self.assertRaises(OSError):
                self.run_matrix()
        self.assertEqual(len(seen_hashes), 1)
        self.assert_clean()
        self.assertNotEqual(seen_hashes[0], "")

    def test_unseal_cannot_leave_a_published_intake_when_it_rejects(self):
        unseal = handoff.unseal

        def dishonest(*args):
            destination = Path(args[3])
            destination.mkdir()
            raise handoff.HandoffHold("synthetic rejected after bad publication")

        with mock.patch.object(handoff, "unseal", side_effect=dishonest):
            with self.assertRaises(matrix.MatrixHold):
                self.run_matrix()
        # Temporary private staging must still be cleaned even after failure.
        self.assert_clean()

    def test_relative_private_work_directory_is_denied(self):
        with self.assertRaises(matrix.MatrixHold):
            matrix.verify_all_entry_tamper_rejection(self.dist, self.r9, "relative-dir")
        self.assert_clean()

    def test_scratch_under_candidate_directory_is_denied(self):
        with self.assertRaises(matrix.MatrixHold):
            matrix.verify_all_entry_tamper_rejection(self.dist, self.r9, self.dist)
        self.assert_clean()

    def test_symlink_private_work_directory_is_denied(self):
        link = self.root / "link-to-work"
        try:
            link.symlink_to(self.work, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this runner")
        with self.assertRaises(handoff.HandoffHold):
            matrix.verify_all_entry_tamper_rejection(self.dist, self.r9, link)
        self.assert_clean()

    def test_invalid_pin_cannot_be_parsed_as_layout(self):
        with self.assertRaises(handoff.HandoffHold):
            matrix._layout(self.r9, "bad-pin")

    def test_bad_bundle_magic_is_rejected(self):
        with self.assertRaises(matrix.MatrixHold):
            matrix._layout(self.r9, handoff._hash(self.r9))

    def test_change_byte_disallows_negative_and_out_of_file_offsets(self):
        with self.assertRaises(matrix.MatrixHold):
            matrix._change_one_byte(self.r9, -1)
        with self.assertRaises(matrix.MatrixHold):
            matrix._change_one_byte(self.r9, self.r9.stat().st_size)
        with self.assertRaises(matrix.MatrixHold):
            matrix._change_one_byte(self.r9, 0, 256)

    def test_byte_mutation_restores_source_even_if_caller_raises(self):
        old = self.r9.read_bytes()
        with self.assertRaisesRegex(RuntimeError, "synthetic"):
            with matrix._tamper(self.r9, 1):
                self.assertNotEqual(old, self.r9.read_bytes())
                raise RuntimeError("synthetic failure")
        self.assertEqual(old, self.r9.read_bytes())

    def test_cli_private_path_does_not_escape_on_failure(self):
        private_path = self.root / "private-customer-ledger-folder"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = matrix.main([str(private_path), str(self.r9), str(self.work)])
        self.assertEqual(code, 1)
        self.assertIn("HOLD", stderr.getvalue())
        self.assertNotIn(str(private_path), stderr.getvalue())
        self.assert_clean()

    def test_cli_success_contains_explicit_release_hold_not_financial_paths(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = matrix.main([str(self.dist), str(self.r9), str(self.work)])
        self.assertEqual(exit_code, 0)
        self.assertIn("16 ciphertext/tag", stdout.getvalue())
        self.assertIn("NO release", stdout.getvalue())
        self.assertNotIn(str(self.root), stdout.getvalue())
        self.assert_clean()


if __name__ == "__main__":
    unittest.main()
