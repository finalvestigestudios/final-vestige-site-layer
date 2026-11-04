"""R188: actual six-product HTMLParser/catalog integration, not synthetic-only."""
from __future__ import annotations

from pathlib import Path
import unittest

import catalog_preflight_r186 as gate
from test_catalog_preflight_r186 import catalog


class CatalogVisibleIntegrationR188(unittest.TestCase):
    def insert(self, markup: str) -> bytes:
        original = catalog()
        marker = '<h2>Pilot with us</h2>'
        self.assertIn(marker, original)
        return original.replace(marker, markup + marker, 1).encode("utf-8")

    def rejected(self, markup: str) -> None:
        with self.assertRaises(gate.CatalogPreflightError):
            gate.verify_catalog(self.insert(markup))

    def test_existing_six_card_fixture_passes(self):
        self.assertEqual(gate.verify_catalog(catalog().encode())["apps"], 6)

    def test_plaintext_premium_link_rejected(self):
        self.rejected('<p>https://example.test/GrantAuditStudioPro.exe</p>')

    def test_split_url_across_inline_elements_rejected(self):
        self.rejected('<p>h<strong>tt</strong>ps://example.test/SECRET</p>')

    def test_entity_obfuscated_url_decoded_and_rejected(self):
        self.rejected('<p>&#x68;ttps://example.test/SECRET</p>')

    def test_unlinked_relative_premium_installer_rejected(self):
        self.rejected('<p>/private/ProcureGuardStudioPro.msix</p>')

    def test_available_now_claim_rejected_even_with_correct_statuses(self):
        self.rejected('<p>GrantAudit Studio Pro is AVAILABLE NOW.</p>')

    def test_download_now_claim_split_over_inline_tags_rejected(self):
        self.rejected('<p>Download <strong>now</strong></p>')

    def test_format_character_disguising_link_rejected(self):
        self.rejected('<p>http\u200bs://example.test/SECRET</p>')

    def test_inline_prose_without_links_remains_allowed(self):
        raw = self.insert('<p>Operators may request a confidential pilot discussion.</p>')
        self.assertEqual(gate.verify_catalog(raw)["premium"], 2)

    def test_original_unpublished_site_draft_when_checkout_present(self):
        source = Path(__file__).resolve().parents[1] / "site" / "software-catalog.gutenberg.html"
        if source.exists():
            self.assertEqual(gate.verify_catalog(source.read_bytes())["result"], "PASS_STATIC_DRAFT_ONLY")


if __name__ == '__main__':
    unittest.main()
