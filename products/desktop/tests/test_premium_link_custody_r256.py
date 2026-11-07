"""R256 private premium inventory hardlink and descriptor-custody regressions."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fvs_suite.premium_link_custody import open_inventory_stream, require_single_link


class PremiumLinkHelperR256(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.path = self.root / "private-inventory.txt"
        self.path.write_bytes(b"Synthetic inventory only\n")

    def test_ordinary_file_passes_single_link_check(self):
        require_single_link(self.path.lstat())

    def test_missing_link_count_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            require_single_link(SimpleNamespace(st_nlink=0))

    def test_multiple_link_count_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            require_single_link(SimpleNamespace(st_nlink=2))

    def test_negative_link_count_fails_closed(self):
        with self.assertRaises(ValueError):
            require_single_link(SimpleNamespace(st_nlink=-1))

    def test_link_count_check_never_reads_file(self):
        with patch("builtins.open", side_effect=AssertionError("private read")):
            require_single_link(self.path.lstat())

    def test_stream_returns_original_binary_bytes(self):
        with open_inventory_stream(self.path, os.O_RDONLY) as stream:
            self.assertEqual(stream.read(), b"Synthetic inventory only\n")

    def test_returned_stream_closes_descriptor_on_exit(self):
        with open_inventory_stream(self.path, os.O_RDONLY) as stream:
            fd = stream.fileno()
            self.assertTrue(stat.S_ISREG(os.fstat(fd).st_mode))
        with self.assertRaises(OSError):
            os.fstat(fd)

    def test_body_exception_still_closes_descriptor(self):
        fd = None
        with self.assertRaisesRegex(ValueError, "synthetic"):
            with open_inventory_stream(self.path, os.O_RDONLY) as stream:
                fd = stream.fileno()
                raise ValueError("synthetic")
        with self.assertRaises(OSError):
            os.fstat(fd)

    def assert_adoption_failure_closed(self, failure):
        opened = []
        native_open = os.open
        def traced_open(*args, **kwargs):
            fd = native_open(*args, **kwargs)
            opened.append(fd)
            return fd
        with patch("fvs_suite.premium_link_custody.os.open", side_effect=traced_open):
            with patch("fvs_suite.premium_link_custody.os.fdopen", side_effect=failure):
                with self.assertRaises(type(failure)):
                    open_inventory_stream(self.path, os.O_RDONLY)
        self.assertEqual(len(opened), 1)
        with self.assertRaises(OSError):
            os.fstat(opened[0])

    def test_fdopen_oserror_does_not_leak_fd(self):
        self.assert_adoption_failure_closed(OSError("synthetic private filename"))

    def test_fdopen_runtimeerror_does_not_leak_fd(self):
        self.assert_adoption_failure_closed(RuntimeError("synthetic"))

    def test_fdopen_keyboard_interrupt_does_not_leak_fd(self):
        self.assert_adoption_failure_closed(KeyboardInterrupt())

    def test_failed_os_open_never_calls_fdopen(self):
        with patch("fvs_suite.premium_link_custody.os.open", side_effect=OSError("synthetic")):
            with patch("fvs_suite.premium_link_custody.os.fdopen") as adopt:
                with self.assertRaises(OSError):
                    open_inventory_stream(self.path, os.O_RDONLY)
                adopt.assert_not_called()

    def test_hardlink_rejected_without_touching_original(self):
        other = self.root / "external-alias.txt"
        try:
            os.link(self.path, other)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"hardlinks unsupported: {type(exc).__name__}")
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            require_single_link(self.path.lstat())
        self.assertEqual(self.path.read_bytes(), before)


# These additional integration cases execute against the *actual* GitHub
# premium_manifest_completion module when the full repository is available.
class PremiumLinkIntegrationR256(unittest.TestCase):
    def setUp(self):
        from fvs_suite.premium_manifest_completion import verify_premium_inventory
        self.verify = verify_premium_inventory
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def bundle(self, product="procurement"):
        stamp = "20261107-005400-123456"
        name = "20261107T085400Z-" + "a" * 32
        prefix, stems = (
            ("grant-evidence-", ("grant-audit-exceptions", "grant-budget-check"))
            if product == "grants" else
            ("procurement-evidence-", ("procurement-three-way",))
        )
        directory = self.root / (prefix + name)
        directory.mkdir()
        reports = []
        for stem in stems:
            path = directory / f"{stem}-{stamp}.csv"
            path.write_bytes((stem + "\n").encode())
            reports.append(path)
        manifest = directory / f"evidence-manifest-{stamp}.txt"
        lines = ["SHA-256 file inventory. Hashes do not certify accuracy or compliance.\n"]
        lines += [f"input-{n}.csv\t" + "a" * 64 + "\n" for n in range(3)]
        for path in reports:
            label = json.dumps(path.name, ensure_ascii=True)[1:-1]
            lines.append(f"{label}\t{hashlib.sha256(path.read_bytes()).hexdigest()}\n")
        manifest.write_text("".join(lines), encoding="ascii")
        return tuple(reports + [manifest])

    def test_valid_premium_bundle_still_passes(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                self.verify(self.bundle(product), product)

    def test_external_manifest_hardlink_rejected(self):
        paths = self.bundle()
        try:
            os.link(paths[-1], self.root / "external.txt")
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"hardlinks unsupported: {type(exc).__name__}")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.verify(paths, "procurement")

    def test_external_report_hardlink_rejected(self):
        paths = self.bundle("grants")
        try:
            os.link(paths[0], self.root / "external.csv")
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"hardlinks unsupported: {type(exc).__name__}")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.verify(paths, "grants")

    def test_external_report_alias_added_during_later_hash_rejected(self):
        from fvs_suite import premium_manifest_completion as subject
        paths = self.bundle("grants")
        original = subject._hash_regular
        calls = 0
        def mutate(path, maximum):
            nonlocal calls
            result = original(path, maximum)
            calls += 1
            if calls == 2:
                os.link(paths[0], self.root / "late-external.csv")
            return result
        try:
            with patch.object(subject, "_hash_regular", side_effect=mutate):
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    self.verify(paths, "grants")
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"hardlinks unsupported: {type(exc).__name__}")

    def test_fdopen_failure_yields_safe_inventory_diagnostic(self):
        from fvs_suite.premium_manifest_completion import _read_bounded_inventory
        paths = self.bundle()
        with patch("fvs_suite.premium_link_custody.os.fdopen", side_effect=OSError("/home/customer/private.csv")):
            with self.assertRaises(ValueError) as error:
                _read_bounded_inventory(paths[-1])
        self.assertNotIn("customer", str(error.exception))
        self.assertNotIn("private.csv", str(error.exception))


if __name__ == "__main__":
    unittest.main()
