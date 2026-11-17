"""R493: format and SHA256 must describe the SAME open PE bytes.

Synthetic PE32+ fixtures only. No executable is run or distributed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import release_gate as gate
from build_inventory import EXPECTED, build_inventory
from pe_fixture_r17 import synthetic_pe64
from pe_image_guard import PEFormatError, verify_amd64_pe


class BoundPEIntegrationR493(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r493-pe-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.image = self.root / EXPECTED[0]
        self.original = synthetic_pe64()
        self.image.write_bytes(self.original)
        self.sha = hashlib.sha256(self.original).hexdigest()

    def test_matching_pe_sha_on_same_descriptor_passes(self):
        verify_amd64_pe(self.image, expected_sha256=self.sha)

    def test_wrong_sha_rejects_even_structurally_valid_pe(self):
        with self.assertRaises(PEFormatError):
            verify_amd64_pe(self.image, expected_sha256="0" * 64)

    def test_altered_overlay_rejected_against_original_sha(self):
        self.image.write_bytes(self.original[:-1] + bytes([self.original[-1] ^ 1]))
        with self.assertRaises(PEFormatError):
            verify_amd64_pe(self.image, expected_sha256=self.sha)

    def test_altered_overlay_accepted_only_with_new_sha(self):
        changed = self.original + b"INERT OVERLAY"
        self.image.write_bytes(changed)
        verify_amd64_pe(self.image, expected_sha256=hashlib.sha256(changed).hexdigest())

    def test_bad_pe_rejected_even_when_sha_matches(self):
        broken = b"not a Windows executable" * 40
        self.image.write_bytes(broken)
        with self.assertRaises(PEFormatError):
            verify_amd64_pe(self.image, expected_sha256=hashlib.sha256(broken).hexdigest())

    def test_gate_pe_wrapper_requires_matching_digest(self):
        gate._pe64(self.image, expected_sha256=self.sha)
        with self.assertRaises(gate.GateFailure):
            gate._pe64(self.image, expected_sha256="0" * 64)

    def fill_bundle(self):
        for name in EXPECTED:
            (self.root / name).write_bytes(self.original)
        self.assertEqual(build_inventory(self.root), "SHA256SUMS.txt")

    def test_full_six_candidate_static_gate_still_rejects_release(self):
        self.fill_bundle()
        receipt = gate.verify(self.root, smoke=False)
        self.assertEqual(len(receipt["artifacts"]), 6)
        self.assertFalse(receipt["release_authorized"])
        self.assertFalse(receipt["windows_executables_verified"])
        self.assertTrue(all(row["sha256"] == self.sha for row in receipt["artifacts"]))

    def test_six_candidate_gate_rejects_stale_hash_even_if_independent_sha_is_forged(self):
        self.fill_bundle()
        target = self.root / EXPECTED[-1]
        target.write_bytes(self.original[:-1] + bytes([self.original[-1] ^ 1]))
        real_sha = gate._sha

        def stale_digest(path):
            if Path(path) == target:
                return self.sha
            return real_sha(path)

        with patch.object(gate, "_sha", side_effect=stale_digest):
            with self.assertRaises(gate.GateFailure):
                gate.verify(self.root, smoke=False)


if __name__ == "__main__":
    unittest.main()
