"""R321 source-pinned delta: adversarial, synthetic-only tests; never touch real source."""
from __future__ import annotations
import copy
import json
import unittest
from preparedness.tests.test_r320_conflict_adjudication_docket_hold import dossier_fixture
from preparedness.tools import r321_conflict_content_delta_hold as gate

BASE_HTML=b'<h2>Call plan</h2><p>Check official sources [source_a]</p><a href="/preparedness/">Guide</a><input name="contact" id="entry">'
MORE_HTML=b'<h2>Call plan</h2><p>Check official sources [source_b] and a local bulletin</p><a href="/preparedness/start-here/">Guide</a><input name="contact2" id="entry">'
BASE_META={'number':102,'slug':'reunification-plan','status':'draft','source_uses':['source_a'],'safety_review':'pending'}
MORE_META={'number':104,'slug':'reunification-plan','status':'draft','source_uses':['source_b'],'safety_review':'pending'}


def synthetic():
    m,_=dossier_fixture()
    blobs={}
    for r in m['records']:
        meta=r['path'].endswith('.json')
        before=json.dumps(BASE_META,sort_keys=True).encode() if meta else BASE_HTML
        after=json.dumps(MORE_META,sort_keys=True).encode() if meta else MORE_HTML
        def register(raw):
            sha=gate.git_blob_sha(raw);blobs[sha]=raw
            return {'sha':sha,'size':len(raw)}
        r['integrated']=register(before)
        if r['disposition']=='INTEGRATED_ONLY':r['continuation']=None;r['followup']=None
        elif r['disposition']=='IDENTICAL':r['continuation']=r['integrated'].copy();r['followup']=r['integrated'].copy()
        else:r['continuation']=register(after);r['followup']=register(after)
    d=gate.review.build_docket(m)
    assert gate.review.validate_docket(m,d)['errors']==[]
    return m,d,blobs

