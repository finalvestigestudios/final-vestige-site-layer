"""R493 exact-stream SHA256 custody with inert synthetic bytes only."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import tempfile
import unittest

from pe_digest_custody_r493 import PEDigestCustodyError, verify_pe_digest_stream


class PEDigestCustodyR493(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r493-")
        self.addCleanup(temp.cleanup)
        self.image = Path(temp.name) / "LedgerDiffLite.exe"
        self.data = b"MZ-inert-synthetic-only-" * 32
        self.image.write_bytes(self.data)
        self.digest = hashlib.sha256(self.data).hexdigest()

    def check(self, digest=None, *, maximum=4096, path=None):
        with (path or self.image).open("rb") as stream:
            verify_pe_digest_stream(stream, os.fstat(stream.fileno()),
                                    self.digest if digest is None else digest,
                                    maximum=maximum)

    def test_exact_bytes_on_same_descriptor_pass(self):
        self.check()

    def test_changed_expected_digest_rejected(self):
        with self.assertRaises(PEDigestCustodyError):
            self.check("0" * 64)

    def test_altered_file_bytes_rejected_even_with_same_size(self):
        self.image.write_bytes(b"X" + self.data[1:])
        with self.assertRaises(PEDigestCustodyError):
            self.check()

    def test_extra_overlay_changes_digest(self):
        self.image.write_bytes(self.data + b"extra-attachment")
        with self.assertRaises(PEDigestCustodyError):
            self.check()

    def test_rejects_wrong_hash_syntax(self):
        for bad in ("", "A" * 64, "0" * 63, "0" * 65, "0" * 64 + "\n"):
            with self.subTest(bad=bad[:8]):
                with self.assertRaises(PEDigestCustodyError):
                    self.check(bad)

    def test_rejects_hostile_hash_subclass_without_calls(self):
        class Hostile(str):
            def __str__(self):
                raise RuntimeError("client-file-secret")
        with self.assertRaises(PEDigestCustodyError):
            self.check(Hostile(self.digest))

    def test_rejects_invalid_bounds(self):
        for bad in (0, -1, 512 * 1024 * 1024 + 1, True, 4.0):
            with self.subTest(bound=bad):
                with self.assertRaises(PEDigestCustodyError):
                    self.check(maximum=bad)

    def test_rejects_oversize_stream(self):
        with self.assertRaises(PEDigestCustodyError):
            self.check(maximum=len(self.data) - 1)

    def test_rejects_stale_opened_descriptor(self):
        with self.image.open("rb") as stream:
            old = os.fstat(stream.fileno())
            self.image.write_bytes(self.data + b"next")
            with self.assertRaises(PEDigestCustodyError):
                verify_pe_digest_stream(stream, old, self.digest, maximum=4096)

    def test_rejects_wrong_descriptor_identity(self):
        other = self.image.parent / "another.exe"
        other.write_bytes(self.data)
        with self.image.open("rb") as a, other.open("rb") as b:
            with self.assertRaises(PEDigestCustodyError):
                verify_pe_digest_stream(a, os.fstat(b.fileno()), self.digest, maximum=4096)

    def test_rejects_empty_file(self):
        self.image.write_bytes(b"")
        with self.assertRaises(PEDigestCustodyError):
            self.check(hashlib.sha256(b"").hexdigest())

    def test_redacts_untrusted_io_exceptions_without_chain(self):
        class Broken:
            def fileno(self):
                raise OSError("/private/grants/secret.csv")
        with self.assertRaises(PEDigestCustodyError) as caught:
            verify_pe_digest_stream(Broken(), os.stat(self.image), self.digest)
        self.assertEqual(str(caught.exception), "PE digest custody unavailable")
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)


if __name__ == "__main__":
    unittest.main()
