"""R83 mutation tests: a green nested pattern must not disguise source drift."""
from __future__ import annotations
import unittest
from wp_source_parity_r83 import NASA_SOURCE_URLS, CITE_IDS, verify_source_parity_r83


class SourceParityR83(unittest.TestCase):
    def setUp(self):
        self.good = dict(
            nasa_links=NASA_SOURCE_URLS, citation_ids=CITE_IDS, drawer_count=6,
            images=0, geographic_claims=0,
            suite_heading=('Six NASA sources; no image-use rights are asserted. '
                           'Record 01 uses an unconfirmed S67-19766 association.'),
            rights_notice=('0 of 6 photographs cleared. This was not a human link check, '
                           'photograph inspection, or rights clearance.'),
        )

    def assert_hold(self, code, **mutation):
        inputs = {**self.good, **mutation}
        with self.assertRaises(AssertionError) as caught:
            verify_source_parity_r83(**inputs)
        self.assertEqual(str(caught.exception), code)
        self.assertNotIn('https://', str(caught.exception))

    def test_approved_five_verified_one_provisional_rights_pending(self):
        result = verify_source_parity_r83(**self.good)
        self.assertEqual(result['approved_nasa_destinations'], 6)
        self.assertEqual(result['individual_photo_rights_cleared'], 0)
        self.assertTrue(result['catalog_source_01_provisional'])
        self.assertFalse(result['official_link_fetch_or_rights_verified'])
        self.assertTrue(all(isinstance(v, (int, bool)) for v in result.values()))

    def test_reordered_official_links_fail(self):
        self.assert_hold('R77_R83_LINK_CUSTODY_CHANGED',
                         nasa_links=NASA_SOURCE_URLS[::-1])

    def test_lookalike_private_url_fails_without_echoing_url(self):
        self.assert_hold('R77_R83_LINK_CUSTODY_CHANGED',
                         nasa_links=NASA_SOURCE_URLS[:-1] +
                         ('https://www.nasa.gov.attacker.invalid/image-detail/',))

    def test_six_cards_but_missing_citation_fails(self):
        self.assert_hold('R77_R83_CITATIONS_MISSING', citation_ids=CITE_IDS[:-1])

    def test_six_citations_but_duplicate_id_fails(self):
        self.assert_hold('R77_R83_CITATIONS_MISSING', citation_ids=CITE_IDS[:-1] + ('05',))

    def test_nativesource_drawer_missing_fails(self):
        self.assert_hold('R77_R83_SOURCE_DRAWERS_MISSING', drawer_count=5)

    def test_media_injection_fails_even_with_legitimate_links(self):
        self.assert_hold('R77_R83_MEDIA_UNCLEARED', images=1)

    def test_unverified_map_pin_fails(self):
        self.assert_hold('R77_R83_GEO_UNVERIFIED', geographic_claims=1)

    def test_unqualified_image_permission_phrase_fails(self):
        self.assert_hold('R77_R83_RIGHTS_NOTICE_MISSING', suite_heading='Images cleared for use')

    def test_catalog_association_promoted_to_confirmed_fails(self):
        self.assert_hold('R77_R83_PROVISIONAL_NOTICE_MISSING',
                         suite_heading='No image-use rights are asserted. S67-19766 confirmed.')

    def test_rights_ledger_missing_fails(self):
        self.assert_hold('R77_R83_RIGHTS_CLEARANCE_UNVERIFIED',
                         rights_notice='Five sources verified, everything permitted.')

    def test_claim_of_media_approval_fails(self):
        self.assert_hold('R77_R83_RIGHTS_CLEARANCE_UNVERIFIED',
                         rights_notice='6 of 6 photographs rights clearance complete.')

if __name__ == '__main__':
    unittest.main()
