"""R118 ephemeral six-EXE integration harness contracts (synthetic PE inputs).

The mandatory Windows build additionally runs the unmocked entry point against
all six REAL R9-native-smoked EXEs. Synthetic tests never certify binaries.
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
import sealed_candidate_handoff_r117 as h
import native_sealed_roundtrip_r118 as r


class NativeRoundtripR118Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.work = self.root / "runner-private"
        self.work.mkdir(mode=0o700)
        self.dist = self.root / "dist"
        self.dist.mkdir()
        self.r9 = self.root / "r9.json"
        self.r9.write_bytes(b'{"synthetic":"not native Windows smoke"}')
        for index, name in enumerate(h.NAMES):
            (self.dist / name).write_bytes(b"MZ-SYNTHETIC-NOT-EXE" + bytes([index + 1]) * 97)
        (self.dist / "SHA256SUMS.txt").write_text("FAKE INVENTORY - NOT VERIFIED\n")
        self.custody = mock.patch.object(h, "_custody", return_value=None)
        self.custody.start()
        self.addCleanup(self.custody.stop)

    def _run(self):
        return r.verify_native_roundtrip(self.dist, self.r9, self.work)

    def _no_staging(self):
        self.assertEqual(list(self.work.iterdir()), [], "Temporary key/bundle/plaintext persisted")

    def test_six_synthetic_entry_roundtrip_and_tamper_rejection(self):
        result = self._run()
        self.assertEqual(result["candidate_count"], 6)
        self.assertEqual(result["verified_private_entries"], 8)
        self.assertTrue(result["ciphertext_tamper_rejected"])
        self.assertFalse(result["independent_r9_pin"])
        self.assertFalse(result["release_authorized"])
        self.assertFalse(result["premium_distribution_authorized"])
        self.assertFalse(result["physical_windows11_acceptance"])
        self._no_staging()

    def test_roundtrip_does_not_modify_six_source_inputs(self):
        before = r._snapshot(h._paths(self.dist, self.r9))
        self._run()
        self.assertEqual(r._snapshot(h._paths(self.dist, self.r9)), before)
        self._no_staging()

    def test_failed_r9_custody_does_not_create_key_or_bundle(self):
        with mock.patch.object(h, "_custody", side_effect=h.HandoffHold("fake bad R9")):
            with self.assertRaises(h.HandoffHold):
                self._run()
        self._no_staging()

    def test_missing_candidate_fails_without_sealing(self):
        (self.dist / h.NAMES[0]).unlink()
        with self.assertRaises(OSError):
            self._run()
        self._no_staging()

    def test_wrong_authorization_claim_from_sealer_fails_closed(self):
        real = h.seal

        def bad_seal(*args):
            output = real(*args)
            return {**output, "release_authorized": True}

        with mock.patch.object(h, "seal", side_effect=bad_seal):
            with self.assertRaises(r.RoundtripHold):
                self._run()
        self._no_staging()

    def test_wrong_authorization_claim_from_unsealer_fails_closed(self):
        real = h.unseal

        def bad_unseal(*args):
            output = real(*args)
            return {**output, "release_authorized": True}

        with mock.patch.object(h, "unseal", side_effect=bad_unseal):
            with self.assertRaises(r.RoundtripHold):
                self._run()
        self._no_staging()

    def test_handoff_unseal_exception_cleans_entire_ephemeral_tree(self):
        with mock.patch.object(h, "unseal", side_effect=h.HandoffHold("injected")):
            with self.assertRaises(h.HandoffHold):
                self._run()
        self._no_staging()

    def test_dishonest_authenticator_acceptance_is_detected(self):
        real = h.unseal
        count = 0

        def dishonest(*args):
            nonlocal count
            count += 1
            if count == 2:
                return {"release_authorized": False, "six_exes": 6}
            return real(*args)

        with mock.patch.object(h, "unseal", side_effect=dishonest):
            with self.assertRaises(r.RoundtripHold):
                self._run()
        self.assertEqual(count, 2)
        self._no_staging()

    def test_mutated_source_after_sealing_is_detected(self):
        real = h.seal

        def mutate_after_sealing(*args):
            result = real(*args)
            with (self.dist / h.NAMES[0]).open("ab") as changed:
                changed.write(b"TOCTOU")
            return result

        with mock.patch.object(h, "seal", side_effect=mutate_after_sealing):
            with self.assertRaises(r.RoundtripHold):
                self._run()
        self._no_staging()

    def test_relative_scratch_root_is_rejected(self):
        with self.assertRaises(r.RoundtripHold):
            r.verify_native_roundtrip(self.dist, self.r9, Path("relative"))
        self._no_staging()

    def test_work_root_inside_candidates_is_denied(self):
        with self.assertRaises((r.RoundtripHold, h.HandoffHold)):
            r.verify_native_roundtrip(self.dist, self.r9, self.dist)
        self._no_staging()

    def test_work_root_symlink_is_denied(self):
        link = self.root / "alias"
        try:
            link.symlink_to(self.work, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Creating symlinks unsupported on this host")
        with self.assertRaises(h.HandoffHold):
            r.verify_native_roundtrip(self.dist, self.r9, link)
        self._no_staging()

    def test_cli_failure_redacts_private_paths_and_does_not_claim_pass(self):
        secret = self.root / "private-sensitive-ledger-location"
        captured = io.StringIO()
        with contextlib.redirect_stderr(captured):
            exit_code = r.main([str(secret), str(self.r9), str(self.work)])
        self.assertEqual(exit_code, 1)
        self.assertIn("HOLD", captured.getvalue())
        self.assertNotIn(str(secret), captured.getvalue())
        self._no_staging()

    def test_success_stdout_never_includes_input_paths_or_hashes(self):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            result = r.main([str(self.dist), str(self.r9), str(self.work)])
        self.assertEqual(result, 0)
        self.assertIn("NO release", capture.getvalue())
        self.assertNotIn(str(self.root), capture.getvalue())
        self.assertNotIn(h._hash(self.r9), capture.getvalue())
        self._no_staging()

    def test_modified_real_ciphertext_can_not_publish_plaintext(self):
        # R118 mutates the first actual encrypted candidate byte and calls
        # R117's authenticated unseal. No synthetic bypass is mocked here.
        output = self._run()
        self.assertTrue(output["ciphertext_tamper_rejected"])
        self._no_staging()


if __name__ == "__main__":
    unittest.main()
