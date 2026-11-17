"""R445 adversarial synthetic tests; structural custody is not safety approval."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC=Path(__file__).resolve().parents[1]/'tools'/'r445_url_crosswalk_bijection.py'
spec=importlib.util.spec_from_file_location('r445',SRC)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

def fixture():
    pins=[{'branch':f'claude/prep-synthetic-{i}', 'sha':f'{i+1:040x}'} for i in range(9)]
    groups=[];byid={};i=0
    for j in range(17):
        ids=[f'src-{n:03d}' for n in range(i,i+(3 if j<5 else 2))]
        i+=len(ids);url=f'https://agency.example/shared-{j}'
        groups.append({'url':url,'ids':ids,'review_required':True})
        for sid in ids:byid[sid]=url
    for n in range(i,203):byid[f'src-{n:03d}']=f'https://agency.example/solo-{n}'
    rows=[]
    for n,(sid,url) in enumerate(byid.items()):
        variants=[{'branch':pins[0]['branch'],'source_blob':'a'*40,'url':url}]
        if n<77:variants.append({'branch':pins[1]['branch'],'source_blob':'b'*40,'url':url})
        rows.append({'source_id':sid,'variants':variants})
    disputes=[]
    for row in rows[:5]:
        disputes.append({'source_id':row['source_id'],'decision':'HUMAN_REVIEW_REQUIRED',
                         'selected_record':None,
                         'variants':[dict(v,supports_exact='Limited cited claim',
                                          reading_scope_notes_exact='Specific paragraph; human review pending')
                                     for v in row['variants']]})
    forks=[]
    for k in range(9):
        forks.append({'decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,
                      'requires_reading_depth_review':True,'requires_source_citation_review':True,
                      'variants':[{'branch':pins[z]['branch'],'git_blob_sha':f'{k+z+1:040x}',
                                   'byte_length':1000+z} for z in (0,1)]})
    return {'schema':1,'repo':'finalvestigestudios/final-vestige-site-layer',
            'issue':136,'parent_conversion_issue':820,'release_state':g.DRAFT,
            'publication_approved':False,'qualified_safety_approved':False,
            'automatic_variant_selection':False,'merchant_offer_verified':False,
            'branch_pins':pins,'original_articles':[{'slug':f'article-{k}'} for k in range(35)],
            'all_original_source_id_crosswalk':rows,'shared_exact_url_review_groups':groups,
            'source_evidence_disputes':disputes,'original_fork_disputes':forks}

class Gate(unittest.TestCase):
    def setUp(self):self.d=fixture()
    def errors(self):return g.audit(self.d)['errors']
    def test_synthetic_shape_only(self):
        r=g.audit(self.d)
        self.assertEqual(35,r['articles']);self.assertEqual(203,r['source_ids'])
        self.assertEqual(280,r['occurrences']);self.assertEqual(181,r['exact_urls'])
        self.assertEqual(17,r['review_groups']);self.assertEqual(5,r['disputes']);self.assertEqual(9,r['forks'])
        self.assertEqual(['AUTHENTIC_R397_BYTES_MISSING','CURRENT_BRANCH_SHA_EVIDENCE_MISSING_OR_DRIFTED'],r['errors'])
    def test_never_release(self):
        r=g.audit(self.d)
        self.assertEqual('DRAFT_HARD_HOLD',r['release_state'])
        self.assertFalse(r['publishable']);self.assertFalse(r['qd_pass']);self.assertFalse(r['paid_offer_verified'])
    def test_real_byte_pin_cannot_be_forged_by_counts(self):
        self.assertIn('AUTHENTIC_R397_BYTES_MISSING',g.audit(self.d,json.dumps(self.d).encode())['errors'])
    def test_not_mutating_original(self):
        before=copy.deepcopy(self.d);g.audit(self.d);self.assertEqual(before,self.d)
    def test_wrong_current_sha_fails(self):
        heads={p['branch']:p['sha'] for p in self.d['branch_pins']};heads.pop(next(iter(heads)))
        self.assertIn('CURRENT_BRANCH_SHA_EVIDENCE_MISSING_OR_DRIFTED',g.audit(self.d,observed_heads=heads)['errors'])
    def test_actual_relationships_not_only_count(self):
        row=self.d['all_original_source_id_crosswalk'][0]
        for v in row['variants']:v['url']=self.d['shared_exact_url_review_groups'][1]['url']
        self.assertIn('EXACT_URL_BIJECTION_DRIFT:',','.join(self.errors()))
    def test_missing_file_cli_still_holds(self):
        p=subprocess.run([sys.executable,'-I',str(SRC),'missing.json'],capture_output=True,text=True)
        self.assertEqual(2,p.returncode);self.assertFalse(json.loads(p.stdout)['qd_pass'])
    def test_fixture_cli_still_holds(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'d.json';path.write_text(json.dumps(self.d))
            p=subprocess.run([sys.executable,'-I',str(SRC),str(path)],capture_output=True,text=True)
            self.assertEqual(2,p.returncode);self.assertFalse(json.loads(p.stdout)['publishable'])

CASES=[
 ('owner',lambda d:d.update(repo='false/site'),'DOCKET_OWNER_DRIFT'),
 ('issue',lambda d:d.update(issue=999),'DOCKET_OWNER_DRIFT'),
 ('campaign',lambda d:d.update(parent_conversion_issue=999),'DOCKET_OWNER_DRIFT'),
 ('schema',lambda d:d.update(schema=4),'DOCKET_OWNER_DRIFT'),
 ('release',lambda d:d.update(release_state='LIVE'),'FALSE_RELEASE_OR_COMMERCE_APPROVAL'),
 ('publish',lambda d:d.update(publication_approved=True),'FALSE_RELEASE_OR_COMMERCE_APPROVAL'),
 ('qd',lambda d:d.update(qualified_safety_approved=True),'FALSE_RELEASE_OR_COMMERCE_APPROVAL'),
 ('commerce',lambda d:d.update(merchant_offer_verified=True),'FALSE_RELEASE_OR_COMMERCE_APPROVAL'),
 ('variant_auto',lambda d:d.update(automatic_variant_selection=True),'FALSE_RELEASE_OR_COMMERCE_APPROVAL'),
 ('missing_pin',lambda d:d['branch_pins'].pop(),'NINE_CONTRIBUTORS_NOT_PRESERVED'),
 ('duplicate_pin',lambda d:d['branch_pins'][1].update(branch=d['branch_pins'][0]['branch']),'NINE_CONTRIBUTORS_NOT_PRESERVED'),
 ('missing_source',lambda d:d['all_original_source_id_crosswalk'].pop(),'SOURCE_ID_COUNT_DRIFT'),
 ('duplicate_id',lambda d:d['all_original_source_id_crosswalk'][1].update(source_id=d['all_original_source_id_crosswalk'][0]['source_id']),'DUPLICATE_SOURCE_ID:'),
 ('bad_source_row',lambda d:d['all_original_source_id_crosswalk'].__setitem__(0,None),'INVALID_SOURCE_ROW:'),
 ('remove_variant',lambda d:d['all_original_source_id_crosswalk'][0].update(variants=[]),'SOURCE_VARIANTS_MISSING:'),
 ('extra_variant',lambda d:d['all_original_source_id_crosswalk'][0]['variants'].append({'branch':d['branch_pins'][2]['branch'],'source_blob':'c'*40,'url':'https://agency.example/new'}),'SOURCE_OCCURRENCE_COUNT_DRIFT'),
 ('wrong_branch',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(branch='untrusted'),'UNKNOWN_VARIANT_BRANCH:'),
 ('duplicate_id_branch',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][1].update(branch=d['all_original_source_id_crosswalk'][0]['variants'][0]['branch']),'REPEATED_ID_BRANCH:'),
 ('bad_blob',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(source_blob='z'*40),'INVALID_SOURCE_BLOB:'),
 ('missing_url',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url=None),'INVALID_SOURCE_URL:'),
 ('http_url',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url='http://agency.example/a'),'INVALID_SOURCE_URL:'),
 ('js_url',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url='javascript:alert(1)'),'INVALID_SOURCE_URL:'),
 ('credentials_url',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url='https://x:y@agency.example/'), 'INVALID_SOURCE_URL:'),
 ('space_url',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url='https://agency.example/a b'),'INVALID_SOURCE_URL:'),
 ('bidi_url',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url='https://agency.example/\u202ea'),'INVALID_SOURCE_URL:'),
 ('lost_url',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url='https://agency.example/new'),'EXACT_URL_COUNT_DRIFT'),
 ('changed_group_id',lambda d:d['shared_exact_url_review_groups'][0]['ids'].__setitem__(0,'src-150'),'EXACT_URL_BIJECTION_DRIFT:'),
 ('lost_group',lambda d:d['shared_exact_url_review_groups'].pop(),'SHARED_URL_COUNT_DRIFT'),
 ('duplicate_group_url',lambda d:d['shared_exact_url_review_groups'][1].update(url=d['shared_exact_url_review_groups'][0]['url']),'DUPLICATE_REVIEW_GROUP_URL:'),
 ('duplicate_group_id',lambda d:d['shared_exact_url_review_groups'][0]['ids'].__setitem__(1,d['shared_exact_url_review_groups'][0]['ids'][0]),'DUPLICATE_GROUP_ID:'),
 ('group_url_changed',lambda d:d['shared_exact_url_review_groups'][0].update(url='https://agency.example/wrong'),'EXACT_URL_BIJECTION_DRIFT:'),
 ('group_review_removed',lambda d:d['shared_exact_url_review_groups'][0].update(review_required=False),'SHARED_URL_REVIEW_REMOVED:'),
 ('missing_dispute',lambda d:d['source_evidence_disputes'].pop(),'FIVE_DISPUTES_CHANGED'),
 ('selected_dispute',lambda d:d['source_evidence_disputes'][0].update(selected_record=0),'PREMATURE_SOURCE_SELECTION:'),
 ('decided_dispute',lambda d:d['source_evidence_disputes'][0].update(decision='APPROVED'),'PREMATURE_SOURCE_SELECTION:'),
 ('duplicate_dispute_id',lambda d:d['source_evidence_disputes'][1].update(source_id=d['source_evidence_disputes'][0]['source_id']),'DUPLICATE_DISPUTED_ID:'),
 ('wrong_dispute_url',lambda d:d['source_evidence_disputes'][0]['variants'][0].update(url='https://agency.example/false'),'DISPUTE_CROSSWALK_VARIANT_MISMATCH:'),
 ('wrong_dispute_blob',lambda d:d['source_evidence_disputes'][0]['variants'][0].update(source_blob='z'*40),'DISPUTE_CROSSWALK_VARIANT_MISMATCH:'),
 ('missing_scope',lambda d:d['source_evidence_disputes'][0]['variants'][0].update(reading_scope_notes_exact=''),'DISPUTE_SCOPE_LOST:'),
 ('missing_support',lambda d:d['source_evidence_disputes'][0]['variants'][0].update(supports_exact=''),'DISPUTE_SCOPE_LOST:'),
 ('missing_dispute_variants',lambda d:d['source_evidence_disputes'][0].update(variants=[]),'DISPUTE_VARIANTS_LOST:'),
 ('missing_fork',lambda d:d['original_fork_disputes'].pop(),'NINE_FORKS_CHANGED'),
 ('selected_fork',lambda d:d['original_fork_disputes'][0].update(selected_sha='a'*40),'PREMATURE_FORK_SELECTION:'),
 ('decided_fork',lambda d:d['original_fork_disputes'][0].update(decision='APPROVED'),'PREMATURE_FORK_SELECTION:'),
 ('depth_false',lambda d:d['original_fork_disputes'][0].update(requires_reading_depth_review=False),'FORK_REVIEW_DEPTH_LOST:'),
 ('citations_false',lambda d:d['original_fork_disputes'][0].update(requires_source_citation_review=False),'FORK_REVIEW_DEPTH_LOST:'),
 ('fork_variants_lost',lambda d:d['original_fork_disputes'][0].update(variants=[]),'FORK_VARIANTS_LOST:'),
 ('variant_branch_list',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(branch=['bad']),'UNKNOWN_VARIANT_BRANCH:'),
 ('variant_url_list',lambda d:d['all_original_source_id_crosswalk'][0]['variants'][0].update(url=['bad']),'INVALID_SOURCE_URL:'),
 ('group_id_list',lambda d:d['shared_exact_url_review_groups'][0]['ids'].__setitem__(0,['bad']),'NONSTRING_GROUP_SOURCE_ID:'),
 ('dispute_id_list',lambda d:d['source_evidence_disputes'][0].update(source_id=['bad']),'INVALID_DISPUTED_ID:'),
 ('dispute_blob_list',lambda d:d['source_evidence_disputes'][0]['variants'][0].update(source_blob=['bad']),'DISPUTE_CROSSWALK_VARIANT_MISMATCH:'),

]
for name,mutate,error in CASES:
    def test(self,mutate=mutate,error=error):
        mutate(self.d)
        self.assertTrue(any(x.startswith(error) for x in self.errors()),self.errors())
    setattr(Gate,'test_adversarial_'+name,test)
if __name__=='__main__':unittest.main()
