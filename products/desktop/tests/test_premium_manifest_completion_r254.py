"""R254: synthetic premium manifest post-publication custody tests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fvs_suite.premium_manifest_completion import verify_premium_inventory

STAMP = "20261107-005400-123456"
PACK = "20261107T085400Z-" + "a" * 32
LAYOUT = {
    "grants": ("grant-evidence-", ("grant-audit-exceptions", "grant-budget-check")),
    "procurement": ("procurement-evidence-", ("procurement-three-way",)),
}
HEADER = "SHA-256 file inventory. Hashes do not certify accuracy or compliance.\n"


class PremiumManifestR254(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def bundle(self, app, *, input_count=3):
        prefix, stems = LAYOUT[app]
        package = self.root / (prefix + PACK)
        package.mkdir()
        files = []
        for stem in stems:
            report = package / f"{stem}-{STAMP}.csv"
            report.write_bytes((stem + "\n").encode())
            files.append(report)
        manifest = package / f"evidence-manifest-{STAMP}.txt"
        sources = [f"source-{i}.csv\t" + "a" * 64 + "\n"
                   for i in range(input_count)]
        outputs = []
        for path in files:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            outputs.append(f"{json.dumps(path.name, ensure_ascii=True)[1:-1]}\t{digest}\n")
        manifest.write_text(HEADER + "".join(sources + outputs), encoding="ascii")
        return tuple(files + [manifest])

    def test_valid_grant(self):
        verify_premium_inventory(self.bundle("grants"), "grants")

    def test_valid_procurement_with_optional_policy(self):
        verify_premium_inventory(self.bundle("procurement", input_count=4),
                                 "procurement")

    def test_valid_procurement_without_policy(self):
        verify_premium_inventory(self.bundle("procurement"), "procurement")

    def test_tampered_report_rejected(self):
        files = self.bundle("grants")
        files[0].write_text("different financial evidence\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify_premium_inventory(files, "grants")

    def test_mixed_report_and_manifest_same_bundle_rejected(self):
        files = self.bundle("procurement")
        files[0].write_text("other batch\n")
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "procurement")

    def test_missing_or_extra_file_rejected(self):
        for extra in (True, False):
            with self.subTest(extra=extra):
                files = self.bundle("grants" if extra else "procurement")
                if extra:
                    (files[0].parent / "unexpected.dat").write_text("x")
                else:
                    files[-1].unlink()
                with self.assertRaises((ValueError, OSError)):
                    verify_premium_inventory(files,
                                             "grants" if extra else "procurement")

    def test_excessive_inventory_rejected(self):
        files = self.bundle("grants")
        files[-1].write_text("Z" * (128 * 1024 + 1))
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "grants")

    def test_bad_header_rejected(self):
        files = self.bundle("grants")
        path = files[-1]
        path.write_text(path.read_text().replace("SHA-256 file inventory",
                                                  "FORGED file inventory"))
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "grants")

    def test_bad_hex_and_count_rejected(self):
        files = self.bundle("grants")
        path = files[-1]
        path.write_text(path.read_text().replace("a" * 64, "g" * 64, 1))
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "grants")
        path.write_text(HEADER + "source-only\t" + "a" * 64 + "\n")
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "grants")

    def test_duplicate_input_labels_rejected(self):
        files = self.bundle("grants")
        path = files[-1]
        path.write_text(path.read_text().replace("source-1.csv", "source-0.csv"))
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            verify_premium_inventory(files, "grants")

    def test_mismatch_wrong_product_rejected(self):
        files = self.bundle("grants")
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "procurement")

    def test_symlink_manifest_rejected(self):
        files = self.bundle("procurement")
        original = files[-1]
        target = self.root / "outside.txt"
        target.write_bytes(original.read_bytes())
        original.unlink()
        try:
            original.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlinks unavailable: {type(exc).__name__}")
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "procurement")

    def test_private_files_not_modified_on_failure(self):
        files = self.bundle("grants")
        before = files[0].read_bytes()
        files[-1].write_text("bad")
        with self.assertRaises(ValueError):
            verify_premium_inventory(files, "grants")
        self.assertEqual(before, files[0].read_bytes())


if __name__ == "__main__":
    unittest.main()
