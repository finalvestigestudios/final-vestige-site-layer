"""R190 full six-product Gutenberg static source integration (never publish)."""
from __future__ import annotations

from pathlib import Path
import unittest

import catalog_preflight_r186 as gate


SOURCE = Path(__file__).resolve().parents[1] / "site" / "software-catalog.gutenberg.html"
INSERT_BEFORE = '<h2 class="wp-block-heading">Pilot with us</h2>'


class CatalogCompatibilityIntegrationR190(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_bytes()
        cls.html = cls.source.decode("utf-8", "strict")
        if cls.html.count(INSERT_BEFORE) != 1:
            raise RuntimeError("tracked catalog pilot heading changed")

    def inserted(self, text: str) -> bytes:
        return self.html.replace(INSERT_BEFORE, text + INSERT_BEFORE, 1).encode("utf-8")

    def blocked(self, text: str) -> None:
        with self.assertRaises(gate.CatalogPreflightError) as cm:
            gate.verify_catalog(self.inserted(text))
        self.assertNotIn("SECRET", str(cm.exception))
        self.assertNotIn("customer", str(cm.exception))

    def test_original_static_six_product_catalog_still_passes_without_approval(self):
        report = gate.verify_catalog(self.source)
        self.assertEqual((report["apps"], report["free"], report["premium"]), (6, 4, 2))
        self.assertFalse(report["qd_approved"])
        self.assertFalse(report["site_publication_authorized"])
        self.assertFalse(report["premium_access_verified"])

    def test_synthetic_fullwidth_false_download_claim_rejected(self):
        self.blocked("<p>Ｄｏｗｎｌｏａｄ ｎｏｗ</p>")

    def test_synthetic_fullwidth_dot_and_private_file_rejected(self):
        self.blocked("<p>customer SECRET GrantAudit．ｍｓｉ</p>")

    def test_synthetic_fullwidth_http_destination_rejected(self):
        self.blocked("<p>customer SECRET ｈｔｔｐｓ：//example.test/private</p>")

    def test_synthetic_circled_download_rejected(self):
        self.blocked("<p>Ⓓⓞⓦⓝⓛⓞⓐⓓ ⓝⓞⓦ</p>")

    def test_synthetic_compatibility_release_word_rejected(self):
        self.blocked("<p>Ｒｅｌｅａｓｅｄ</p>")

    def test_synthetic_nested_inline_node_bypass_rejected(self):
        self.blocked("<p>Ｄｏｗ<strong>ｎｌｏａｄ </strong><strong>ｎｏｗ</strong></p>")

    def test_synthetic_numeric_html_entities_rejected(self):
        self.blocked("<p>&#x24B9;&#x24DE;&#x24E6;&#x24DD;&#x24DB;&#x24DE;&#x24D0;&#x24D3; now</p>")

    def test_synthetic_nonbreaking_space_rejected(self):
        self.blocked("<p>Buy&#xa0;now</p>")

    def test_benign_compatibility_copy_permitted(self):
        report = gate.verify_catalog(self.inserted("<p>Ｐｒｉｖａｔｅ pilot inquiry only.</p>"))
        self.assertEqual(report["result"], "PASS_STATIC_DRAFT_ONLY")
        self.assertFalse(report["downloads_verified"])

    def test_input_static_file_not_modified(self):
        gate.verify_catalog(self.source)
        self.assertEqual(SOURCE.read_bytes(), self.source)


if __name__ == "__main__":
    unittest.main()
