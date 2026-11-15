"""R446: canonical and printable financial evidence inventories (synthetic only)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite.evidence_label import canonical_evidence_label
from fvs_suite.manifest_guard import inventory_text
from fvs_suite.premium_manifest_completion import verify_premium_inventory


class EvidenceLabelR446(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def bundle(self, product="grants", input_count=3, *, international=False):
        source = self.root / "sources"
        source.mkdir(exist_ok=True)
        package = self.root / product
        package.mkdir(exist_ok=True)
        source_names = [f"input-{i}.csv" for i in range(input_count)]
        if international:
            source_names[0] = "Café 東京.csv"
        inputs = []
        for name in source_names:
            path = source / name
            path.write_bytes(b"synthetic,12.00\n")
            inputs.append(path)
        stems = ("grant-audit-exceptions", "grant-budget-check") if product == "grants" else ("procurement-three-way",)
        outputs = []
        for stem in stems:
            path = package / (stem + ".csv")
            path.write_bytes(b"review-needed,1\n")
            outputs.append(path)
        manifest = package / "evidence-manifest.txt"
        manifest.write_text(inventory_text(inputs, outputs), encoding="ascii")
        return tuple(outputs + [manifest]), tuple(inputs)

    def test_canonical_visible_ascii_and_international_labels(self):
        for name in ("source-0.csv", "grant report.csv", "Café 東京.csv", "Ångström-∆.csv"):
            with self.subTest(name=name):
                self.assertEqual(json.loads('"' + canonical_evidence_label(name) + '"'), name)
                self.assertEqual(canonical_evidence_label(name), json.dumps(name, ensure_ascii=True)[1:-1])

    def test_reject_non_string_empty_dot_and_path_labels(self):
        for name in (None, 1, True, "", ".", "..", "a/b.csv", r"a\b.csv"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                    canonical_evidence_label(name)

    def test_reject_ascii_control_labels(self):
        for token in ("\0", "\t", "\n", "\r", "\x1b", "\x7f"):
            with self.subTest(token=repr(token)):
                with self.assertRaises(ValueError):
                    canonical_evidence_label("source" + token + ".csv")

    def test_reject_unicode_format_surrogate_separator_and_noncharacters(self):
        for codepoint in (0x200B, 0x200D, 0x202E, 0x2066, 0x2069, 0x00A0,
                          0x2028, 0x2029, 0xD800, 0xFDD0, 0xFFFE, 0xFFFF,
                          0x1FFFE, 0x10FFFF):
            with self.subTest(codepoint=f"U+{codepoint:04X}"):
                with self.assertRaises(ValueError):
                    canonical_evidence_label("input" + chr(codepoint) + ".csv")

    def test_valid_both_premium_inventory_packages_and_international_input(self):
        for product, input_count in (("grants", 3), ("procurement", 3), ("procurement", 4)):
            with self.subTest(product=product, input_count=input_count):
                paths, _ = self.bundle(product, input_count, international=True)
                verify_premium_inventory(paths, product)
                self.assertIn(r"\u", paths[-1].read_text(encoding="ascii"))
                for file in paths:
                    file.unlink()
                paths[0].parent.rmdir()

    def test_noncanonical_json_source_alias_refused(self):
        paths, _ = self.bundle()
        manifest = paths[-1]
        manifest.write_text(manifest.read_text(encoding="ascii").replace("input-0.csv", r"\u0069nput-0.csv", 1), encoding="ascii")
        with self.assertRaisesRegex(ValueError, "Noncanonical premium evidence label"):
            verify_premium_inventory(paths, "grants")

    def test_noncanonical_json_report_alias_refused(self):
        paths, _ = self.bundle("procurement")
        manifest = paths[-1]
        manifest.write_text(manifest.read_text(encoding="ascii").replace("procurement-three-way", r"\u0070rocurement-three-way", 1), encoding="ascii")
        with self.assertRaisesRegex(ValueError, "Noncanonical premium evidence label"):
            verify_premium_inventory(paths, "procurement")

    def test_escaped_control_and_bidi_input_labels_refused(self):
        for label in (r"input\t-0.csv", r"input\u202e-0.csv", r"input\u200b-0.csv",
                      r"input\ud800-0.csv", r"input\ufffe-0.csv"):
            with self.subTest(label=label):
                paths, _ = self.bundle("grants")
                path = paths[-1]
                path.write_text(path.read_text(encoding="ascii").replace("input-0.csv", label, 1), encoding="ascii")
                with self.assertRaisesRegex(ValueError, "Invalid premium evidence label"):
                    verify_premium_inventory(paths, "grants")
                for file in paths:
                    file.unlink()
                paths[0].parent.rmdir()

    def test_ordinary_report_tampering_still_rejected(self):
        paths, _ = self.bundle()
        paths[0].write_bytes(b"altered,20.00\n")
        with self.assertRaisesRegex(ValueError, "does not match"):
            verify_premium_inventory(paths, "grants")

    def test_builder_rejects_invisible_source_label_before_hash_io(self):
        source = self.root / "hidden\u202e.csv"
        output = self.root / "normal.csv"
        with patch("fvs_suite.manifest_guard._hash_regular") as hashing:
            with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
                inventory_text([source], [output])
            hashing.assert_not_called()

    def test_builder_rejects_invisible_report_label_before_hash_io(self):
        source = self.root / "source.csv"
        output = self.root / "report\u200b.csv"
        with patch("fvs_suite.manifest_guard._hash_regular") as hashing:
            with self.assertRaises(ValueError):
                inventory_text([source], [output])
            hashing.assert_not_called()

    def test_builder_rejects_surrogate_source_label_before_hash_io(self):
        source = self.root / "source\ud800.csv"
        output = self.root / "report.csv"
        with patch("fvs_suite.manifest_guard._hash_regular") as hashing:
            with self.assertRaises(ValueError):
                inventory_text([source], [output])
            hashing.assert_not_called()

    def test_tampered_inventory_does_not_modify_report_bytes(self):
        paths, _ = self.bundle("grants")
        original_reports = tuple(path.read_bytes() for path in paths[:-1])
        manifest = paths[-1]
        manifest.write_text(manifest.read_text(encoding="ascii").replace("input-0.csv", r"\u0069nput-0.csv", 1), encoding="ascii")
        with self.assertRaises(ValueError):
            verify_premium_inventory(paths, "grants")
        self.assertEqual(original_reports, tuple(path.read_bytes() for path in paths[:-1]))


if __name__ == "__main__":
    unittest.main()
