"""R123 read-only 35-article/30-source-group synthetic and mutation regression tests.

No network, shared-tree modification, WordPress, checkout or approval side effects.
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

TOOL = Path(__file__).with_name('r123_claim_source_coverage_gate.py')
SPEC = importlib.util.spec_from_file_location('r123_source_gate', TOOL)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
SLUGS = [f'test-guide-{i:02d}' for i in range(35)]
N = 30

def fixture():
    objects = {}
    def add(value):
        raw = value.encode() if isinstance(value,str) else json.dumps(value,sort_keys=True).encode()
        sha = GATE.blob_sha(raw)
        objects[sha] = raw
        return sha
    base_sources = [{'id':'source-one','url':'https://example.org/primary',
                     'verified_on':'2026-10-29','supports':'Primary source'}]
    food_sources = []
    groups = []
    for i in range(N):
        key=f'shared-{i:02d}'
        url=f'https://example.org/shared/{i:02d}'
        orig={'id':key,'url':url,'verified_on':None,'supports':None}
        revised={'id':key,'url':url,'verified_on':'2026-10-29',
                 'supports':f'Claim verification {i}'}
        base_sources.append(orig)
        food_sources.append(revised)
        groups.append({'url':url,'review_status':'pending-human-source-and-reading-scope-review',
                       'variants':[{'origin':'base','source':orig},
                                   {'origin':'food','source':revised}]})
    register_sha=add({'sources':base_sources})
    files={}
    for slug in SLUGS:
        files[slug+'.body.html']=add('<article><p>Useful {{cite:source-one}} and '+
             '{{cite:shared-00}} evidence.</p></article>')
        files[slug+'.meta.json']=add({'slug':slug,'status':{'publish':'draft'},
             'safety_review':{'state':'pending'},
             'source_use':{'source-one':'Recorded baseline use',
                           'shared-00':'Recorded specific reading scope'}})
    frags={}
    for fn in GATE.EXPECTED_FRAGMENTS:
        frags[fn] = add({'sources':food_sources if fn=='food.json' else []})
    frags['README.md']=add('SOURCE DATA README')
    snapshot={'schema':GATE.SCHEMA,'issue':136,'business_issue':820,
              'governance':{'release_state':'HOLD','may_merge':False,'may_publish':False,
                            'independent_QD_PASS':False,'medical_safety_verified':False,
                            'merchant_offer_verified':False},
              'snapshots':[{'role':'baseline','sha':'a'*40,'article_files':copy.deepcopy(files),
                            'source_fragments':copy.deepcopy(frags)},
                           {'role':'candidate','sha':'b'*40,'article_files':copy.deepcopy(files),
                            'source_fragments':copy.deepcopy(frags)}]
             + [{'role':'contributor','cluster':name,'sha':format(i+1,'040x')}
                for i,name in enumerate(('food','health','historical-field','historical-food',
                                          'historical-home','shelter','start-here'))]}
    crosswalk={'status':'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
               'duplicate_url_groups':N,'groups':groups}
    return snapshot,register_sha,crosswalk,objects

def audit(f):
    snap,oid,crosswalk,blobs=f
    return GATE.audit(snap,oid,crosswalk,lambda key: blobs[key])

def revise_file(f, version, file, fn):
    snap,_,_,objs=f
    ref=snap['snapshots'][0 if version=='original' else 1]
    sha=ref['article_files'][file]
    content=objs[sha].decode()
    new=fn(content)
    raw=new.encode()
    oid=GATE.blob_sha(raw)
    objs[oid]=raw
    ref['article_files'][file]=oid

def revise_fragment(f, version, file, fn):
    snap,_,_,objs=f
    ref=snap['snapshots'][0 if version=='original' else 1]
    sha=ref['source_fragments'][file]
    j=json.loads(objs[sha].decode())
    fn(j)
    raw=json.dumps(j,sort_keys=True).encode()
    oid=GATE.blob_sha(raw)
    objs[oid]=raw
    ref['source_fragments'][file]=oid

class FullSyntheticCensus(unittest.TestCase):
    def test_clean_returns_hold_never_approval(self):
        r=audit(fixture())
        self.assertEqual(r['state'],'HOLD')
        self.assertEqual(r['article_count'],35)
        self.assertEqual(r['contributor_count'],7)
        self.assertEqual(r['candidate_shared_url_groups'],30)
        self.assertEqual(r['declared_shared_url_groups'],30)
        self.assertEqual(r['candidate_source_rows'],61)
        self.assertEqual(r['citation_counts'],{'original':70,'candidate':70})
        self.assertFalse(r['QD_PASS'])
        self.assertFalse(r['may_publish'])
        self.assertFalse(r['medical_safety_verified'])
        self.assertFalse(r['merchant_offer_verified'])
        self.assertEqual(r['blockers'],[])
        self.assertTrue(any(x['code']=='SHARED_URL_SOURCE_SCOPE_REVIEW' for x in r['human_review_worklist']))
    def test_deterministic_no_mutation(self):
        f=fixture(); before=copy.deepcopy(f)
        self.assertEqual(audit(f),audit(f))
        self.assertEqual(f,before)
    def test_unchanged_source_scope_no_added_exposure(self):
        f=fixture()
        self.assertFalse(any(x['code']=='CITATION_EXPOSURE_CHANGED' for x in audit(f)['human_review_worklist']))
    def test_changed_source_use_is_human_review_not_approval(self):
        f=fixture()
        revise_file(f,'candidate',SLUGS[0]+'.meta.json',
                    lambda s:s.replace('Recorded baseline use','Different interpretation'))
        items=audit(f)['human_review_worklist']
        self.assertTrue(any(x['code']=='AUTHOR_READING_SCOPE_CHANGED' for x in items))
    def test_source_addition_exposure(self):
        f=fixture()
        revise_file(f,'candidate',SLUGS[0]+'.body.html',
                    lambda s:s.replace('</p>',' Extra {{cite:shared-01}}</p>'))
        revise_file(f,'candidate',SLUGS[0]+'.meta.json',
                    lambda s:s.replace('"source-one":', '"shared-01": "Specific additional use", "source-one":'))
        self.assertTrue(any(x['code']=='CITATION_EXPOSURE_CHANGED' for x in audit(f)['human_review_worklist']))
    def test_crosswalk_old_shared_url_gone(self):
        f=fixture()
        revise_fragment(f,'candidate','food.json',lambda j: j['sources'][0].update(url='https://other.org/resource'))
        codes={x['code'] for x in audit(f)['human_review_worklist']}
        self.assertTrue('SOURCE_ID_URL_DIVERGENCE' in codes)
        self.assertTrue('CROSSWALK_URL_NO_LONGER_SHARED' in codes)
    def test_crosswalk_unlisted_collision(self):
        f=fixture()
        def change(j):
            j['sources'].append({'id':'source-one','url':'https://example.org/primary',
                                 'verified_on':'2026-10-29','supports':'New interpretation'})
        revise_fragment(f,'candidate','health.json',change)
        self.assertIn('UNRECORDED_SHARED_SOURCE_URL',
                      {x['code'] for x in audit(f)['blockers']})
    def test_crosswalk_different_id_same_url(self):
        f=fixture()
        revise_fragment(f,'candidate','food.json',lambda j:j['sources'][0].update(id='other-identity'))
        self.assertIn('CROSSWALK_VARIANT_ROSTER_DRIFT',
                      {x['code'] for x in audit(f)['blockers']})
    def test_base_source_identity_digest(self):
        f=fixture(); f[3][f[1]]=b'forged'
        with self.assertRaisesRegex(GATE.Hold,'GIT_BLOB_IDENTITY_MISMATCH'):
            audit(f)
    def test_unchanged_sources_require_human_review(self):
        f=fixture()
        r=audit(f)
        self.assertEqual(sum(x['code']=='SHARED_URL_SOURCE_SCOPE_REVIEW' for x in r['human_review_worklist']),60)
    def test_source_with_all_variants_unverified(self):
        f=fixture()
        revise_fragment(f,'candidate','food.json',
                        lambda j:j['sources'][0].update(verified_on=None))
        self.assertTrue(any(x['code']=='CITED_SOURCE_HAS_NO_VERIFIED_VARIANT' for x in audit(f)['blockers']))
    def test_metadata_safety_state_tamper(self):
        f=fixture()
        revise_file(f,'candidate',SLUGS[0]+'.meta.json',
                    lambda s:s.replace('"pending"','"approved"'))
        self.assertIn('SAFETY_STATE_DRIFT',{x['code'] for x in audit(f)['blockers']})
    def test_no_shared_source_web_or_network_calls(self):
        f=fixture(); n=len(f[3]);audit(f)
        self.assertEqual(len(f[3]),n)

class AdversarialInputs(unittest.TestCase):
    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(GATE.Hold,'DUPLICATE_JSON_KEY'):
            GATE.strict_json('{"a":1,"a":2}')
    def test_non_utf8_blob(self):
        f=fixture(); k=f[0]['snapshots'][0]['article_files'][SLUGS[0]+'.body.html']
        f[3][k]=b'\xff'
        with self.assertRaises(GATE.Hold):audit(f)
    def test_missing_article_pair(self):
        f=fixture();f[0]['snapshots'][1]['article_files'].pop(SLUGS[0]+'.meta.json')
        with self.assertRaisesRegex(GATE.Hold,'ARTICLE_FILE_ROSTER_DRIFT'):audit(f)
    def test_extra_article_pair(self):
        f=fixture();f[0]['snapshots'][1]['article_files']['other.body.html']='f'*40
        with self.assertRaisesRegex(GATE.Hold,'ARTICLE_FILE_ROSTER_DRIFT'):audit(f)
    def test_removed_contributor(self):
        f=fixture();f[0]['snapshots'].pop()
        with self.assertRaisesRegex(GATE.Hold,'NINE_HEADS_REQUIRED'):audit(f)
    def test_wrong_contributor(self):
        f=fixture();f[0]['snapshots'][4]['cluster']='injected'
        with self.assertRaisesRegex(GATE.Hold,'CLUSTERS_CHANGED'):audit(f)
    def test_wrong_issue(self):
        f=fixture();f[0]['business_issue']=900
        with self.assertRaisesRegex(GATE.Hold,'ISSUE_SCOPE_MISMATCH'):audit(f)
    def test_bad_source_fragment_roster(self):
        f=fixture();f[0]['snapshots'][1]['source_fragments'].pop('start.json')
        with self.assertRaisesRegex(GATE.Hold,'FRAGMENT_ROSTER_CHANGED'):audit(f)
    def test_invalid_source_id(self):
        f=fixture();revise_fragment(f,'candidate','food.json',
                        lambda j:j['sources'][0].update(id='BAD-ID'))
        with self.assertRaisesRegex(GATE.Hold,'BAD_SOURCE_ID'):audit(f)
    def test_malformed_citation_token(self):
        f=fixture();revise_file(f,'candidate',SLUGS[0]+'.body.html',
                                lambda s:s+'{{cite:BAD SOURCE}}')
        with self.assertRaisesRegex(GATE.Hold,'MALFORMED_CITATION'):audit(f)
    def test_source_scope_missing_field(self):
        f=fixture();revise_file(f,'candidate',SLUGS[0]+'.meta.json',
                                lambda s:s.replace('Recorded specific reading scope',''))
        self.assertIn('CITED_SOURCE_MISSING_ARTICLE_USE',
                      {x['code'] for x in audit(f)['blockers']})
    def test_unregistered_citation(self):
        f=fixture();revise_file(f,'candidate',SLUGS[0]+'.body.html',
                                lambda s:s+'{{cite:ghost-unknown}}')
        self.assertIn('CITED_SOURCE_NOT_REGISTERED',
                      {x['code'] for x in audit(f)['blockers']})
    def test_crosswalk_status_approval_rejected(self):
        f=fixture();f[2]['groups'][0]['review_status']='approved'
        with self.assertRaisesRegex(GATE.Hold,'ILLEGAL_CROSSWALK_APPROVAL'):audit(f)
    def test_duplicate_crosswalk_url_rejected(self):
        f=fixture();f[2]['groups'][1]['url']=f[2]['groups'][0]['url']
        with self.assertRaisesRegex(GATE.Hold,'DUPLICATE_CROSSWALK_GROUP'):audit(f)
    def test_crosswalk_count_corrupted(self):
        f=fixture();f[2]['duplicate_url_groups']=31
        with self.assertRaisesRegex(GATE.Hold,'CROSSWALK_GROUP_COUNT_CORRUPT'):audit(f)
    def test_missing_human_review_marker(self):
        f=fixture();f[2]['status']='PASSED'
        with self.assertRaisesRegex(GATE.Hold,'CROSSWALK_NOT_HOLD'):audit(f)
    def test_source_fragment_not_json(self):
        f=fixture();revise_fragment(f,'candidate','food.json',lambda j:j.update(sources='bad'))
        with self.assertRaisesRegex(GATE.Hold,'BAD_SOURCE_FRAGMENT'):audit(f)
    def test_source_url_http_rejected(self):
        f=fixture();revise_fragment(f,'candidate','food.json',
                        lambda j:j['sources'][0].update(url='http://example.org/bad'))
        with self.assertRaisesRegex(GATE.Hold,'HTTPS_HOST_REQUIRED'):audit(f)
    def test_bad_metadata_slug(self):
        f=fixture();revise_file(f,'candidate',SLUGS[0]+'.meta.json',
                                lambda s:s.replace(SLUGS[0],'another-slug'))
        with self.assertRaisesRegex(GATE.Hold,'ARTICLE_SLUG_CHANGED'):audit(f)
    def test_published_state_fails(self):
        f=fixture();revise_file(f,'candidate',SLUGS[0]+'.meta.json',
                                lambda s:s.replace('"draft"','"published"'))
        with self.assertRaisesRegex(GATE.Hold,'ARTICLE_PUBLICATION_UPGRADE'):audit(f)
    def test_approval_flag_fails(self):
        for flag in ('may_publish','may_merge','independent_QD_PASS',
                     'medical_safety_verified','merchant_offer_verified'):
            with self.subTest(flag=flag):
                f=fixture();f[0]['governance'][flag]=True
                with self.assertRaisesRegex(GATE.Hold,'UNAUTHORIZED_APPROVAL'):audit(f)

class URLGuard(unittest.TestCase):
    def test_default_https_port(self):
        self.assertEqual(GATE.canonical_url('https://EXAMPLE.ORG:443/x'),
                         'https://example.org/x')
    def test_nondefault_port_preserved(self):
        self.assertEqual(GATE.canonical_url('https://example.org:8443/x'),
                         'https://example.org:8443/x')
    def test_fragments_preserved(self):
        self.assertNotEqual(GATE.canonical_url('https://example.org/pdf#page=4'),
                            GATE.canonical_url('https://example.org/pdf#page=5'))
    def test_queries_preserved(self):
        self.assertNotEqual(GATE.canonical_url('https://example.org/?a=1&b=2'),
                            GATE.canonical_url('https://example.org/?b=2&a=1'))
    def test_path_case_preserved(self):
        self.assertNotEqual(GATE.canonical_url('https://example.org/A'),
                            GATE.canonical_url('https://example.org/a'))
    def test_url_username_denied(self):
        with self.assertRaisesRegex(GATE.Hold,'HTTPS_HOST_REQUIRED'):
            GATE.canonical_url('https://user:pw@example.org/')
    def test_scheme_other_than_https_denied(self):
        for url in ('http://a.org/x','ftp://a.org','javascript:alert(1)',
                    'file:///etc/passwd','data:text/plain,hello','//a.org/path'):
            with self.subTest(url=url):
                with self.assertRaises(GATE.Hold):GATE.canonical_url(url)
    def test_bad_port(self):
        with self.assertRaises(GATE.Hold):GATE.canonical_url('https://example.org:99999/a')
    def test_newline_and_backslash(self):
        for url in ('https://example.org/a\nb','https://example.org/a\\b'):
            with self.subTest(url=url):
                with self.assertRaises(GATE.Hold):GATE.canonical_url(url)

# Each article's citation/source-use relationship must fail closed independently.
# These generate 35 different realistic deletions instead of incrementing a dummy counter.
def make_missing_source_test(slug):
    def case(self):
        f=fixture()
        revise_file(f,'candidate',slug+'.meta.json',
                    lambda s:s.replace('"shared-00": "Recorded specific reading scope"',
                                       '"shared-00": ""'))
        self.assertTrue(any(b['code']=='CITED_SOURCE_MISSING_ARTICLE_USE' and
                            b['article']==slug for b in audit(f)['blockers']))
    return case
for slug in SLUGS:
    setattr(FullSyntheticCensus,'test_missing_source_use_'+slug,make_missing_source_test(slug))

if __name__ == '__main__':
    unittest.main()
