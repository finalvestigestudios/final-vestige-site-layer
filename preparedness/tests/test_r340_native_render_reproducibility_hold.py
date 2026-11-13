"""Synthetic R340 adversarial export parity; no claim support, QD, release."""
from __future__ import annotations
import copy
from pathlib import Path
import tempfile
import unittest
from preparedness.tools import r340_native_render_reproducibility_hold as gate

SLUGS=[f'article-{n:02d}' for n in range(1,36)]+[
    'family-reunification-card','reunification-plan','water-planner',
    'kit-builder','power-outage-planner','home-fire-escape-worksheet']
SECTIONS=['start-here','water','food','shelter-power','health-sanitation',
          'family-communication','lost-ways','field-tools']
NAMES=SLUGS+['hub-'+s for s in SECTIONS]+['landing']

def fixture():
    return {f'{folder}/{slug}.html':
            (f'{folder}|{slug}|<!-- draft not public; QD PENDING -->').encode()
            for folder in ('wp','preview') for slug in NAMES}

class RenderParity(unittest.TestCase):
    def setUp(self): self.expected=fixture(); self.actual=fixture()
    def test_clean_synthetic_is_always_draft(self):
        r=gate.exact_compare(self.expected,self.actual)
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(r['matched_private_export_files'],100)
        self.assertEqual(len(r['sha256_manifest']),100)
        for flag in ('qualified_qd_pass','may_publish','may_merge','may_activate_commerce',
                     'realized_net_revenue_verified','emergency_or_medical_advice_approved'):
            self.assertIs(r[flag],False)
    def test_root_absent_fails_without_writing(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(gate.audit_native(Path(td))['state'],'INVALID_HARD_HOLD')
            self.assertEqual(list(Path(td).iterdir()),[])
    def test_identically_tampered_wordpress_and_preview_cannot_hide(self):
        for folder in ('wp','preview'):
            key=f'{folder}/family-reunification-card.html'
            self.actual[key] += b'<!-- unauthorized synchronized change -->'
        r=gate.exact_compare(self.expected,self.actual)
        self.assertEqual(r['state'],'INVALID_HARD_HOLD')
        self.assertEqual(len([e for e in r['errors'] if 'SOURCE_TO_RENDER_BYTES_DRIFT' in e]),2)

    def test_synthetic_clean_never_says_authentic_source(self):
        r=gate.exact_compare(self.expected,self.actual)
        self.assertIs(r['authentic_source_checkout_verified'], False)
        self.assertIs(r['wordpress_live_or_published'], False)

    def test_false_hub_count_report(self):
        expected={'articles':[], 'hubs':[{'section':'start-here','guides':4}], 'landing':{}}
        actual={'articles':[], 'hubs':[{'section':'start-here','guides':0}], 'landing':{},'release_evidence':{
            'state':'HOLD','article_drafts':41,'article_published':0,
            'independent_qa_verified':False,'wordpress_publication_performed':False}}
        self.assertIn('BUILDER_SOURCE_REPORT_DRIFT:hubs',gate.report_compare(expected,actual))

    def test_missing_expected_file(self):
        self.expected.pop('wp/landing.html')
        self.assertIn('EXACT_100_FILE_SET_REQUIRED', gate.exact_compare(self.expected,self.actual)['errors'])
    def test_missing_actual_file(self):
        self.actual.pop('preview/landing.html')
        self.assertTrue(gate.exact_compare(self.expected,self.actual)['errors'])
    def test_extra_file(self):
        self.actual['wp/forged.html']=b'draft'
        self.assertTrue(gate.exact_compare(self.expected,self.actual)['errors'])
    def test_non_bytes_fail_closed(self):
        self.actual['wp/landing.html']='not bytes'
        self.assertTrue(gate.exact_compare(self.expected,self.actual)['errors'])
    def test_source_report_rejects_false_approval(self):
        r={'articles':[], 'hubs':[], 'landing':{},'release_evidence':{
            'state':'LIVE','article_drafts':0,'article_published':41,
            'independent_qa_verified':True,'wordpress_publication_performed':True}}
        self.assertIn('BUILD_REPORT_FALSE_PUBLISH_OR_QD_STATE',gate.report_compare({'articles':[], 'hubs':[], 'landing':{}},r))
    def test_article_order_report_drift(self):
        expected={'articles':[{'slug':'x'}], 'hubs':[], 'landing':{}}
        r={'articles':[{'slug':'y'}], 'hubs':[], 'landing':{},'release_evidence':{'state':'HOLD','article_drafts':41,
            'article_published':0,'independent_qa_verified':False,'wordpress_publication_performed':False}}
        self.assertIn('BUILDER_SOURCE_REPORT_DRIFT:articles',gate.report_compare(expected,r))

def corruption(filename, mode):
    def test(self):
        if mode=='alter':
            self.actual[filename] = self.actual[filename].replace(b'QD PENDING',b'QD APPROVED')
        elif mode=='truncate':self.actual[filename] = self.actual[filename][:-5]
        else:self.actual[filename] += b'<a href="https://payhip.com/fake">Paid</a>'
        result=gate.exact_compare(self.expected,self.actual)
        self.assertEqual(result['state'],'INVALID_HARD_HOLD')
        self.assertIn('SOURCE_TO_RENDER_BYTES_DRIFT:'+filename,result['errors'])
    return test

# All 100 output identities independently attacked; an identical WP+preview
# transformation must not mask divergence from the original frozen source.
for filename in fixture():
    func='test_output_'+filename.replace('/','_').replace('-','_').replace('.','_')
    setattr(RenderParity,func,corruption(filename,'alter'))
for filename in ['wp/landing.html','preview/landing.html','wp/family-reunification-card.html',
                 'preview/family-reunification-card.html','wp/reunification-plan.html','preview/reunification-plan.html']:
    setattr(RenderParity,'test_truncation_'+filename.replace('/','_').replace('-','_').replace('.','_'),corruption(filename,'truncate'))

if __name__=='__main__':unittest.main()
