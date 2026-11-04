"""R189 genuine six-card catalog preflight integration cases.

These run on the repository fixture and static tracked draft, not an isolated
HTMLParser shim. They do not confer QD or publication approval.
"""
from __future__ import annotations

import unittest

import catalog_preflight_r186 as gate
from test_catalog_preflight_r186 import catalog


class CatalogFragmentIntegrationR189(unittest.TestCase):
    def inserted(self, text: str) -> bytes:
        original = catalog()
        target = "<h2>Pilot with us</h2>"
        if original.count(target) != 1:
            self.fail("fixture lost its unique pilot heading")
        return original.replace(target, text + target, 1).encode("utf-8")

    def blocked(self, text: str) -> None:
        with self.assertRaises(gate.CatalogPreflightError) as cm:
            gate.verify_catalog(self.inserted(text))
        self.assertNotIn("SECRET", str(cm.exception))

    def test_fixture_stays_pre_release_only(self):
        result = gate.verify_catalog(catalog().encode("utf-8"))
        self.assertEqual(result["result"], "PASS_STATIC_DRAFT_ONLY")
        self.assertEqual((result["free"], result["premium"]), (4, 2))
        self.assertFalse(result["qd_approved"])
        self.assertFalse(result["site_publication_authorized"])

    def test_download_split_midword_and_following_heading(self):
        self.blocked("<p>Down<strong>load </strong><strong>now</strong></p>")

    def test_available_for_download_split(self):
        self.blocked("<p>Avail<strong>able </strong>for <strong>download</strong></p>")

    def test_false_released_claim_split(self):
        self.blocked("<p>Re<strong>leased</strong></p>")

    def test_private_exe_filename_split(self):
        self.blocked("<p>GrantAudit.e<strong>x</strong>e</p>")

    def test_private_msix_filename_split(self):
        self.blocked("<p>ProcureGuard.ms<strong>ix</strong></p>")

    def test_numeric_entity_inside_split_claim(self):
        self.blocked("<p>Down<strong>load &#x6e;ow</strong></p>")

    def test_legitimate_informational_paragraph(self):
        report = gate.verify_catalog(self.inserted(
            "<p>Operators can request an offline pilot discussion.</p>"
        ))
        self.assertEqual(report["result"], "PASS_STATIC_DRAFT_ONLY")

    def test_literal_private_separator_rejected(self):
        self.blocked("<p>This text includes \ue000 SECRET</p>")


if __name__ == "__main__":
    unittest.main()
