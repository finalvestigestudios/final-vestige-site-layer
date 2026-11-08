"""Native Python 3 unit tests for read-only Dispatch mail preview builder."""
from pathlib import Path
import json
import tempfile
import unittest
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_offline_previews import build,inline_html,sections,preview_html,GATE,POSTAL,OPTOUT

class PreviewSafety(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.out=Path(self.tmp.name)
        self.report=build(self.out)
    def tearDown(self): self.tmp.cleanup()
    def test_exactly_six_editions(self): self.assertEqual(len(self.report['issues']),6)
    def test_four_editorial_two_commercial(self): self.assertEqual([x['kind'] for x in self.report['issues']].count('commercial-review-pending'),2)
    def test_never_sends(self): self.assertIs(self.report['send_capability'],False)
    def test_all_held(self): self.assertTrue(all(x['release']=='HOLD' for x in self.report['issues']))
    def test_all_offline_holds(self):
        for i in range(1,7):
            page=(self.out/f'{i:02d}.html').read_text()
            self.assertIn(GATE,page);self.assertIn(POSTAL,page);self.assertIn(OPTOUT,page)
    def test_html_and_plaintext_exist(self):
        for i in range(1,7):
            self.assertTrue((self.out/f'{i:02d}.txt').is_file())
            self.assertTrue((self.out/f'{i:02d}.html').is_file())
    def test_no_scripts_or_remote_images(self):
        for p in self.out.glob('*.html'):
            page=p.read_text().lower()
            for forbidden in ('<script','<iframe','<form','<img','http-equiv="refresh"','javascript:'):
                self.assertNotIn(forbidden,page)
    def test_mailing_address_remains_unverified(self):
        self.assertEqual(self.report['release_status'],'HOLD')
    def test_product_cta_not_hyperlinked(self):
        for i in (3,5):
            page=(self.out/f'{i:02d}.html').read_text()
            self.assertNotIn('href="https://zen12.com/',page)
            self.assertNotIn('href="https://hypnosislive.com/',page)
    def test_plaintext_contains_source(self):
        self.assertIn('Twelve minutes is an inviting proposition',(self.out/'03.txt').read_text())
    def test_site_links_https_firstparty(self):
        self.assertIn('href="https://finalvestige.com/focus/"',(self.out/'06.html').read_text())
    def test_external_markdown_link_not_live(self):
        self.assertIn('[external link withheld in offline preview]',inline_html('[merchant](https://zen12.com/hnp)'))
    def test_script_tag_escaped(self):
        self.assertIn('&lt;script&gt;',inline_html('<script>'))
    def test_subject_html_escaped(self):
        self.assertIn('&lt;bad&gt;',preview_html('<bad>','z',[],1))
    def test_no_merchant_sales_verified(self):
        self.assertTrue(all(x['merchant_permission']!='VERIFIED' for x in self.report['issues']))
    def test_not_jetpack_received(self):
        self.assertTrue(all(x['jetpack_received_preview']=='NOT_OBTAINED' for x in self.report['issues']))
    def test_preheaders_are_candidate_not_native_proven(self):
        self.assertIn('Preheader candidate',(self.out/'01.html').read_text())
    def test_json_audit_is_strictly_nonbuyer(self):
        audit=json.loads((self.out/'audit.json').read_text());self.assertNotIn('email_address',audit)
    def test_index_accessible_named_links(self):
        x=(self.out/'index.html').read_text();self.assertIn('<html lang="en">',x);self.assertEqual(x.count('plaintext</a>'),6)
    def test_layout_meta_viewport(self):
        self.assertIn('width=device-width',(self.out/'03.html').read_text())
    def test_commercial_drafts_disclosed(self):
        for i in (3,5):
            x=(self.out/f'{i:02d}.html').read_text();self.assertIn('Commercial disclosure',x)
    def test_origin_commit_in_audit(self):
        self.assertEqual(self.report['source_commit'],'d57ccdba3aee8f065e143e101c2945f4f3d01647')

if __name__=='__main__':unittest.main()
