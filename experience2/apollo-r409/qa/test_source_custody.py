#!/usr/bin/env python3
"""R409 adversarial custody QA; synthetic fixtures do not verify original NASA HTML."""
import importlib.util, subprocess, sys, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent; SRC=HERE/'source_custody.py'
spec=importlib.util.spec_from_file_location('custody',SRC)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
R=HERE.parent; ANCESTOR=R.parent/'apollo-r408';
HTML=subprocess.check_output(['php',str(ANCESTOR/'qa/fixture.php')],text=True)
# Original HTML fixture renders two instances; release expects a single canonical one.
FIRST=HTML[HTML.find('<div class="fv-r408__experience">'):]
CUT=FIRST.find('<div class="fv-r408__experience">',4)
FIRST=FIRST[:CUT] if CUT!=-1 else FIRST
# Synthetic positive control only: match expected source headings and boundaries,
# without representing it as the authentic NASA source template.
for i,heading in enumerate(m.EXPECTED_HEADINGS,1):
    FIRST=FIRST.replace(f'Test-only record {i}</h3>',heading+'</h3>')
FIRST=FIRST.replace('</section></div>',
    '<p>Ignition source not conclusively identified. Later deliberate tests are not evidence identifying the original ignition.</p></section></div>')
class CustodyTests(unittest.TestCase):
    def test_original_missing_holds(self):
        x=m.release_review(FIRST,None);self.assertEqual(x['status'],'HOLD');self.assertFalse(x['release_authorized'])
        self.assertIn('authentic_PR158_source_custody',x['blockers'])
    def test_html_parser_detects_real_records(self):
        x=m.check_rendered(FIRST);self.assertTrue(x['pass'],x['errors']);self.assertEqual(x['atlas_cards'],6)
    def test_injected_checkout_refused(self):
        x=m.check_rendered(FIRST.replace('</section>','<a href="https://payhip.com/b/abc">Buy now</a></section>',1))
        self.assertIn('unapproved_link',x['errors'])
    def test_official_lookalike_host_refused(self):
        x=m.check_rendered(FIRST.replace(m.BOARD,'https://www.nasa.gov.evil.example/path'))
        self.assertIn('unapproved_link',x['errors'])
    def test_javascript_url_refused(self):
        self.assertFalse(m.allowable_link('javascript:alert(1)'))
    def test_protocol_relative_url_refused(self):
        self.assertFalse(m.allowable_link('//www.nasa.gov/example'))
    def test_embedded_media_refused(self):
        x=m.check_rendered(FIRST.replace('</section>','<img src="/unreviewed.jpg"></section>',1));self.assertIn('forbidden_element:img',x['errors'])
    def test_geo_claim_refused(self):
        x=m.check_rendered(FIRST.replace('data-fv-r408-kind="aftermath"','data-lat="28.4" data-fv-r408-kind="aftermath"'))
        self.assertIn('embedded_or_geo_assets',x['errors'])
    def test_broken_fragment_refused(self):
        x=m.check_rendered(FIRST.replace('record-03">Inspect evidence','record-99">Inspect evidence'))
        self.assertTrue(any(e.startswith('broken_anchor:') for e in x['errors']))
    def test_duplicate_id_refused(self):
        x=m.check_rendered(FIRST.replace('id="fv-r408-atlas-1-title"','id="fv-r408-atlas-1-title" id="fv-r408-atlas-1-title"'))
        self.assertIn('duplicate_attribute',x['errors'])
    def test_category_drift_refused(self):
        x=m.check_rendered(FIRST.replace('data-fv-r408-kind="investigation"','data-fv-r408-kind="aftermath"'))
        self.assertIn('atlas_categories',x['errors'])
    def test_limit_disclosures_required(self):
        x=m.check_rendered(FIRST.replace('<summary>Source and evidence limit</summary>','<p>Hidden</p>'))
        self.assertIn('native_source_disclosures',x['errors'])
    def test_original_wrong_git_blob_holds(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'ledger.html';p.write_text(FIRST)
            self.assertEqual(m.check_original(p)['error'],'original_PR158_template_blob_drift')
    def test_absent_axe_and_cwv_block(self):
        x=m.release_review(FIRST,None);self.assertIn('genuine_axe_core',x['blockers']);self.assertIn('navigated_CWV',x['blockers'])
    def test_forbid_self_release_authority(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipt.json';p.write_text('{}')
            x=m.release_review(FIRST,None,staging_receipt=p,axe_receipt=p,cwvs_receipt=p,approved=True)
            self.assertFalse(x['release_authorized']);self.assertEqual(x['status'],'HOLD')
if __name__=='__main__':unittest.main(verbosity=2)
