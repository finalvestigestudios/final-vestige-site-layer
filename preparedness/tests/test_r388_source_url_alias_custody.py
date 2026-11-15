"""R388 adversarial synthetic URL/source-identity tests; not real QD clearance."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location('r388', HERE/'tools/r388_source_url_alias_custody.py')
R=importlib.util.module_from_spec(sp);sp.loader.exec_module(R)

SHA='a'*40

def row(sid, url, branch='one'):
    return {'id':sid,'url':url,'branch':branch,'fragment':'preparedness/sources/fragments/food.json', 'source_blob':SHA}

def fixture():
    # No claims of externally reviewed sources; every record is synthetic.
    cross={'original_fragment_count':7,'source_id_variants':[
        {'id':'alpha','variants':[row('alpha','https://www.cdc.gov/emergency/a/?utm_source=abc', 'one')]},
        {'id':'beta','variants':[row('beta','https://www.cdc.gov/emergency/a/', 'two')]},
        {'id':'gamma','variants':[row('gamma','https://usda.gov/safety/food','one')]}
    ]}
    base={'sources':[{'id':'alpha','url':'https://www.cdc.gov/emergency/a'}, {'id':'delta','url':'https://usda.gov/safety/food'}]}
    claims=[{'source_id':s,'article':f'art-{i}', 'branch':'one','citation_ordinal':i,'claim_sha256':'f'*64} for i,s in enumerate(('alpha','beta','gamma','delta'),1)]
    impact={'status':R.PROVENANCE_STATUS,'publication_approved':False,'qualified_safety_approved':False,
            'counts':{'original_articles':35,'source_collision_groups':5},'claims':claims}
    return cross,base,impact

class KnownTests(unittest.TestCase):
    def test_synthetic_alias_status_never_approval(self):
        x=R.build_alias_docket(*fixture()); self.assertEqual(x['status'],'SOURCE_URL_ALIAS_REVIEW_HARD_HOLD')
        self.assertFalse(x['publication_approved']);self.assertFalse(x['qualified_safety_approved'])
        self.assertFalse(x['merchant_offer_verified']);self.assertFalse(x['live_release_allowed'])
    def test_synthetic_expected_alias_groups(self):
        x=R.build_alias_docket(*fixture());self.assertEqual(x['counts']['alias_review_groups'],2)
        self.assertEqual(sorted(x['ids'] for x in x['alias_review']),[['alpha','beta'],['delta','gamma']])
    def test_synthetic_claim_impact_not_fabricated(self):
        x=R.build_alias_docket(*fixture());self.assertEqual(x['counts']['impacted_claim_occurrences'],4)
    def test_provenance_source_digest_deterministic(self):
        x=R.build_alias_docket(*fixture());y=R.build_alias_docket(*fixture()); self.assertEqual(x,y)
    def test_no_input_mutation(self):
        inp=fixture();cp=copy.deepcopy(inp);R.build_alias_docket(*inp);self.assertEqual(inp,cp)
    def test_query_values_never_exposed(self):
        c,b,i=fixture();c['source_id_variants'][0]['variants'][0]['url']='https://www.cdc.gov/emergency/a/?utm_campaign=private-token-XYZ'
        raw=json.dumps(R.build_alias_docket(c,b,i));self.assertNotIn('private-token-XYZ',raw)
    def test_same_id_same_url_not_alias(self):
        c,b,i=fixture(); c['source_id_variants']=[];b['sources']=[{'id':'alpha','url':'https://www.cdc.gov/a'}, {'id':'alpha','url':'https://www.cdc.gov/a'}]
        x=R.build_alias_docket(c,b,i);self.assertEqual(x['counts']['alias_review_groups'],0)
    def test_all_original_claims_kept(self):
        x=R.build_alias_docket(*fixture());self.assertEqual(x['alias_review'][0]['claim_occurrences'],2)
    def test_source_equality_is_not_asserted(self):
        x=R.build_alias_docket(*fixture());self.assertTrue(all(not a['source_equivalence_proven'] and not a['human_adjudicated'] for a in x['alias_review']))
    def test_same_id_different_destinations_requires_adjudication(self):
        c,b,i=fixture(); b['sources'].append({'id':'alpha','url':'https://example.edu/elsewhere'})
        x=R.build_alias_docket(c,b,i)
        self.assertEqual(x['counts']['identity_drift_ids'],1)
        self.assertEqual(x['source_id_identity_drift'][0]['id'],'alpha')
        self.assertFalse(x['source_id_identity_drift'][0]['human_adjudicated'])
    def test_percent_encoded_dotdot_is_not_silently_normalized(self):
        with self.assertRaises(ValueError):R.url_identity('https://cdc.gov/a/%2e%2e/b')
    def test_source_safety_is_not_asserted(self):
        self.assertTrue(all(a['source_safe_for_advice'] is False for a in R.build_alias_docket(*fixture())['alias_review']))
    def test_bad_impact_status(self):
        c,b,i=fixture();i['status']='PASSED';self.assertIn('UNAUTHENTIC_CLAIM_IMPACT',R.build_alias_docket(c,b,i)['errors'])
    def test_approval_flag_tampering(self):
        c,b,i=fixture();i['publication_approved']=True;self.assertEqual(R.build_alias_docket(c,b,i)['status'],'INVALID_HARD_HOLD')
    def test_qualified_approval_flag_tampering(self):
        c,b,i=fixture();i['qualified_safety_approved']=True;self.assertEqual(R.build_alias_docket(c,b,i)['status'],'INVALID_HARD_HOLD')
    def test_bad_original_article_count(self):
        c,b,i=fixture();i['counts']['original_articles']=34;self.assertIn('SOURCE_CLAIM_COVERAGE_DRIFT',R.build_alias_docket(c,b,i)['errors'])
    def test_bad_original_collision_count(self):
        c,b,i=fixture();i['counts']['source_collision_groups']=0;self.assertIn('SOURCE_CLAIM_COVERAGE_DRIFT',R.build_alias_docket(c,b,i)['errors'])
    def test_no_original_claims(self):
        c,b,i=fixture();i['claims']=[];self.assertIn('MISSING_ORIGINAL_CLAIMS',R.build_alias_docket(c,b,i)['errors'])
    def test_missing_original_seven_fragments(self):
        c,b,i=fixture();c['original_fragment_count']=6;self.assertIn('NOT_SEVEN_ORIGINAL_FRAGMENTS',R.build_alias_docket(c,b,i)['errors'])
    def test_duplicate_source_group(self):
        c,b,i=fixture();c['source_id_variants'].append(copy.deepcopy(c['source_id_variants'][0]));self.assertIn('DUPLICATE_SOURCE_GROUP:alpha',R.build_alias_docket(c,b,i)['errors'])
    def test_wrong_variant_id(self):
        c,b,i=fixture();c['source_id_variants'][0]['variants'][0]['id']='beta';self.assertIn('INVALID_VARIANT_PROVENANCE:alpha',R.build_alias_docket(c,b,i)['errors'])
    def test_malformed_source_blob(self):
        c,b,i=fixture();c['source_id_variants'][0]['variants'][0]['source_blob']='bad';self.assertIn('INVALID_VARIANT_PROVENANCE:alpha',R.build_alias_docket(c,b,i)['errors'])
    def test_missing_variant_branch(self):
        c,b,i=fixture();c['source_id_variants'][0]['variants'][0].pop('branch');self.assertIn('INVALID_VARIANT_BRANCH:alpha',R.build_alias_docket(c,b,i)['errors'])
    def test_missing_base_inventory(self):
        c,b,i=fixture();b.pop('sources');self.assertEqual(R.build_alias_docket(c,b,i)['status'],'INVALID_HARD_HOLD')
    def test_missing_fragment_inventory(self):
        c,b,i=fixture();c.pop('source_id_variants');self.assertEqual(R.build_alias_docket(c,b,i)['status'],'INVALID_HARD_HOLD')
    def test_unknown_original_claim(self):
        c,b,i=fixture();i['claims'].append(None);self.assertIn('INVALID_ORIGINAL_CLAIM',R.build_alias_docket(c,b,i)['errors'])
    def test_original_provenance_fields_preserved(self):
        x=R.build_alias_docket(*fixture()); self.assertTrue(all('source_blob' in v and 'raw_sha256' in v for a in x['alias_review'] for v in a['origin_records']))
    def test_native_no_git_is_exit_two(self):
        p=subprocess.run(['python','-I',str(HERE/'tools/r388_source_url_alias_custody.py'),'--repo','/definitely/no/git'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('INVALID_HARD_HOLD',p.stdout)

# Every pair is a separately reported test, not a loop hidden behind one PASS.
BAD_URLS=[
  'http://cdc.gov/a','ftp://cdc.gov/a','javascript:alert(1)','data:text/plain,hello',
  '//cdc.gov/a','https://user:pw@cdc.gov/a','https://user@cdc.gov/a',
  'https://cdc.gov/a#part','https://cdc.gov/a\n','https://cdc.gov/a\t',
  'https://cdc.gov/a ',' https://cdc.gov/a','https://cdc.gov/%zz',
  'https://cdc.gov/%','https://cdc.gov/%f','https://127.0.0.1/a',
  'https://10.0.0.3/a','https://192.168.0.1/a','https://172.16.2.1/a',
  'https://localhost/a','https://dev.local/a','https://example.internal/a',
  'https://example.invalid/a','https://example.test/a','https://cdc.gov:8443/a',
  'https://cdc.gov/a%2fb','https://cdc.gov/a%5Cb', 'https://cdc.gov/a/../b',
  'https://cdc.gov/a/./b','https://cdc.gov/a\\b','https://cdc.gov/a\0b',
  'https://cdc.gov:bad/a','https://cdc.gov:99999/a',
  'https://[::1]/a','https://[fc00::1]/a',
  'https://cdc.gov/a\r','https://cdc.gov/a\x7f',
]
for n,url in enumerate(BAD_URLS):
    def _case(self, u=url):
        with self.assertRaises(ValueError): R.url_identity(u)
    setattr(KnownTests,f'test_reject_url_{n:02d}',_case)

EQ_PAIRS=[
 ('https://CDC.GOV/a','https://cdc.gov/a'),
 ('https://cdc.gov/a/','https://cdc.gov/a'),
 ('https://cdc.gov:443/a','https://cdc.gov/a'),
 ('https://cdc.gov/%7Eperson','https://cdc.gov/~person'),
 ('https://cdc.gov/a?utm_source=evil','https://cdc.gov/a'),
 ('https://cdc.gov/a?utm_campaign=x&fbclid=123','https://cdc.gov/a'),
 ('https://cdc.gov/a?gclid=123','https://cdc.gov/a'),
 ('https://cdc.gov/a?mc_eid=123','https://cdc.gov/a'),
 ('https://cdc.gov/a?x=1&utm_medium=y','https://cdc.gov/a?x=1'),
]
for n,(a,b) in enumerate(EQ_PAIRS):
    def _case(self, left=a,right=b):self.assertEqual(R.url_identity(left)['key'],R.url_identity(right)['key'])
    setattr(KnownTests,f'test_probable_equivalence_{n:02d}',_case)

DIFFERENT=[
 ('https://www.cdc.gov/a','https://cdc.gov/a'),
 ('https://cdc.gov/a?x=1&y=2','https://cdc.gov/a?y=2&x=1'),
 ('https://cdc.gov/a?x=1','https://cdc.gov/a?x=2'),
 ('https://cdc.gov/a','https://cdc.gov/b'),
 ('https://cdc.gov/a?key=','https://cdc.gov/a'),
 ('https://cdc.gov/a?gclid=1&safe=2','https://cdc.gov/a?safe=3'),
]
for n,(a,b) in enumerate(DIFFERENT):
    def _case(self,left=a,right=b):self.assertNotEqual(R.url_identity(left)['key'],R.url_identity(right)['key'])
    setattr(KnownTests,f'test_do_not_equate_{n:02d}',_case)

if __name__=='__main__':unittest.main()
