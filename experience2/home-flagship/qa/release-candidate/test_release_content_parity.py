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

    def test_independent_repo_fixture_is_accessible(self):
        self.assertEqual(parity.verify_repo(ROOT)["status"],
                         "CHAPTER_BYTES_AND_EDITORIAL_NOTICES_IDENTICAL")

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
