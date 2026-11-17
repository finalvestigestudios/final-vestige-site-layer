"""R496 full parser and six-candidate certificate-framing integration.

PE fixtures are inert and never executed. Structural acceptance is not trust.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import struct
import tempfile
import unittest

from build_inventory import EXPECTED, build_inventory
from pe_fixture_r17 import synthetic_pe64
from pe_image_guard import PEFormatError, verify_amd64_pe
import release_gate


OPTIONAL_START = 128 + 24
DIRECTORIES_START = OPTIONAL_START + 112


def certificate(payload=b"not-a-real-signature", *, revision=0x0200,
                cert_type=2, claimed_length=None) -> bytes:
    length = len(payload) + 8 if claimed_length is None else claimed_length
    raw = struct.pack("<IHH", length, revision, cert_type) + payload
    return raw + b"\0" * (-len(raw) % 8)


def candidate(table: bytes | None) -> bytes:
    raw = bytearray(synthetic_pe64())
    if table is not None:
        struct.pack_into("<I", raw, OPTIONAL_START + 108, 5)
        struct.pack_into("<II", raw, DIRECTORIES_START + 8 * 4,
                         len(raw), len(table))
        raw.extend(table)
    return bytes(raw)


class PECertificateIntegrationR496(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r496-int-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.exe = self.root / EXPECTED[0]

    def inspect(self, raw: bytes) -> None:
        self.exe.write_bytes(raw)
        verify_amd64_pe(self.exe,
                        expected_sha256=hashlib.sha256(raw).hexdigest())

    def test_unsigned_candidate_passes(self):
        self.inspect(candidate(None))

    def test_framed_certificate_passes_structural_preflight(self):
        self.inspect(candidate(certificate()))

    def test_two_certificate_records_pass(self):
        self.inspect(candidate(certificate(b"X") + certificate(b"Y")))

    def test_arbitrary_overlay_rejected(self):
        with self.assertRaisesRegex(PEFormatError, "PE certificate table rejected"):
            self.inspect(candidate(b"Z" * 64))

    def test_obsolete_revision_rejected(self):
        with self.assertRaises(PEFormatError):
            self.inspect(candidate(certificate(revision=0x0100)))

    def test_unexpected_certificate_type_rejected(self):
        with self.assertRaises(PEFormatError):
            self.inspect(candidate(certificate(cert_type=1)))

    def test_record_claiming_bytes_beyond_table_rejected(self):
        with self.assertRaises(PEFormatError):
            self.inspect(candidate(certificate(claimed_length=1000)))

    def test_incomplete_trailing_certificate_rejected(self):
        with self.assertRaises(PEFormatError):
            self.inspect(candidate(certificate() + b"\0" * 8))

    def test_six_candidate_gate_rejects_invalid_certificate(self):
        for name in EXPECTED:
            (self.root / name).write_bytes(candidate(None))
        (self.root / EXPECTED[-1]).write_bytes(candidate(b"Z" * 64))
        self.assertEqual(build_inventory(self.root), "SHA256SUMS.txt")
        with self.assertRaises(release_gate.GateFailure):
            release_gate.verify(self.root, smoke=False)


if __name__ == "__main__":
    unittest.main()
