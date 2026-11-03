"""Source-level negative controls for proposed production/editorial markup parity.

No WordPress production connection, subscriber data or runtime token required.
"""
import unittest
from pathlib import Path
import verify_release_content_parity as parity

ROOT = Path(__file__).resolve().parents[4]
SOURCE = (ROOT / parity.SOURCE).read_bytes()
PAYLOAD = (ROOT / parity.RELEASE_FIXTURE).read_bytes()

class ReleaseCandidateParityTests(unittest.TestCase):
    def test_exact_pr604_source_and_release_payload_match(self):
        report = parity.verify_bytes(SOURCE, PAYLOAD)
        self.assertEqual(report["status"], "CHAPTER_BYTES_AND_EDITORIAL_NOTICES_IDENTICAL")
        self.assertEqual(report["attribution_notices"], ["apollo", "franklin", "malbone"])
        self.assertEqual(report["publication"], "HOLD")
        self.assertEqual(report["wordpress_com_host_parity"], "NOT_ESTABLISHED")

    def test_one_scoped_css_block_is_before_the_hero(self):
        # This experiment changes only parse order, not the editorial
        # seven-chapter content. A pre-hero stylesheet prevents a late
        # style recalculation after the opening text has already rendered.
        text = PAYLOAD.decode("utf-8")
        self.assertTrue(text.startswith("<!-- wp:html -->\n<style>"))
        self.assertEqual(text.count("<style>"), 1)
        self.assertEqual(text.count("</style>"), 1)
        self.assertLess(text.index("</style>"), text.index('data-fv-home-flagship'))
        self.assertEqual(text.count("<script>"), 4)
        self.assertTrue(text.rstrip().endswith("<!-- /wp:html -->"))

    def test_css_first_boundary_does_not_hide_missing_chapters(self):
        raw = PAYLOAD.decode("utf-8").replace(
            '<section class="fv-hf__opening"', '<section class="fv-hf__lost-opening"', 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_CHAPTER_BOUNDARY"):
            parity.compare_interiors(SOURCE.decode("utf-8"), raw)

    def test_independent_repo_fixture_is_accessible(self):
        self.assertEqual(parity.verify_repo(ROOT)["status"],
                         "CHAPTER_BYTES_AND_EDITORIAL_NOTICES_IDENTICAL")

    def test_nojs_fallbacks_are_exactly_two_decorative_eager_images(self):
        for content in (SOURCE.decode("utf-8"), PAYLOAD.decode("utf-8")):
            self.assertEqual(content.count('<noscript>'), 2)
            self.assertEqual(content.count('data-fv-noscript-archive'), 2)
            self.assertEqual(content.count('loading="eager"'), 2)
            self.assertEqual(content.count('role="presentation" aria-hidden="true"'), 2)

    def test_joint_removal_of_nojs_images_is_detected(self):
        import re
        a = re.sub(r'<noscript>\s*<img\b[^>]*>\s*</noscript>', '', SOURCE.decode('utf-8'))
        p = re.sub(r'<noscript>\s*<img\b[^>]*>\s*</noscript>', '', PAYLOAD.decode('utf-8'))
        with self.assertRaisesRegex(ValueError, 'RELEASE_PARITY_NOJS_ARCHIVE_FALLBACK_UNSAFE'):
            parity.compare_interiors(a, p)

    def test_joint_repointing_of_nojs_image_to_unreviewed_source_fails(self):
        a = SOURCE.decode('utf-8').replace('data-fv-noscript-archive', 'data-fv-noscript-archive', 1)
        p = PAYLOAD.decode('utf-8')
        target = 'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'
        import re
        # Change only the fallback source; preserve the real lazy image.
        def reroute(text):
            return re.sub(r'(<noscript><img src=")' + re.escape(target),
                          r'\g<1>https://example.invalid/unreviewed.jpg', text, count=1)
        a, p = reroute(a), reroute(p)
        self.assertNotEqual(a, SOURCE.decode('utf-8'))
        with self.assertRaisesRegex(ValueError, 'RELEASE_PARITY_NOJS_ARCHIVE_FALLBACK_UNSAFE'):
            parity.compare_interiors(a, p)

    def test_stage_rights_deletion_is_detected_even_without_blob_pins(self):
        a = SOURCE.decode("utf-8")
        p = PAYLOAD.decode("utf-8")
        changed = a.replace(parity.RIGHTS["apollo"], "", 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_CHAPTER_BYTES_DIFFER"):
            parity.compare_interiors(changed, p)

    def test_production_rights_deletion_is_detected_even_without_blob_pins(self):
        a = SOURCE.decode("utf-8")
        p = PAYLOAD.decode("utf-8")
        changed = p.replace(parity.RIGHTS["franklin"], "", 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_CHAPTER_BYTES_DIFFER"):
            parity.compare_interiors(a, changed)

    def test_matching_but_missing_nypl_notice_is_not_accepted(self):
        a = SOURCE.decode("utf-8").replace(parity.RIGHTS["malbone"], "", 1)
        p = PAYLOAD.decode("utf-8").replace(parity.RIGHTS["malbone"], "", 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_RIGHTS_MALBONE"):
            parity.compare_interiors(a, p)

    def test_nypl_credit_is_present_without_unsupported_public_domain_conclusion(self):
        for content in (SOURCE.decode("utf-8"), PAYLOAD.decode("utf-8")):
            self.assertIn(parity.RIGHTS["malbone"], content)
            self.assertNotIn(
                "NYPL believes this item is in the public domain under United States law.",
                content,
            )
        self.assertEqual(parity.verify_bytes(SOURCE, PAYLOAD)["nypl_capture_rights"], "UNVERIFIED_NOT_REPRODUCED")

    def test_reintroducing_old_nypl_claim_to_both_sources_fails(self):
        old = "NYPL believes this item is in the public domain under United States law."
        a = SOURCE.decode("utf-8").replace(parity.RIGHTS["malbone"], old, 1)
        p = PAYLOAD.decode("utf-8").replace(parity.RIGHTS["malbone"], old, 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_UNVERIFIED_NYPL_RIGHTS_CLAIM"):
            parity.compare_interiors(a, p)

    def test_repointing_nypl_source_link_in_both_sources_fails(self):
        official = "https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0"
        a = SOURCE.decode("utf-8").replace(official, "https://example.org/unknown", 1)
        p = PAYLOAD.decode("utf-8").replace(official, "https://example.org/unknown", 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_NYPL_ORIGINAL_LINK"):
            parity.compare_interiors(a, p)

    def test_joint_reintroduction_of_nypl_capture_reproduction_fails(self):
        # Matching staging/production HTML must not launder unlicensed images.
        needle = '<div class="fv-hf__source-plate"'
        img = ('<img src="https://i0.wp.com/finalvestige.com/'
               'wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg">')
        a = SOURCE.decode("utf-8").replace(needle, img + needle, 1)
        p = PAYLOAD.decode("utf-8").replace(needle, img + needle, 1)
        self.assertNotEqual(a, SOURCE.decode("utf-8"))
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_NYPL_UNCLEARED_IMAGE_REPRODUCTION"):
            parity.compare_interiors(a, p)

    def test_original_nypl_link_is_preserved_without_image_payload(self):
        for raw in (SOURCE, PAYLOAD):
            page=raw.decode("utf-8")
            self.assertNotIn('edit-017-v02-nypl-5003296-original.jpg',page)
            self.assertIn('ARCHIVAL REFERENCE · IMAGE NOT REPRODUCED',page)
        self.assertEqual(parity.verify_bytes(SOURCE,PAYLOAD)["nypl_capture_rights"],
                         "UNVERIFIED_NOT_REPRODUCED")

    def test_matching_but_missing_commercial_notice_is_not_accepted(self):
        a = SOURCE.decode("utf-8").replace(parity.MIND_NOTICE, "", 1)
        p = PAYLOAD.decode("utf-8").replace(parity.MIND_NOTICE, "", 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_MIND_DISCLOSURE"):
            parity.compare_interiors(a, p)

    def test_stage_study_banner_must_not_enter_public_block(self):
        p = PAYLOAD.decode("utf-8").replace(
            '<div class="fv-hf__canvas">', 'DESIGN CANDIDATE <div class="fv-hf__canvas">', 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_STUDY_BANNER_LEAK"):
            parity.compare_interiors(SOURCE.decode("utf-8"), p)

    def test_wrong_wordpress_wrapper_fails_even_if_chapters_equal(self):
        p = PAYLOAD.decode("utf-8").replace(
            '<div class="fv-hf fv-hf--wp alignfull" data-fv-home-flagship>',
            '<div class="fv-hf" data-fv-home-flagship>', 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_WORDPRESS_WRAPPER"):
            parity.compare_interiors(SOURCE.decode("utf-8"), p)

    def test_root_hash_prevents_jointly_injected_editorial_claim(self):
        a = SOURCE.replace(b"nothing on this page is for sale", b"clinically proven changes")
        p = PAYLOAD.replace(b"nothing on this page is for sale", b"clinically proven changes")
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_SOURCE_BLOB_MISMATCH"):
            parity.verify_bytes(a, p)

    def test_production_payload_signature_is_independently_pinned(self):
        altered = PAYLOAD.replace(b"<style>", b"<style data-injected='true'>", 1)
        with self.assertRaisesRegex(ValueError, "RELEASE_PARITY_PROPOSED_BLOCK_BLOB_MISMATCH"):
            parity.verify_bytes(SOURCE, altered)

if __name__ == "__main__":
    unittest.main()
