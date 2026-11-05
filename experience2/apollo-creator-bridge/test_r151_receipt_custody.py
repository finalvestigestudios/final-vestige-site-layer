import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from r149_gallery_release_candidate import propose, digest
from r150_real_excerpt_gate import git_blob_sha
import r151_receipt_custody as target

SRC=Path(__file__).with_name('r149_model_fixture_unpatched.html').read_text()
WIDTHS=target.WIDTHS

class Custody(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)
        self.html=SRC
        self.r149={'schema':'fv.apollo.r149.browser.v1','scope':'OFFLINE_SOURCE_FRAGMENT_NOT_RENDERED_WP',
                   'source_sha256':digest(SRC),'candidate_sha256':digest(propose(SRC)),
                   'browser_version':'144.0.0', 'approved_to_publish':False,'screenshots':[],'checks':[]}
        for stage in ('before','after'):
            for w in WIDTHS:
                checks=target.STAGE_CHECKS | (target.AFTER_CHECKS if stage=='after' else set())
                self.r149['checks'] += [{'stage':stage,'width':w,'check':k,'pass':True} for k in checks]
        self.r149['checks'] += [{'stage':'nojs','width':390,'check':x,'pass':True} for x in
            ('all_three_figures_visible','all_three_nasa_links','slider_enhancement_hidden')]
        self.r149['failed']=0; self.r149['passed']=len(self.r149['checks'])
        for name in sorted(target.SCREENSHOTS):
            (self.path/name).write_bytes(name.encode())
            import hashlib
            self.r149['screenshots'].append({'file':name,'sha256':hashlib.sha256(name.encode()).hexdigest()})
        self.r150={'schema':'fv.apollo.r150.source-bound-browser.v1',
                   'source':{'type':'ACTUAL_WP_DERIVED_EXCERPT','original_blob':git_blob_sha(SRC),'candidate_blob':git_blob_sha(propose(SRC))},
                   'r150_extra':{'checks':[], 'axe_results':[]},'axe':'EXECUTED','failed':0,
                   'approved_to_publish':False,'production_qa_complete':False,
                   'actual_site_browser':'NOT_EXECUTED','rights':'NOT_CLEARED_FOR_COMMERCIAL_PRODUCT',
                   'sales':'NOT_VERIFIED','screenshots':copy.deepcopy(self.r149['screenshots'])}
        for w in WIDTHS:
            self.r150['r150_extra']['checks'] += [{'width':w,'check':k,'pass':True} for k in target.NOJS_CHECKS|{'axe_no_wcag_violations'}]
            self.r150['r150_extra']['axe_results'].append({'width':w,'violations':[],'incomplete':0})
        self.patch=patch.object(target,'ACTUAL_WP_EXCERPT_BLOB',git_blob_sha(SRC))
        self.patch.start();self.addCleanup(self.patch.stop)
    def result(self):return target.audit(self.html,self.r149,self.r150,self.path)
    def assert_bad(self, category):
        r=self.result();self.assertIn(r['status'],{'FAIL_STAGING_HOLD','INCOMPLETE_STAGING_HOLD'});self.assertTrue(any(category in x for x in r['errors']+r['incomplete']))
    def test_valid_source_excerpt_receipts_pass_but_not_live(self):
        r=self.result(); self.assertEqual(r['status'],'SOURCE_EXCERPT_QA_PASS_STAGING_HOLD');self.assertFalse(r['approved_to_publish'])
    def test_synthetic_downgrade_rejected(self):self.r150['source']['type']='CONTROLLED_MODEL';self.assert_bad('scope')
    def test_altered_source_rejected(self):self.html+='<!-- drift -->';self.assert_bad('pinned')
    def test_mismatched_candidate_blob_rejected(self):self.r150['source']['candidate_blob']='0'*40;self.assert_bad('candidate_blob')
    def test_tampered_screenshot_rejected(self):(self.path/next(iter(target.SCREENSHOTS))).write_bytes(b'tamper');self.assert_bad('screenshot')
    def test_missing_screenshot_rejected(self):(self.path/next(iter(target.SCREENSHOTS))).unlink();self.assert_bad('screenshot')
    def test_forged_axe_without_results_rejected(self):self.r150['r150_extra']['axe_results']=[];self.assert_bad('axe')
    def test_axe_incomplete_blocks_pass(self):self.r150['r150_extra']['axe_results'][0]['incomplete']=1;self.assert_bad('axe')
    def test_axe_violation_blocks_pass(self):self.r150['r150_extra']['axe_results'][0]['violations']=[{'id':'color-contrast'}];self.assert_bad('axe')
    def test_axe_missing_check_blocks_pass(self):
        checks=self.r150['r150_extra']['checks']
        checks.remove(next(c for c in checks if c['width']==320 and c['check']=='axe_no_wcag_violations'))
        self.assert_bad('axe')
    def test_axe_not_executed_blocks_pass(self):self.r150['axe']='NOT_EXECUTED_AXE_UNAVAILABLE';self.assert_bad('axe')
    def test_js_gallery_missing_pass_rejected(self):self.r149['checks'][0]['pass']=False;self.assert_bad('chrome')
    def test_nojs_missing_at_mobile_rejected(self):
        c=next(c for c in self.r150['r150_extra']['checks'] if c['width']==320 and c['check']=='no_js_three_context_photos')
        c['pass']=False;self.assert_bad('nojs')
    def test_fake_paid_sales_rejected(self):self.r150['sales']='20';self.assert_bad('sales')
    def test_fake_rights_rejected(self):self.r150['rights']='CLEARED';self.assert_bad('rights')
    def test_fake_publish_permission_rejected(self):self.r150['approved_to_publish']=True;self.assert_bad('unsafe_publish')
    def test_screenshot_receipt_split_rejected(self):self.r150['screenshots']=[];self.assert_bad('screenshot_manifest_divergence')
    def test_browser_not_executed_rejected(self):self.r149['browser_version']='';self.assert_bad('chromium_version')
    def test_unpatched_shape_corrupted_rejected(self):self.html=self.html.replace('const photos = $(box','const photos = $$(box');self.assert_bad('source_unpatched_shape')

if __name__=='__main__':unittest.main()
