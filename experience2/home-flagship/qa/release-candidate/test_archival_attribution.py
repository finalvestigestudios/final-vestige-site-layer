import unittest
from verify_archival_attribution import audit


def fixture():
    from verify_archival_attribution import EXPECTED
    blocks=[]
    for name,spec in EXPECTED.items():
        img='https://finalvestige.com/wp-content/uploads/2026/08/'+spec['filename']
        srcset=(f'https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/{spec["filename"]}'
                '?fit=600%2C400&amp;ssl=1 600w')
        links=''.join(f'<a href="{link}">Inspect source</a>' for link in spec['sources'])
        blocks.append(f'<article data-fv-case="{name}"><figure><img data-fv-archive-img src="{img}" '
                      f'srcset="{srcset}" sizes="(max-width: 600px) 100vw, 600px" '
                      'width="900" height="900" loading="lazy" decoding="async" '
                      f'alt="Detailed historical archival evidence belonging to {name} with authentic materials" />'
                      f'</figure><p>Evidence boundary: interpretation is limited.</p>{links}</article>')
    return '<html><body>'+''.join(blocks)+'</body></html>'


class AttributionTest(unittest.TestCase):
    def test_valid_three_case_fixture(self):
        z=audit(fixture())
        self.assertEqual(z['status'],'PASS_SOURCE_LINKS_ONLY')
        self.assertEqual(z['case_count'],3)
        self.assertFalse(z['rights_cleared'])
        self.assertEqual(z['release'],'HOLD')

    def test_off_domain_image(self):
        self.assertEqual(audit(fixture().replace('https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
                                                 'https://evil.example/s67-19766.webp'))['status'],'FAIL')

    def test_forged_folio_rmg_image(self):
        self.assertEqual(audit(fixture().replace('https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg',
                                                 'https://images.rmg.co.uk/Franklinexpeditionnote.jpg'))['status'],'FAIL')

    def test_missing_source_link(self):
        self.assertEqual(audit(fixture().replace('https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg',
                                                 'https://example.org/not-the-image'))['status'],'FAIL')

    def test_wrong_nypl_item(self):
        self.assertEqual(audit(fixture().replace('c745e730-d2a9-012f-5ecc-58d385a7bbd0',
                                                 '172ae4f0-d292-012f-aace-58d385a7b928'))['status'],'FAIL')

    def test_missing_alt(self):
        self.assertEqual(audit(fixture().replace('alt="Detailed historical archival evidence belonging to apollo with authentic materials"',
                                                 'alt=""'))['status'],'FAIL')

    def test_missing_srcset(self):
        self.assertEqual(audit(fixture().replace('srcset="https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp?fit=600%2C400&amp;ssl=1 600w"',
                                                 'srcset=""'))['status'],'FAIL')

    def test_missing_evidence_limit(self):
        self.assertEqual(audit(fixture().replace('Evidence boundary: interpretation is limited.',
                                                 'Everything is certain.'))['status'],'FAIL')

    def test_new_unexpected_case(self):
        self.assertEqual(audit(fixture()+'<article data-fv-case="fabrication"></article>')['status'],'FAIL')

    def test_duplicate_case(self):
        a=fixture()
        self.assertEqual(audit(a+a[a.index('<article'):a.index('</article>')+len('</article>')])['status'],'FAIL')

    def test_orphan_image(self):
        self.assertEqual(audit(fixture()+'<img data-fv-archive-img src="x">')['status'],'FAIL')

    def test_unsafe_http_srcset(self):
        self.assertEqual(audit(fixture().replace('https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
                                                 'http://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'))['status'],'FAIL')

if __name__ == '__main__':unittest.main()
