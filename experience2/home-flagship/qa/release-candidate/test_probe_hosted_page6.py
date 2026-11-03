"""Offline fail-closed regression tests: no public network calls or CMS credentials."""
from __future__ import annotations
import unittest
from probe_hosted_page6 import CHAPTER_TARGETS, inspect_public_html, evaluate_receipts, internal_focus_link, first_party_media_url


def fixture(image_vector: str = "", margins: int = 72, focus: int = 2,
            jetpack: bool = True) -> str:
    chapters = "".join(f'<a href="#{c}">A</a><section id="{c}"></section>'
                       for c in CHAPTER_TARGETS)
    records = "".join(f'<span class="fv-margin-strip__item" style="--i:{i}">Record</span>'
                      for i in range(margins))
    links = '<a href="https://finalvestige.com/focus/">Fieldbook</a>' * focus
    images = ('<img src="https://files.example.net/s67-19766.webp">'
              '<img src="https://files.example.net/Franklinexpeditionnote.jpg">')
    jet = '<div class="wp-block-jetpack-subscriptions"></div>' if jetpack else ''
    return '<html><body><div data-fv-home-flagship>' + chapters + records + links + images + jet + image_vector + '</div></body></html>'


class HostedPublicAdmissionTests(unittest.TestCase):
    def test_fixture_passes_protected_structural_contract(self):
        a = inspect_public_html(fixture())
        self.assertTrue(a['structural']['protected_content_ok'])
        self.assertFalse(a['nypl_binary_embedded'])
        self.assertEqual(a['structural']['margins_count'], 72)
        self.assertEqual(a['structural']['chapter_targets_and_links'], 7)

    def test_img_src_and_srcset_nypl_each_hold(self):
        for vector in ('<img src="https://i0.wp.com/example/edit-017-v02-nypl-5003296-original.jpg">',
                       '<source srcset="https://x/nypl-5003296-original.jpg 1x">',
                       '<img data-src="https://x/nypl-5003296-original.jpg">'):
            with self.subTest(vector=vector):
                r = inspect_public_html(fixture(image_vector=vector))
                self.assertTrue(r['nypl_binary_embedded'])
                self.assertTrue(r['nypl_vectors'])
                self.assertTrue(r['structural']['protected_content_ok'])

    def test_catalog_link_does_not_imply_image_reproduction(self):
        r = inspect_public_html(fixture(image_vector='<a href="https://nypl.org/item/5003296">Catalog</a>'))
        self.assertFalse(r['nypl_binary_embedded'])

    def test_forged_external_focus_does_not_qualify(self):
        for bad in ('https://finalvestige.com.evil.test/focus/',
                    'https://evil.test/focus/', 'javascript:alert(1)',
                    'http://finalvestige.com/focus/', '/focus-fake/'):
            with self.subTest(bad=bad):
                self.assertFalse(internal_focus_link(bad))

    def test_first_party_media_must_be_exact_authorized_source(self):
        self.assertTrue(first_party_media_url(
            "https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp",
            "s67-19766.webp"))
        for candidate in ("https://evil.test/wp-content/uploads/2026/08/s67-19766.webp",
                          "https://finalvestige.com.evil.test/wp-content/uploads/2026/08/s67-19766.webp",
                          "https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg",
                          "https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp?fit=1",
                          "http://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp"):
            self.assertFalse(first_party_media_url(candidate, "s67-19766.webp"))

    def test_missing_margin_is_structural_failure(self):
        self.assertFalse(inspect_public_html(fixture(margins=71))['structural']['protected_content_ok'])

    def test_duplicate_margin_index_fails(self):
        h = fixture().replace('style="--i:71"', 'style="--i:70"')
        self.assertFalse(inspect_public_html(h)['structural']['protected_content_ok'])

    def test_lost_jetpack_fails(self):
        self.assertFalse(inspect_public_html(fixture(jetpack=False))['structural']['protected_content_ok'])

    def test_lost_focus_link_fails(self):
        self.assertFalse(inspect_public_html(fixture(focus=1))['structural']['protected_content_ok'])

    def test_missing_chapter_anchor_fails(self):
        self.assertFalse(inspect_public_html(fixture().replace('href="#fv-hf-mind-title"',
                                                'href="#wrong"'))['structural']['protected_content_ok'])

    def test_invalid_html_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'HOST_HTML_INVALID'):
            inspect_public_html('oops')

    def test_release_never_passes_on_clean_fixture(self):
        receipt = [dict(test_case=f'js_{width}', http_status=200, host='finalvestige.com',
                        protected_content_ok=True, nypl_binary_embedded=False)
                   for width in (320, 390, 768, 1440, 1920)]
        receipt.append(dict(test_case='nojs_390', http_status=200, host='finalvestige.com',
                            protected_content_ok=True, nypl_binary_embedded=False))
        receipt[1]['first_party_media'] = {'apollo': {'status': 'PASS'},
                                          'franklin': {'status': 'PASS'}}
        self.assertEqual(evaluate_receipts(receipt)['release_gate'], 'HOLD')
        self.assertEqual(evaluate_receipts(receipt)['structural_gate'], 'PASS')
        self.assertEqual(evaluate_receipts(receipt)['first_party_archive_binary_gate'], 'PASS')
        receipt[1]['first_party_media']['apollo']['status'] = 'TRANSFER_FAILED'
        self.assertEqual(evaluate_receipts(receipt)['first_party_archive_binary_gate'], 'FAIL')
        receipt[0]['nypl_binary_embedded'] = True
        self.assertEqual(evaluate_receipts(receipt)['nypl_image_specific_rights_gate'],
                         'HOLD_REPRODUCTION_PRESENT')

    def test_incomplete_or_bad_hosted_browser_matrix_fails(self):
        rec = [dict(test_case=f'js_{w}', http_status=200, host='finalvestige.com',
                    protected_content_ok=True, nypl_binary_embedded=False)
               for w in (320,390,768,1440,1920)]
        with self.assertRaisesRegex(ValueError,'HOST_BROWSER_MATRIX_INCOMPLETE'):
            evaluate_receipts(rec)
        rec.append(dict(test_case='nojs_390', http_status=403, host='finalvestige.com',
                        protected_content_ok=True, nypl_binary_embedded=False))
        self.assertEqual(evaluate_receipts(rec)['structural_gate'], 'FAIL')
        rec[-1]['http_status'] = 200
        rec[0]['host'] = 'evil.test'
        self.assertEqual(evaluate_receipts(rec)['structural_gate'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
