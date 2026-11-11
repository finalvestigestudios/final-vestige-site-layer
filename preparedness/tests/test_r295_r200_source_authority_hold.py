"""Review-only synthetic adversarial tests. No real article/source safety approval."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'r295_r200_source_authority_hold.py'
spec = importlib.util.spec_from_file_location('r295_hold', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SHAS = {
    'start':'2122d856fce9f64887c16df3d52e64be9f59a55b',
    'shelter':'5daeaf2dd5ab71806a6b73c91edfb1d8df5da976',
    'food':'f911ff7a655de8d81535ea86ec3d65a49ee76648',
    'health':'d5ef5bafd68361434dd1cc9209915b8e8a4eaf17',
    'hist-food':'67e116e536c7410bed30f8f3b1bb8c166f3c223d',
    'hist-home':'7504a5f099594d635e3dd7332a33a2e1346c43a2',
    'hist-field':'4e5caf812727953aa45e3bda2d382f2c67b6a09c',
}
ROWS = [
 ('hist-food','pemmican-and-dried-meats',46,2498,7,False),
 ('hist-food','pioneer-travel-rations',39,2438,1,False),
 ('hist-home','pickling-fermentation-old-recipes',49,2853,0,True),
 ('hist-home','root-cellars-cool-storage',42,2903,0,True),
 ('hist-home','sanitation-before-germ-theory',48,2793,0,True),
 ('hist-field','navigation-before-gps',47,3002,0,True),
 ('hist-field','pioneer-supply-chains-failed',63,3270,0,True),
]

def make_valid():
    articles=[]
    for i in range(35):
        if i < 7:
            cluster,slug,*_=ROWS[i]
            section='lost-ways'
        else:
            cluster='start'; slug=f'synthetic-article-{i}'; section='start-here'
        articles.append({'slug':slug,'section':section,'source_cluster':cluster,
                         'route':f'/preparedness/{section}/{slug}/','branch_sha':SHAS[cluster],
                         'body_oid':'a'*40,'meta_oid':'b'*40})
    r200={'state':'DRAFT_HARD_HOLD','publication_authorized':False,
          'independent_qd_pass':False,'human_source_approved':False,'medical_safety_verified':False,
          'artifact_count':35,'export_target_count_with_six_tools':41,
          'branch_heads':dict(SHAS),'articles':articles}
    r293={'clusters':{k:{'head':v,'frozen':v if k in ('start','shelter') else 'f'*40,
                           'status':'identical' if k in ('start','shelter') else 'ahead'} for k,v in SHAS.items()}}
    receipt={'live_branch_comparisons':{k:{'r200_base':v,'observed_head':v,'ahead_by':0,
        'behind_by':0,'changed_files':0,'status':'identical'} for k,v in SHAS.items()}}
    witnesses={k:{'cluster':k,'state':'DRAFT_HARD_HOLD','publication_authorized':False,
            'independent_qd_pass':False,'medical_safety_verified':False,'privacy_approved':False,
            'witness_commit_refs':{'live':SHAS[k],'frozen':'f'*40,
                                   'integrated':mod.R293_INTEGRATED},'articles':[]}
        for k in mod.R294}
    for cluster,slug,total,words,alias_count,match in ROWS:
        route='/preparedness/lost-ways/'+slug+'/'
        counts={'source-a':total-alias_count}
        r200_counts=dict(counts)
        if alias_count:
            counts['hist-food-nchfp-jerky']=alias_count
            r200_counts['nchfp-jerky']=alias_count
        status={'editorial':'drafted','publish':'draft'}
        def meta(ids): return {'status':dict(status),'section':'lost-ways',
                                'canonical_route':route,'source_use_ids':list(ids),
                                'safety_review':{'state':'pending'}}
        witnesses[cluster]['articles'].append({
            'slug':slug,'body':{'live':{'citations':r200_counts,'citation_count':total,
                    'word_tokens':words},'integrated':{'citations':counts,'citation_count':total,
                    'word_tokens':words}},'meta':{'live':meta(r200_counts),
                    'integrated':meta(counts)},'comparisons':{'integrated_equals_live_lf':match}})
    return [r200,r293,witnesses,receipt]


class R295ProvenanceSafetyTests(unittest.TestCase):
    def setUp(self): self.args=make_valid()
    def check(self, fragment):
        result=mod.examine(*self.args)
        self.assertFalse(result['mechanical_consistency'], result)
        self.assertTrue(any(fragment in e for e in result['errors']), result)
        self.assertEqual(result['state'],'INVALID_HARD_HOLD')
        for k in ('publication_authorized','independent_qd_pass','medical_safety_verified',
                  'privacy_approved','merchant_offer_verified'):
            self.assertIs(result[k],False)
    def test_valid_mechanical_state_never_passes_publication(self):
        r=mod.examine(*self.args)
        self.assertTrue(r['mechanical_consistency'],r)
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(r['counts']['r200_routes'],35)
        self.assertEqual(r['counts']['r294_routes'],7)
        self.assertEqual(r['counts']['r294_citations'],334)
        self.assertEqual(r['counts']['r294_exact_id_substitutions'],8)
        self.assertEqual(r['counts']['branches_matching_r200'],7)
        self.assertEqual(r['counts']['same_witness_articles'],5)
        self.assertEqual(len(r['review_warnings']),10)
    def test_false_qd_is_detected(self):
        self.args[0]['independent_qd_pass']=True; self.check('R200_RELEASE_HOLD_CORRUPT')
    def test_false_publication_flag_is_detected(self):
        self.args[0]['publication_authorized']=True; self.check('R200_RELEASE_HOLD_CORRUPT')
    def test_false_medical_flag_is_detected(self):
        self.args[0]['medical_safety_verified']=True; self.check('R200_RELEASE_HOLD_CORRUPT')
    def test_34_articles_rejected(self):
        self.args[0]['articles'].pop(); self.check('R200_DUPLICATE_OR_MISSING_ROUTES')
    def test_overspecified_word_count_rejected(self):
        a=self.args[2]['hist-field']['articles'][0]; a['body']['integrated']['word_tokens']-=1
        self.check('R294_READING_DEPTH_LOSS')
    def test_replacement_count_rejected(self):
        a=self.args[2]['hist-food']['articles'][0]
        a['body']['integrated']['citations']['hist-food-nchfp-jerky']-=1
        self.check('R294_BAD_CITATION_COUNTER')
    def test_safety_metadata_rejected(self):
        self.args[2]['hist-food']['articles'][0]['meta']['integrated']['status']['publish']='published'
        self.check('R294_UNEXPECTED_SAFETY_STATE')
    def test_wrong_integrated_witness_rejected(self):
        self.args[2]['hist-home']['witness_commit_refs']['integrated']='f'*40
        self.check('R294_WRONG_INTEGRATED_WITNESS')
    def test_unreviewed_citation_drift_rejected(self):
        a=self.args[2]['hist-home']['articles'][0]
        a['body']['integrated']['citations']['source-a']-=1
        a['body']['integrated']['citations']['fake-source']=1
        a['meta']['integrated']['source_use_ids'].append('fake-source')
        self.check('R294_UNREVIEWED_CITATION_DRIFT')
    def test_shortened_route_rejected(self):
        self.args[2]['hist-home']['articles'][1]['meta']['integrated']['canonical_route']='/broken/'
        self.check('R294_ROUTE_DRIFT')
    def test_stale_live_branch_receipt_rejected(self):
        self.args[3]['live_branch_comparisons']['start']['observed_head']='f'*40
        self.check('LIVE_HEAD_NOT_R200')
    def test_changed_branch_rejected(self):
        self.args[3]['live_branch_comparisons']['food']['ahead_by']=1
        self.check('LIVE_BRANCH_CHANGED')
    def test_missing_cluster_rejected(self):
        del self.args[2]['hist-home'];self.check('R294_MISSING_CLUSTER')


def route_case(index):
    def test(self):
        self.args[0]['articles'][index]['route']=self.args[0]['articles'][0]['route']
        self.check('R200_DUPLICATE_OR_MISSING_ROUTES' if index else 'R200_BAD_ROUTE')
    return test

# 34 independent duplicate-route negative cases, plus 14 fixed tests.
for i in range(1,35):
    setattr(R295ProvenanceSafetyTests,f'test_duplicate_route_{i:02d}',route_case(i))


def branch_case(cluster):
    def test(self):
        self.args[0]['branch_heads'][cluster]='f'*40
        self.check('R200_ARTICLE_CUSTODY' if cluster in ('start','hist-food','hist-home','hist-field')
                   else 'R293_HEAD_NOT_R200')
    return test
for c in SHAS:
    setattr(R295ProvenanceSafetyTests,f'test_r200_branch_sha_tamper_{c.replace("-","_")}',branch_case(c))

if __name__=='__main__': unittest.main()
