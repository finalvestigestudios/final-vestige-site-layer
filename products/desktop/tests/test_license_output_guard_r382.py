"""R382: offline, synthetic signing-output custody; no real credentials or site writes."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import license_output_guard as guard

CANARY = '/private/operator/customer-secret/issuer.sqlite3'


class OutputError(ValueError):
    pass


class LicenseOutputGuardR382Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r382-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.path = self.root / "test.fvslicense"
        self.data = b'{"signed":"synthetic-test-only"}\n'

    def create(self, data=None):
        return guard.create_issued_license(self.path, self.data if data is None else data, OutputError)

    def denied(self, fragment, data=None):
        with self.assertRaises(OutputError) as ctx:
            self.create(data)
        err = ctx.exception
        self.assertIn(fragment, str(err))
        self.assertIsNone(err.__cause__)
        self.assertIsNone(err.__context__)
        self.assertNotIn(CANARY, str(err))
        return err

    def test_exact_output_is_new_private_and_not_replaced(self):
        self.create()
        self.assertEqual(self.path.read_bytes(), self.data)
        if os.name == "posix":
            self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.denied("already exists")
        self.assertEqual(self.path.read_bytes(), self.data)

    def test_existing_output_never_overwritten(self):
        self.path.write_bytes(b"customer-preexisting-data")
        self.denied("already exists")
        self.assertEqual(self.path.read_bytes(), b"customer-preexisting-data")

    def test_existing_symlink_never_followed_or_unlinked(self):
        real = self.root / "private-original"
        real.write_bytes(b"keep")
        try:
            self.path.symlink_to(real)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unsupported")
        self.denied("already exists")
        self.assertEqual(real.read_bytes(), b"keep")
        self.assertTrue(self.path.is_symlink())

    def test_existing_directory_never_replaced(self):
        self.path.mkdir()
        self.denied("already exists")
        self.assertTrue(self.path.is_dir())

    def test_unwritable_parent_does_not_create_file(self):
        self.path = self.root / "nonexistent" / "new.fvslicense"
        self.denied("Cannot create")
        self.assertFalse(self.path.exists())

    def test_rejects_non_bytes_and_empty_and_oversize_preopen(self):
        for value in ("string", bytearray(b"a"), b"", b"x" * 8193):
            with self.subTest(value_type=type(value).__name__):
                self.denied("bounded bytes", value)
                self.assertFalse(self.path.exists())

    def test_exact_maximum_size_is_accepted(self):
        value = b"x" * 8192
        self.create(value)
        self.assertEqual(self.path.read_bytes(), value)

    def test_partial_writes_complete_without_duplicate_or_gap(self):
        actual = guard.os.write
        calls = []
        def short(fd, contents):
            calls.append(len(contents))
            return actual(fd, contents[:min(3, len(contents))])
        with patch.object(guard.os, "write", side_effect=short):
            self.create()
        self.assertGreater(len(calls), 2)
        self.assertEqual(self.path.read_bytes(), self.data)

    def test_zero_progress_does_not_loop_or_delete_uncertain_file(self):
        with patch.object(guard.os, "write", return_value=0) as writer:
            self.denied("Cannot finish")
        writer.assert_called_once()
        self.assertTrue(self.path.exists())
        self.assertEqual(self.path.read_bytes(), b"")

    def test_invalid_write_count_does_not_mark_issued(self):
        with patch.object(guard.os, "write", return_value=len(self.data) + 1):
            self.denied("Cannot finish")
        self.assertTrue(self.path.exists())

    def test_write_fault_redacts_private_path_and_leaves_partial_file(self):
        real_write = guard.os.write
        calls = 0
        def faulty(fd, value):
            nonlocal calls
            calls += 1
            if calls == 1:
                return real_write(fd, value[:4])
            raise OSError(CANARY)
        with patch.object(guard.os, "write", side_effect=faulty):
            self.denied("Cannot complete")
        self.assertEqual(self.path.read_bytes(), self.data[:4])

    def test_open_fault_redacts_private_path(self):
        with patch.object(guard.os, "open", side_effect=PermissionError(CANARY)):
            self.denied("Cannot create")

    def test_fstat_fault_closes_created_descriptor(self):
        real_open = guard.os.open
        owned = []
        def tracked(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            owned.append(fd)
            return fd
        with patch.object(guard.os, "open", side_effect=tracked), \
             patch.object(guard.os, "fstat", side_effect=OSError(CANARY)):
            self.denied("Cannot complete")
        self.assertEqual(len(owned), 1)
        with self.assertRaises(OSError):
            os.fstat(owned[0])

    def test_fsync_error_is_private_and_file_not_deleted(self):
        with patch.object(guard.os, "fsync", side_effect=OSError(CANARY)):
            self.denied("Cannot complete")
        self.assertEqual(self.path.read_bytes(), self.data)

    def test_fsync_once_per_successful_issue(self):
        original = guard.os.fsync
        calls = []
        def tracked(fd):
            calls.append(fd)
            return original(fd)
        with patch.object(guard.os, "fsync", side_effect=tracked):
            self.create()
        self.assertEqual(len(calls), 1)

    def test_postwrite_path_replacement_detected(self):
        if os.name == "nt":
            orig_lstat = guard.os.lstat
            def fake(path):
                original = orig_lstat(path)
                values = {name: getattr(original, name) for name in guard._ID_FIELDS}
                values["st_ino"] += 1
                return SimpleNamespace(**values)
            with patch.object(guard.os, "lstat", side_effect=fake):
                self.denied("identity")
        else:
            orig_lstat = guard.os.lstat
            replacement = self.root / "second"
            replacement.write_bytes(self.data)
            called = False
            def swap(path):
                nonlocal called
                if not called:
                    called = True
                    self.path.unlink()
                    replacement.rename(self.path)
                return orig_lstat(path)
            with patch.object(guard.os, "lstat", side_effect=swap):
                self.denied("identity")
            self.assertEqual(self.path.read_bytes(), self.data)

    def test_short_custody_length_detected(self):
        original = guard.os.fstat
        calls = 0
        def shrink(fd):
            nonlocal calls
            calls += 1
            v = original(fd)
            if calls == 2:
                fields = {name: getattr(v, name) for name in guard._ID_FIELDS}
                fields["st_uid"] = getattr(v, "st_uid", 0)
                fields["st_size"] -= 1
                return SimpleNamespace(**fields)
            return v
        with patch.object(guard.os, "fstat", side_effect=shrink):
            self.denied("length")

    def test_reparse_metadata_is_not_accepted(self):
        original = guard.os.fstat
        def reparse(fd):
            v = original(fd)
            fields = {name: getattr(v, name) for name in guard._ID_FIELDS}
            fields["st_file_attributes"] = 0x400
            return SimpleNamespace(**fields)
        with patch.object(guard.os, "fstat", side_effect=reparse):
            self.denied("not a new private")

    def test_close_error_is_private_and_does_not_count_as_success(self):
        real_close = guard.os.close
        def faulty(fd):
            real_close(fd)
            raise OSError(CANARY)
        with patch.object(guard.os, "close", side_effect=faulty):
            self.denied("Cannot close")
        self.assertEqual(self.path.read_bytes(), self.data)

    def test_real_ed25519_signed_synthetic_documents_for_both_premium_products(self):
        import base64
        import hashlib
        import json
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key = Ed25519PrivateKey.generate()
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                path = self.root / (product + ".fvslicense")
                payload = {"product": product, "license_id": "synthetic-r382-only"}
                canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
                payload["signature"] = base64.urlsafe_b64encode(key.sign(canonical)).decode()
                signed = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
                guard.create_issued_license(path, signed, OutputError)
                self.assertEqual(hashlib.sha256(path.read_bytes()).digest(), hashlib.sha256(signed).digest())
                actual = json.loads(path.read_bytes())
                signature = base64.urlsafe_b64decode(actual.pop("signature"))
                from_disk = json.dumps(actual, sort_keys=True, separators=(",", ":")).encode()
                key.public_key().verify(signature, from_disk)
                self.assertEqual(actual["product"], product)

    def test_tamper_after_signing_cannot_verify_against_signed_data(self):
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        key = Ed25519PrivateKey.generate()
        original = b"grant-budget|100.00|manual-review"
        signed = key.sign(original)
        self.create(original)
        key.public_key().verify(signed, self.path.read_bytes())
        self.path.write_bytes(b"grant-budget|900.00|manual-review")
        with self.assertRaises(InvalidSignature):
            key.public_key().verify(signed, self.path.read_bytes())

    def test_no_stdout_or_stderr_or_network_side_effect(self):
        import contextlib, io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.create()
        self.assertEqual((out.getvalue(), err.getvalue()), ("", ""))


if __name__ == "__main__":
    unittest.main()
