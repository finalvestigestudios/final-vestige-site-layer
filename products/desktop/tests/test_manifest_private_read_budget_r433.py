"""R433: bounded inventory descriptor reads must not reveal private paths in chains.

Synthetic local test files; no network, entitlements, customer data, or release artifacts.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import manifest_guard as guard


class PrivateInventoryReadBudgetR433(unittest.TestCase):
    def setUp(self):
        private = tempfile.TemporaryDirectory(prefix="fvs-r433-")
        self.addCleanup(private.cleanup)
        self.root = Path(private.name)
        self.source = self.root / "PRIVATE_LEDGER_TOKEN.csv"
        self.source.write_bytes(b"invoice,amount\nA,12.30\n")
        self.report = self.root / "review.csv"
        self.report.write_bytes(b"invoice,status\nA,requires_human_review\n")

    def assert_private_failure(self, invoke, expected_type, message):
        with self.assertRaises(expected_type) as caught:
            invoke()
        raised = caught.exception
        self.assertEqual(str(raised), message)
        self.assertIsNone(raised.__cause__)
        self.assertIsNone(raised.__context__)
        self.assertNotIn("PRIVATE_LEDGER_TOKEN", str(raised))

    def test_missing_private_source_does_not_leave_filename_in_hidden_chain(self):
        missing = self.root / "PRIVATE_LEDGER_TOKEN_MISSING.csv"
        self.assert_private_failure(lambda: guard._metadata(missing), FileNotFoundError,
                                    "Inventory evidence file is missing")

    def test_metadata_oserror_does_not_leave_secret_in_hidden_chain(self):
        with patch.object(Path, "lstat", side_effect=PermissionError("PRIVATE_LEDGER_TOKEN")):
            self.assert_private_failure(lambda: guard._metadata(self.source), ValueError,
                                        "Cannot inspect inventory evidence file")

    def test_open_missing_does_not_leave_secret_in_hidden_chain(self):
        with patch.object(guard, "open_inventory_stream",
                          side_effect=FileNotFoundError("PRIVATE_LEDGER_TOKEN")):
            self.assert_private_failure(
                lambda: guard._hash_regular(self.source, guard.MAX_INPUT_BYTES),
                FileNotFoundError, "Inventory evidence file is missing")

    def test_open_oserror_does_not_leave_secret_in_hidden_chain(self):
        with patch.object(guard, "open_inventory_stream",
                          side_effect=PermissionError("PRIVATE_LEDGER_TOKEN")):
            self.assert_private_failure(
                lambda: guard._hash_regular(self.source, guard.MAX_INPUT_BYTES),
                ValueError, "Cannot safely open inventory evidence")

    def test_read_oserror_does_not_leave_secret_in_hidden_chain(self):
        class FailedRead:
            def __init__(self, handle): self.handle = handle
            def __enter__(self): return self
            def __exit__(self, *unused): self.handle.close()
            def fileno(self): return self.handle.fileno()
            def read(self, unused): raise OSError("PRIVATE_LEDGER_TOKEN")

        def failed_stream(path, unused_flags):
            return FailedRead(path.open("rb"))

        with patch.object(guard, "open_inventory_stream", side_effect=failed_stream):
            self.assert_private_failure(
                lambda: guard._hash_regular(self.source, guard.MAX_INPUT_BYTES),
                ValueError, "Unable to read inventory evidence")

    def test_bad_maximum_types_are_rejected_before_any_path_access(self):
        class IntSubclass(int):
            pass
        for maximum in (None, True, 1.0, float("inf"), float("nan"),
                        IntSubclass(8), -1, guard.MAX_REPORT_BYTES + 1, "50"):
            with self.subTest(type=type(maximum).__name__, value=repr(maximum)):
                with patch.object(guard, "_metadata", side_effect=AssertionError("PATH_TOUCHED")) as meta:
                    self.assert_private_failure(
                        lambda: guard._hash_regular(self.source, maximum), ValueError,
                        "Invalid inventory size limit")
                    meta.assert_not_called()

    def test_empty_file_with_zero_maximum_is_valid(self):
        empty = self.root / "empty.csv"
        empty.write_bytes(b"")
        digest, signature = guard._hash_regular(empty, 0)
        self.assertEqual(digest, hashlib.sha256(b"").hexdigest())
        self.assertEqual(signature[2], 0)

    def test_positive_limit_below_file_size_remains_rejected(self):
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            guard._hash_regular(self.source, len(self.source.read_bytes()) - 1)

    def test_normal_digest_is_exact_and_source_is_unchanged(self):
        before = self.source.read_bytes()
        digest, signature = guard._hash_regular(self.source, guard.MAX_INPUT_BYTES)
        self.assertEqual(digest, hashlib.sha256(before).hexdigest())
        self.assertEqual(signature[2], len(before))
        self.assertEqual(before, self.source.read_bytes())

    def test_inventory_source_report_and_pinned_digest_unchanged(self):
        digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        report_digest = hashlib.sha256(self.report.read_bytes()).hexdigest()
        body = guard.inventory_text([self.source], [self.report],
                                    expected_input_digests={self.source: digest})
        self.assertEqual(body.splitlines()[1], f"{self.source.name}\t{digest}")
        self.assertEqual(body.splitlines()[2], f"{self.report.name}\t{report_digest}")


if __name__ == "__main__":
    unittest.main()
