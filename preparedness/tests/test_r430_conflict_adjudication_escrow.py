"""R430 synthetic adversarial tests. No authentic manuscript or clinical approval."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'r430_conflict_adjudication_escrow.py'
_spec = importlib.util.spec_from_file_location('r430_conflict_adjudication_escrow', SCRIPT)
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)
A = 'a'*40
B = 'b'*40
C = 'c'*40
BRANCHES = ['claude/prep-'+str(i) for i in range(9)]
PATHS = ['preparedness/content/articles/article-'+str(i//2)+('.body.html' if i%2==0 else '.meta.json') for i in range(8)] + ['preparedness/sources/fragments/shelter.json']


def fixture():
    ids = [{'source_id':'s-'+str(i), 'variants':[{'branch':BRANCHES[i%9], 'source_blob':A,'url':'https://example.org/'+str(i)}]} for i in range(203)]
    disputes = []
    for i in range(5):
        vars = []
        for j in range(2):
            vars.append({'branch':BRANCHES[j], 'source_blob':A, 'url':'https://example.org/'+str(i),
                         'verified_on':'2026-10-29', 'human_link_check':False,
                         'publisher':'An agency','supports_exact':'Claim with specified boundaries',
                         'reading_scope_notes_exact':'Only the indicated landing page was read',
                         'fragment':'preparedness/sources/fragments/'+str(j)+'.json'})
        ids[i]['variants'] = [{k:v[k] for k in ('branch','source_blob','url')} for v in vars]
        disputes.append({'source_id':'s-'+str(i),'decision':'HUMAN_REVIEW_REQUIRED','selected_record':None,'variants':vars})
    forks=[]
    for i,path in enumerate(PATHS):
        forks.append({'path':path,'decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,
                     'requires_reading_depth_review':True,'requires_source_citation_review':True,
                     'variants':[{'branch':BRANCHES[j], 'git_blob_sha':[A,B][j], 'byte_length':1234+j} for j in range(2)]})
    return {'schema':1, 'issue':136, 'provenance':'ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY',
            'release_state':'DRAFT_HARD_HOLD','publication_approved':False,
            'qualified_safety_approved':False,'merchant_offer_verified':False,
            'automatic_variant_selection':False,
            'expected':dict(g.EXPECTED_COUNTS),'observed':dict(g.EXPECTED_COUNTS),
            'branch_pins':[{'branch':b,'sha':A} for b in BRANCHES],
            'original_articles':[{'slug':'article-'+str(i)} for i in range(35)],
            'all_original_source_id_crosswalk':ids,
            'source_evidence_disputes':disputes,'original_fork_disputes':forks}


def review(d=None, test_only=True, raw=None):
    if d is None:
        d=fixture()
    if raw is None:
        raw=json.dumps(d,sort_keys=True).encode()
    return g.audit(d,raw=raw,test_only=test_only)

class Baseline(unittest.TestCase):
    def test_14_cases(self):
        r=review();self.assertTrue(r['escrow_structure_ok'],r['errors'])
        self.assertEqual(len(r['unresolved_cases']),14)
        self.assertEqual(r['source_disputes_unresolved'],5)
        self.assertEqual(r['manuscript_forks_unresolved'],9)
    def test_all_fork_candidates_remain_visible(self):
        r=review()
        self.assertEqual(sum(len(c['contenders']) for c in r['unresolved_cases']),28)
    def test_never_approval_or_revenue(self):
        r=review()
        for k in ('eligible','publication_approved','qualified_safety_approved','paid_activation_approved','merchant_offer_verified'):
            self.assertIs(r[k],False)
        self.assertIsNone(r['verified_paid_orders'])
        self.assertIsNone(r['net_revenue_per_1000_qualified_humans'])
    def test_normalized_case_order_independent_digest(self):
        d=fixture();a=review(d)
        d['original_fork_disputes'].reverse();d['source_evidence_disputes'].reverse()
        b=review(d)
        self.assertEqual(a['review_receipt_sha256'],b['review_receipt_sha256'])
    def test_distinct_sha_not_auto_selected(self):
        r=review();f=next(c for c in r['unresolved_cases'] if c['kind']=='MANUSCRIPT_FORK')
        self.assertEqual(f['unique_git_blob_count'],2)
        self.assertIsNone(f['selected'])
    def test_same_sha_two_branches_keep_both(self):
        d=fixture();d['original_fork_disputes'][0]['variants'][1]['git_blob_sha']=A
        d['original_fork_disputes'][0]['variants'][1]['byte_length']=1234
        r=review(d); self.assertTrue(r['escrow_structure_ok'],r['errors'])
        f=next(c for c in r['unresolved_cases'] if c['id']==PATHS[0]);self.assertEqual(f['unique_git_blob_count'],1)
        self.assertEqual(len(f['contenders']),2)
    def test_scope_text_preserved_not_promoted(self):
        r=review();s=next(c for c in r['unresolved_cases'] if c['kind']=='SOURCE_APPLICABILITY')
        self.assertIn('only',s['contenders'][0]['reading_scope_as_drafted'].lower())
        self.assertEqual(s['contenders'][0]['evidence_status'],'CLAIM_ONLY_REQUIRES_INDEPENDENT_REVIEW')
    def test_strict_native_pin_rejects_synthetic(self):
        r=review(test_only=False)
        self.assertIn('R430_ORIGINAL_GIT_BLOB_UNVERIFIED',r['errors'])
    def test_raw_json_mismatch(self):
        d=fixture();raw=json.dumps(d).encode();d['original_articles'][0]['slug']='changed'
        r=review(d,raw=raw);self.assertIn('R430_RAW_OBJECT_MISMATCH',r['errors'])
    def test_duplicate_json_keys(self):
        self.assertRaises(ValueError,g.unique_pairs,[('schema',1),('schema',2)])
    def test_missing_docket_cli_hard_hold_exit_two(self):
        p=subprocess.run([sys.executable,'-I',str(SCRIPT),'/missing/not-here.json'],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['eligible'])
    def test_synthetic_cli_cannot_bypass_pin(self):
        with tempfile.TemporaryDirectory() as t:
            f=Path(t)/'original.json';f.write_text(json.dumps(fixture()))
            p=subprocess.run([sys.executable,'-I',str(SCRIPT),str(f)],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,2)
            self.assertIn('R430_ORIGINAL_GIT_BLOB_UNVERIFIED',json.loads(p.stdout)['errors'])
    def test_no_test_only_cli_flag(self):
        p=subprocess.run([sys.executable,str(SCRIPT),'--test-only','/none'],capture_output=True,text=True,timeout=10)
        self.assertNotEqual(p.returncode,0)
    def test_path_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'doc.json';target.write_text(json.dumps(fixture()))
            link=Path(t)/'alias';link.symlink_to(target)
            p=subprocess.run([sys.executable,str(SCRIPT),str(link)],capture_output=True,text=True,timeout=10)
            self.assertIn('R430_UNAVAILABLE_OR_INVALID_ORIGINAL_ValueError',json.loads(p.stdout)['errors'])

MUTATIONS = [
 ('root_wrong_schema',lambda d:d.__setitem__('schema',2)),
 ('root_wrong_issue',lambda d:d.__setitem__('issue',820)),
 ('root_wrong_provenance',lambda d:d.__setitem__('provenance','SELECTED')),
 ('root_fake_release',lambda d:d.__setitem__('release_state','PASS')),
 ('root_publication_true',lambda d:d.__setitem__('publication_approved',True)),
 ('root_qd_true',lambda d:d.__setitem__('qualified_safety_approved',True)),
 ('root_merchant_true',lambda d:d.__setitem__('merchant_offer_verified',True)),
 ('root_automatic_selection',lambda d:d.__setitem__('automatic_variant_selection',True)),
 ('expected_count_changed',lambda d:d['expected'].__setitem__('source_evidence_disputes',4)),
 ('observed_count_changed',lambda d:d['observed'].__setitem__('unselected_original_forks',8)),
 ('expected_boolean_count',lambda d:d['expected'].__setitem__('source_evidence_disputes',True)),
 ('removed_branch',lambda d:d['branch_pins'].pop()),
 ('changed_branch_sha',lambda d:d['branch_pins'][0].__setitem__('sha','not-sha')),
 ('duplicate_branch',lambda d:d['branch_pins'][1].__setitem__('branch',d['branch_pins'][0]['branch'])),
 ('removed_source',lambda d:d['all_original_source_id_crosswalk'].pop()),
 ('duplicate_source_id',lambda d:d['all_original_source_id_crosswalk'][1].__setitem__('source_id','s-0')),
 ('removed_article',lambda d:d['original_articles'].pop()),
 ('duplicate_article',lambda d:d['original_articles'][1].__setitem__('slug','article-0')),
 ('unrelated_article_slug',lambda d:d['original_articles'][0].__setitem__('slug','../bad')),
 ('removed_dispute',lambda d:d['source_evidence_disputes'].pop()),
 ('duplicated_dispute',lambda d:d['source_evidence_disputes'][1].__setitem__('source_id','s-0')),
 ('renamed_dispute_id',lambda d:d['source_evidence_disputes'][0].__setitem__('source_id','unknown-id')),
 ('source_decision_pass',lambda d:d['source_evidence_disputes'][0].__setitem__('decision','PASS')),
 ('source_selected_record',lambda d:d['source_evidence_disputes'][0].__setitem__('selected_record',{'url':'https://example.org'})),
 ('source_one_variant',lambda d:d['source_evidence_disputes'][0]['variants'].pop()),
 ('source_removed_variants',lambda d:d['source_evidence_disputes'][0].__setitem__('variants',None)),
 ('source_wrong_branch',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('branch','claude/bad')),
 ('source_wrong_blob',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('source_blob',B)),
 ('source_invalid_blob',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('source_blob','xyz')),
 ('source_http_url',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('url','http://example.org')),
 ('source_empty_url',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('url','')),
 ('source_url_control',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('url','https://example.org\n')),
 ('source_claims_link_verified',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('human_link_check',True)),
 ('source_support_missing',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('supports_exact','')),
 ('source_reading_scope_missing',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('reading_scope_notes_exact',None)),
 ('source_publisher_missing',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('publisher','')),
 ('source_date_missing',lambda d:d['source_evidence_disputes'][0]['variants'][0].__setitem__('verified_on',None)),
 ('source_duplicate_variant',lambda d:d['source_evidence_disputes'][0]['variants'].__setitem__(1,copy.deepcopy(d['source_evidence_disputes'][0]['variants'][0]))),
 ('removed_fork',lambda d:d['original_fork_disputes'].pop()),
 ('duplicate_fork_path',lambda d:d['original_fork_disputes'][1].__setitem__('path',PATHS[0])),
 ('traversal_fork_path',lambda d:d['original_fork_disputes'][0].__setitem__('path','../evil.body.html')),
 ('foreign_article_fork',lambda d:d['original_fork_disputes'][0].__setitem__('path','preparedness/content/articles/foreign.body.html')),
 ('fork_decision_pass',lambda d:d['original_fork_disputes'][0].__setitem__('decision','PASS')),
 ('fork_selected_sha',lambda d:d['original_fork_disputes'][0].__setitem__('selected_sha',A)),
 ('fork_skips_depth',lambda d:d['original_fork_disputes'][0].__setitem__('requires_reading_depth_review',False)),
 ('fork_skips_source',lambda d:d['original_fork_disputes'][0].__setitem__('requires_source_citation_review',False)),
 ('fork_one_variant',lambda d:d['original_fork_disputes'][0]['variants'].pop()),
 ('fork_missing_variants',lambda d:d['original_fork_disputes'][0].__setitem__('variants',None)),
 ('fork_bad_branch',lambda d:d['original_fork_disputes'][0]['variants'][0].__setitem__('branch','x')),
 ('fork_duplicate_branch',lambda d:d['original_fork_disputes'][0]['variants'][1].__setitem__('branch',BRANCHES[0])),
 ('fork_bad_blob',lambda d:d['original_fork_disputes'][0]['variants'][0].__setitem__('git_blob_sha','zip')),
 ('fork_bad_length',lambda d:d['original_fork_disputes'][0]['variants'][0].__setitem__('byte_length',-4)),
 ('fork_boolean_length',lambda d:d['original_fork_disputes'][0]['variants'][0].__setitem__('byte_length',True)),
 ('fork_too_big',lambda d:d['original_fork_disputes'][0]['variants'][0].__setitem__('byte_length',2000001)),
 ('fork_same_sha_different_length',lambda d:d['original_fork_disputes'][0]['variants'][1].__setitem__('git_blob_sha',A)),
]

class Adversarial(unittest.TestCase):pass

def make_case(label,attack):
    def run(self):
        d=fixture();attack(d)
        r=review(d)
        self.assertFalse(r['escrow_structure_ok'],label)
        self.assertFalse(r['eligible'],label)
        self.assertTrue(r['errors'],label)
    run.__name__='test_attack_'+label
    return run

for i,(label,attack) in enumerate(MUTATIONS):
    setattr(Adversarial,'test_%02d_%s'%(i,label),make_case(label,attack))

if __name__=='__main__': unittest.main()