class R321DiffTests(unittest.TestCase):
    def setUp(self):self.m,self.d,self.blobs=synthetic()
    def report(self):return gate.build_report(self.m,self.d,self.blobs.__getitem__)
    def test_authentic_structural_fixture(self):self.assertEqual(gate.review.validate_docket(self.m,self.d)['errors'],[])
    def test_complete_authentic_blob_inputs(self):self.assertEqual(self.report()['errors'],[])
    def test_hold_even_when_valid(self):self.assertEqual(self.report()['state'],'DRAFT_HARD_HOLD')
    def test_no_false_qd(self):self.assertIs(self.report()['release']['independent_qd_pass'],False)
    def test_no_automatic_merges(self):self.assertIs(self.report()['release']['automatic_merge_permitted'],False)
    def test_no_false_publishing(self):self.assertIs(self.report()['release']['publication_authorized'],False)
    def test_no_false_sales(self):self.assertIs(self.report()['release']['paid_conversion_verified'],False)
    def test_exact_review_count(self):self.assertEqual(self.report()['review_count'],15)
    def test_deterministic(self):self.assertEqual(self.report(),gate.build_report(copy.deepcopy(self.m),copy.deepcopy(self.d),self.blobs.__getitem__))
    def test_sorted_path_output(self):self.assertEqual([x['path'] for x in self.report()['records']],sorted(x['path'] for x in self.d['records']))
    def test_metadata_approval_sensitive(self):
        r=next(x for x in self.report()['records'] if x['path'].endswith('meta.json'))
        self.assertIn('$.number',r['comparisons']['followup']['safety_sensitive_paths'])
    def test_body_citation_delta(self):
        r=next(x for x in self.report()['records'] if x['path'].endswith('body.html'))
        self.assertIn('source_a',r['comparisons']['followup']['citations_removed'])
        self.assertIn('source_b',r['comparisons']['followup']['citations_added'])
    def test_body_link_delta(self):
        r=next(x for x in self.report()['records'] if x['path'].endswith('body.html'))
        self.assertTrue(r['comparisons']['followup']['links_removed'])
    def test_body_field_delta(self):
        r=next(x for x in self.report()['records'] if x['path'].endswith('body.html'))
        self.assertEqual(r['comparisons']['followup']['form_fields_removed'],1)
    def test_source_ref_retained(self):self.assertEqual(self.report()['records'][0]['source_refs'],self.d['records'][0]['source_refs'])
    def test_blob_sha_deterministic(self):self.assertEqual(gate.git_blob_sha(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_corrupted_docket(self):self.d['release']['publication_authorized']=True;self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_removed_docket(self):self.d['records'].pop();self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_invalid_manifest(self):self.m['baseline']['sha']='0'*40;self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_no_source_load_on_invalid_docket(self):
        self.d['release']['publication_authorized']=True
        def forbidden(_):raise RuntimeError('unexpected fetch')
        self.assertEqual(gate.build_report(self.m,self.d,forbidden)['state'],'INVALID_HARD_HOLD')
    def test_hard_hold_missing_blob(self):
        self.blobs.clear();self.assertTrue(any('MISSING_OR_INVALID_GIT_OBJECT' in s for s in self.report()['errors']))
    def test_strict_json_dup_key_rejected(self):
        with self.assertRaises(ValueError):gate.strict_json(b'{"safety_review":"pending","safety_review":"approved"}')
    def test_strict_json_object(self):self.assertEqual(gate.strict_json(b'{"x":1}'),{'x':1})
    def test_strict_json_list_valid_but_meta_rejected(self):
        with self.assertRaises(ValueError):gate.delta(b'[]',b'{}','x.meta.json')
    def test_invalid_suffix_rejected(self):
        with self.assertRaises(ValueError):gate.delta(b'x',b'y','x.txt')
    def test_sha1_type(self):self.assertEqual(len(gate.git_blob_sha(b'hello')),40)
    def test_duplicate_heading_tracked(self):
        r=gate.delta(b'<h2>Keep warning</h2><h2>Keep warning</h2>',b'<h2>Keep warning</h2>','x.body.html')
        self.assertEqual(r['headings_removed'],[('h2','Keep warning')])
    def test_ignore_script_text(self):self.assertNotIn('danger',gate.html_features(b'<script>danger</script><p>safe</p>')['text'])
    def test_hold_error_shape(self):self.assertEqual(gate.build_report(None,None,lambda _:b'')['state'],'INVALID_HARD_HOLD')
    def test_reviewer_never_approved(self):self.assertTrue(all(row['qualified_approval'] is False for row in self.report()['records']))
    def test_output_privacy_no_raw_body(self):self.assertNotIn('local bulletin',json.dumps(self.report()))
    def test_source_ref_schema_invalid(self):
        with self.assertRaises(ValueError):gate.read_verified_blob({'sha':'x','size':1},lambda _:b'!')
    def test_size_bool_rejected(self):
        with self.assertRaises(ValueError):gate.read_verified_blob({'sha':'a'*40,'size':True},lambda _:b'')
    def test_corrupted_utf8_rejected(self):
        raw=b'\xff';ref={'sha':gate.git_blob_sha(raw),'size':1}
        with self.assertRaises(UnicodeDecodeError):gate.read_verified_blob(ref,lambda _:raw)
    def test_non_bytes_rejected(self):
        ref={'sha':gate.git_blob_sha(b'a'),'size':1}
        with self.assertRaises(ValueError):gate.read_verified_blob(ref,lambda _: 'a')


def mutation_case(index, mode):
    def test(self):
        row=self.d['records'][index]
        sha=row['source_refs']['integrated']['sha']
        if mode=='lost':self.blobs.pop(sha,None)
        elif mode=='changed':self.blobs[sha]=b'A completely different body!'
        elif mode=='size':row['source_refs']['integrated']['size']+=1
        elif mode=='hash':row['source_refs']['integrated']['sha']='1'*40
        r=self.report()
        self.assertEqual(r['state'],'INVALID_HARD_HOLD')
        self.assertTrue(r['errors'])
    return test

for i in range(15):
    for mode in ('lost','changed','size','hash'):
        setattr(R321DiffTests,f'test_conflict_{i:02}_{mode}',mutation_case(i,mode))

if __name__=='__main__':unittest.main()
