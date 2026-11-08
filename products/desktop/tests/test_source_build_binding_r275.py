"""R275 synthetic source-to-build custody tests; not native Windows QA."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "source_build_binding_r275.py"
spec = importlib.util.spec_from_file_location("source_build_binding_r275", MODULE)
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)


class TestedSourceBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "products/desktop/fvs_suite/engine.py"
        self.test = self.root / "products/desktop/tests/test_engine.py"
        for path in (self.src, self.test):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"original synthetic data\n")
        self.receipt = {"source_smoke": {"source_inventory": self._sources()},
                        "test_inventory": self._tests()}

    def _entries(self, folder):
        paths = sorted(folder.rglob("*.py"))
        return [{"path": p.relative_to(self.root).as_posix(),
                 "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]

    def _sources(self, root=None):
        return self._entries(self.root / "products/desktop/fvs_suite")

    def _tests(self, root=None):
        return self._entries(self.root / "products/desktop/tests")

    def verify(self):
        binding.verify_source_binding(self.root, self.receipt,
                                      source_inventory_reader=self._sources,
                                      test_inventory_reader=self._tests)

    def rejected(self):
        with self.assertRaises(binding.SourceBindingRejected) as ctx:
            self.verify()
        self.assertEqual(str(ctx.exception), binding.SAFE_ERROR)
        self.assertIsNone(ctx.exception.__cause__)
        self.assertIsNone(ctx.exception.__context__)

    def test_unchanged_checkout_passes(self):
        self.verify()

    def test_source_rewrite_after_tests_rejected(self):
        self.src.write_bytes(b"unreviewed code\n")
        self.rejected()

    def test_test_rewrite_after_tests_rejected(self):
        self.test.write_bytes(b"weakened tests\n")
        self.rejected()

    def test_source_added_after_tests_rejected(self):
        (self.src.parent / "injected.py").write_bytes(b"pass\n")
        self.rejected()

    def test_test_added_after_tests_rejected(self):
        (self.test.parent / "test_new.py").write_bytes(b"pass\n")
        self.rejected()

    def test_source_removed_after_tests_rejected(self):
        self.src.unlink()
        self.rejected()

    def test_test_removed_after_tests_rejected(self):
        self.test.unlink()
        self.rejected()

    def test_mutated_digest_in_receipt_rejected(self):
        self.receipt["test_inventory"][0]["sha256"] = "0" * 64
        self.rejected()

    def test_traversal_receipt_path_rejected(self):
        self.receipt["test_inventory"][0]["path"] = "products/desktop/tests/../fvs_suite/engine.py"
        self.rejected()

    def test_windows_slash_receipt_path_rejected(self):
        self.receipt["test_inventory"][0]["path"] = "products/desktop/tests\\test_engine.py"
        self.rejected()

    def test_unicode_digest_rejected(self):
        self.receipt["test_inventory"][0]["sha256"] = "é" * 64
        self.rejected()

    def test_oversized_inventory_rejected(self):
        self.receipt["test_inventory"] = self.receipt["test_inventory"] * 513
        self.rejected()

    def test_duplicate_inventory_rejected(self):
        self.receipt["test_inventory"] *= 2
        self.rejected()

    def test_unexpected_inventory_field_rejected(self):
        self.receipt["test_inventory"][0]["private"] = "customer.csv"
        self.rejected()

    def test_reader_error_is_path_safe(self):
        def fail(root):
            raise OSError("C:/private/payroll.csv")
        with self.assertRaises(binding.SourceBindingRejected) as ctx:
            binding.verify_source_binding(self.root, self.receipt,
                                          source_inventory_reader=fail,
                                          test_inventory_reader=self._tests)
        self.assertNotIn("payroll", str(ctx.exception))
        self.assertIsNone(ctx.exception.__context__)

    def test_bogus_root_is_path_safe(self):
        with self.assertRaises(binding.SourceBindingRejected) as ctx:
            binding.verify_source_binding(self.root / "not-real", self.receipt,
                                          source_inventory_reader=self._sources,
                                          test_inventory_reader=self._tests)
        self.assertEqual(str(ctx.exception), binding.SAFE_ERROR)

    def test_wrong_type_receipt_rejected(self):
        self.receipt = None
        self.rejected()

    def test_missing_smoke_inventory_rejected(self):
        self.receipt["source_smoke"].pop("source_inventory")
        self.rejected()


if __name__ == "__main__":
    unittest.main()
